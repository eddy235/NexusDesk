from django.test import SimpleTestCase, override_settings


class DemoSecurityTests(SimpleTestCase):
    @override_settings(DEMO_MODE=True, DEBUG=False, SECURE_SSL_REDIRECT=False)
    def test_demo_is_read_only(self):
        response = self.client.get('/demo/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SYNTHETIC DATA ONLY')
        self.assertContains(response, 'VPN connection intermittent')
        self.assertEqual(self.client.post('/tickets/new/', {}).status_code, 404)
        self.assertEqual(self.client.get('/admin/').status_code, 404)
        self.assertEqual(self.client.get('/login/').status_code, 404)
        self.assertEqual(self.client.get('/tickets/').status_code, 404)
        self.assertEqual(self.client.get('/assets/').status_code, 404)
        self.assertEqual(self.client.post('/demo/', {}).status_code, 404)

    @override_settings(DEMO_MODE=False, DEBUG=True)
    def test_local_mode_remains_private(self):
        self.assertEqual(self.client.get('/demo/').status_code, 404)
        self.assertEqual(self.client.get('/tickets/').status_code, 302)

    @override_settings(DEMO_MODE=True, DEBUG=False, SECURE_SSL_REDIRECT=False)
    def test_health_contains_no_sensitive_data(self):
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'status': 'ok', 'demo_mode': True})
