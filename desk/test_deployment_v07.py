"""Unit checks for the external-deployment verification helper; no network used."""
from unittest.mock import patch

from django.test import SimpleTestCase

from scripts.verify_demo_http import verify


class DeploymentVerifierTests(SimpleTestCase):
    def test_known_safe_demo_passes(self):
        paths = []
        def fake_probe(base, path, method='GET'):
            paths.append((path, method))
            if method != 'GET':
                return 404, {}, b'Not available in read-only demo mode.'
            if path == '/health/':
                return 200, {}, b'{"status":"ok","demo_mode":true}'
            if path == '/demo/':
                return 200, {
                    'Content-Security-Policy': "default-src 'none'; script-src 'none'; frame-ancestors 'none'",
                    'X-Content-Type-Options': 'nosniff',
                }, (b'NexusDesk SYNTHETIC DATA ONLY Filter examples Asset lifecycle')
            if path == '/static/desk/style.css':
                return 200, {}, b'body {}'
            return 404, {}, b'Not available in read-only demo mode.'
        with patch('scripts.verify_demo_http.probe', side_effect=fake_probe):
            verify('https://example.onrender.com')
        self.assertIn(('/tickets/new/', 'POST'), paths)
        self.assertIn(('/admin/', 'GET'), paths)

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
