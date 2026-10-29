"""Unit checks for the external-deployment verification helper; no network used."""
from unittest.mock import patch

from django.test import SimpleTestCase

from scripts.verify_demo_http import verify, header_value


class DeploymentVerifierTests(SimpleTestCase):
    def test_known_safe_demo_passes(self):
        paths = []
        def fake_probe(base, path, method='GET'):
            paths.append((path, method))
            if method != 'GET':
                return 404, {}, b'Not available in read-only demo mode.'
            if path == '/health/':
                return 200, {}, b'{"status":"ok","demo_mode":true}'
            if path == '/demo/?status=Open&priority=High':
                return 200, {}, b'Email client authentication failure'
            if path == '/demo/?asset_state=Maintenance':
                return 200, {}, b'Wireless access point'
            if path == '/demo/':
                return 200, {
                    'content-security-policy': "default-src 'none'; script-src 'none'; frame-ancestors 'none'",
                    'x-content-type-options': 'nosniff',
                }, (b'NexusDesk SYNTHETIC DATA ONLY Filter examples Asset lifecycle v1.0')
            if path == '/static/desk/style.css':
                return 200, {}, b'body {}'
            return 404, {}, b'Not available in read-only demo mode.'
        with patch('scripts.verify_demo_http.probe', side_effect=fake_probe):
            verify('https://example.onrender.com')
        self.assertIn(('/tickets/new/', 'POST'), paths)
        self.assertIn(('/admin/', 'GET'), paths)
        self.assertIn(('/demo/?status=Open&priority=High', 'GET'), paths)
        self.assertIn(('/demo/?asset_state=Maintenance', 'GET'), paths)

    def test_header_names_are_case_insensitive(self):
        self.assertEqual(header_value({'CONTENT-SECURITY-POLICY': 'safe'}, 'content-security-policy'), 'safe')
        self.assertEqual(header_value({'x-content-type-options': 'nosniff'}, 'X-Content-Type-Options'), 'nosniff')

    def test_non_demo_service_is_rejected(self):
        with patch('scripts.verify_demo_http.probe',
                   return_value=(200, {}, b'{"demo_mode":false}')):
            with self.assertRaisesRegex(AssertionError, 'not in demo mode'):
                verify('https://example.onrender.com')

    def test_public_http_origin_is_rejected(self):
        with self.assertRaises(ValueError):
            verify('http://example.onrender.com')

    def test_origin_with_path_is_rejected(self):
        with self.assertRaises(ValueError):
            verify('https://example.onrender.com/demo/')
