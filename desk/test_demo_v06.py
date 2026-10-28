"""Regression checks for the interactive, synthetic-only v0.6 showcase."""
from django.test import SimpleTestCase, override_settings


@override_settings(DEMO_MODE=True, DEBUG=False, SECURE_SSL_REDIRECT=False)
class InteractiveDemoTests(SimpleTestCase):
    def test_synthetic_stats_match_unfiltered_records(self):
        response = self.client.get('/demo/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ticket_count'], 12)
        self.assertEqual(response.context['asset_count'], 7)
        self.assertEqual(response.context['stats']['open'], 5)
        self.assertEqual(response.context['stats']['in_progress'], 5)
        self.assertEqual(response.context['stats']['overdue'], 2)
        self.assertContains(response, 'Every displayed ticket, asset, figure and team is fictional')

    def test_ticket_filters_are_combined(self):
        response = self.client.get('/demo/', {
            'q': 'laptop', 'status': 'In progress', 'priority': 'High'
        })
        self.assertEqual(response.context['ticket_count'], 1)
        self.assertContains(response, 'Laptop VPN connection intermittent')
        self.assertNotContains(response, 'Printer queue stuck')
        self.assertEqual(response.context['stats']['open'], 5)

    def test_asset_state_filter(self):
        response = self.client.get('/demo/', {'asset_state': 'Maintenance'})
        self.assertEqual(response.context['asset_count'], 1)
        self.assertContains(response, 'Wireless access point')
        self.assertNotContains(response, 'External display')

    def test_bad_filter_values_default_to_unfiltered(self):
        response = self.client.get('/demo/', {
            'status': 'Hidden', 'priority': 'Top secret', 'asset_state': 'Lost'
        })
        self.assertEqual(response.context['ticket_count'], 12)
        self.assertEqual(response.context['asset_count'], 7)

    def test_search_is_bounded_and_html_escaped(self):
        response = self.client.get('/demo/', {'q': '<script>alert(1)</script>'})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, '<script>alert(1)</script>', html=False)
        self.assertContains(response, '&lt;script&gt;', html=False)
        response = self.client.get('/demo/', {'q': 'x' * 1000})
        self.assertEqual(len(response.context['query']), 80)

    def test_public_demo_has_restrictive_content_policy(self):
        response = self.client.get('/demo/')
        self.assertIn("script-src 'none'", response['Content-Security-Policy'])
        self.assertIn("frame-ancestors 'none'", response['Content-Security-Policy'])
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')

    def test_private_routes_and_write_methods_blocked(self):
        for route in ['/admin/', '/login/', '/logout/', '/tickets/',
                      '/tickets/new/', '/assets/', '/assets/new/']:
            self.assertEqual(self.client.get(route).status_code, 404)
            self.assertEqual(self.client.post(route, {}).status_code, 404)
        self.assertEqual(self.client.post('/demo/', {'q': 'hello'}).status_code, 404)
        self.assertEqual(self.client.post('/health/', {}).status_code, 404)

    def test_root_redirects_to_demo(self):
        self.assertEqual(self.client.get('/').url, '/demo/')
