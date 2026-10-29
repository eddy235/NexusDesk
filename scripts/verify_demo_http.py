"""Non-destructive HTTP checks for a deployed NexusDesk *synthetic* demo.

Usage: python scripts/verify_demo_http.py https://YOUR-SERVICE.onrender.com
Only ordinary GET/HEAD and intentionally rejected POST requests are sent.
"""
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def probe(base, path, method="GET"):
    request = Request(base + path, method=method,
                      headers={"User-Agent": "NexusDesk-Release-Smoke/1.0"})
    try:
        with urlopen(request, timeout=12) as response:
            return response.status, dict(response.headers), response.read(120000)
    except HTTPError as exc:
        return exc.code, dict(exc.headers), exc.read(120000)


def header_value(headers, name):
    """HTTP field names are case-insensitive; normal dict keys may not be."""
    return next((str(value) for key, value in headers.items()
                 if str(key).lower() == name.lower()), '')


def verify(base):
    base = base.rstrip("/")
    target = urlsplit(base)
    local = target.hostname in ("127.0.0.1", "::1", "localhost")
    if target.scheme != "https" and not (target.scheme == "http" and local):
        raise ValueError("Use HTTPS for deployed sites; HTTP is allowed only on loopback")
    if not target.netloc or target.path or target.query or target.fragment:
        raise ValueError("Supply the base origin only, without path or query")

    status, headers, raw = probe(base, "/health/")
    assert status == 200, f"Health check returned {status}"
    assert json.loads(raw)["demo_mode"] is True, "Server is not in demo mode"

    status, headers, raw = probe(base, "/demo/")
    assert status == 200, f"Demo returned {status}"
    html = raw.decode("utf-8")
    for expected in ("SYNTHETIC DATA ONLY", "NexusDesk",
                     "Filter examples", "Asset lifecycle", "v1.0"):
        assert expected in html, f"Demo missing expected element: {expected}"
    csp = header_value(headers, "Content-Security-Policy")
    assert "script-src 'none'" in csp, "Expected restrictive script policy"
    assert "frame-ancestors 'none'" in csp, "Expected anti-framing policy"
    assert header_value(headers, "X-Content-Type-Options").lower() == "nosniff"

    status, _, filtered = probe(base, "/demo/?status=Open&priority=High")
    assert status == 200, f"Ticket filter returned {status}"
    assert b"Email client authentication failure" in filtered, "Open/high filter did not include expected fictional ticket"
    assert b"Laptop VPN connection intermittent" not in filtered, "Open/high filter included an in-progress ticket"

    status, _, filtered_assets = probe(base, "/demo/?asset_state=Maintenance")
    assert status == 200, f"Asset filter returned {status}"
    assert b"Wireless access point" in filtered_assets, "Asset maintenance filter did not include expected item"
    assert b"External display" not in filtered_assets, "Asset maintenance filter included available equipment"

    status, _, _ = probe(base, "/static/desk/style.css")
    assert status == 200, f"Static CSS returned {status}"

    for path in ("/admin/", "/login/", "/tickets/", "/assets/", "/tickets/new/", "/reports/", "/reports/export.csv"):
        status, _, _ = probe(base, path)
        assert status == 404, f"Private route {path} returned {status}, expected 404"
    for path in ("/demo/", "/tickets/new/", "/health/"):
        status, _, _ = probe(base, path, method="POST")
        assert status == 404, f"Write request {path} returned {status}, expected 404"
    print("PASS: v1.0 synthetic dashboard, filters, health, security headers, static files and demo isolation")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python scripts/verify_demo_http.py https://service.onrender.com")
    try:
        verify(sys.argv[1])
    except (AssertionError, ValueError, URLError) as exc:
        raise SystemExit(f"FAIL: {exc}") from exc
