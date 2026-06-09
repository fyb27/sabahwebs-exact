from playwright.sync_api import sync_playwright
import time
import json
import os

def main():
    screenshots_dir = r"Z:\sites\sabahwebs happycodes\sabahwebs\mirror\screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    url_a = "https://sabahwebs.com/"
    url_b = "https://fyb27.github.io/sabahwebs-exact/"

    path_a_full    = os.path.join(screenshots_dir, "page_a_sabahwebs_desktop.png")
    path_b_full    = os.path.join(screenshots_dir, "page_b_clone_desktop.png")
    path_a_hero    = os.path.join(screenshots_dir, "page_a_hero.png")
    path_b_hero    = os.path.join(screenshots_dir, "page_b_hero.png")
    path_a_resources = os.path.join(screenshots_dir, "page_a_resources.png")
    path_b_resources = os.path.join(screenshots_dir, "page_b_resources.png")

    with sync_playwright() as p:
        # Launch with ignore_https_errors to handle SSL issues
        browser = p.chromium.launch(args=['--ignore-certificate-errors'])

        # ---------- PAGE A ----------
        print("Capturing Page A (original)...")
        ctx_a = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            ignore_https_errors=True
        )
        page_a = ctx_a.new_page()
        try:
            page_a.goto(url_a, wait_until='networkidle', timeout=60000)
        except Exception as e:
            print(f"networkidle timed out on A, continuing: {e}")
        time.sleep(3)
        page_a.screenshot(path=path_a_full, full_page=True)
        print(f"Saved full: {path_a_full}")
        # Above-fold hero
        page_a.screenshot(path=path_a_hero, full_page=False)
        print(f"Saved hero: {path_a_hero}")

        # Try to find and scroll to the Resources / tabs section
        try:
            # Look for the section by visible tab text
            el = page_a.locator('text=E-commerce').first
            el.scroll_into_view_if_needed()
            time.sleep(1.5)
            page_a.screenshot(path=path_a_resources, full_page=False)
            print(f"Saved resources: {path_a_resources}")
        except Exception as e:
            print(f"Resources scroll A failed, trying generic selector: {e}")
            try:
                page_a.evaluate("window.scrollBy(0, document.body.scrollHeight * 0.6)")
                time.sleep(1)
                page_a.screenshot(path=path_a_resources, full_page=False)
                print(f"Saved resources (fallback): {path_a_resources}")
            except Exception as e2:
                print(f"Resources scroll A fallback failed: {e2}")

        ctx_a.close()

        # ---------- PAGE B ----------
        print("\nCapturing Page B (clone)...")
        console_errors = []
        failed_requests = []

        ctx_b = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            ignore_https_errors=True
        )
        page_b = ctx_b.new_page()

        def handle_console(msg):
            if msg.type in ('error', 'warning'):
                console_errors.append({'type': msg.type, 'text': msg.text})

        def handle_request_failed(request):
            failed_requests.append({'url': request.url, 'failure': str(request.failure)})

        def handle_response(response):
            if response.status >= 400:
                failed_requests.append({'url': response.url, 'status': response.status})

        page_b.on('console', handle_console)
        page_b.on('requestfailed', handle_request_failed)
        page_b.on('response', handle_response)

        try:
            page_b.goto(url_b, wait_until='networkidle', timeout=60000)
        except Exception as e:
            print(f"networkidle timed out on B, continuing: {e}")
        time.sleep(3)

        page_b.screenshot(path=path_b_full, full_page=True)
        print(f"Saved full: {path_b_full}")
        page_b.screenshot(path=path_b_hero, full_page=False)
        print(f"Saved hero: {path_b_hero}")

        # Resources section on B
        try:
            el_b = page_b.locator('text=E-commerce').first
            el_b.scroll_into_view_if_needed()
            time.sleep(1.5)
            page_b.screenshot(path=path_b_resources, full_page=False)
            print(f"Saved resources: {path_b_resources}")
        except Exception as e:
            print(f"Resources scroll B failed, trying generic: {e}")
            try:
                page_b.evaluate("window.scrollBy(0, document.body.scrollHeight * 0.6)")
                time.sleep(1)
                page_b.screenshot(path=path_b_resources, full_page=False)
                print(f"Saved resources (fallback): {path_b_resources}")
            except Exception as e2:
                print(f"Resources scroll B fallback failed: {e2}")

        ctx_b.close()
        browser.close()

    # ---------- REPORT ----------
    print("\n=== CONSOLE ERRORS on Page B ===")
    if console_errors:
        for e in console_errors[:40]:
            print(f"  [{e['type'].upper()}] {e['text'][:200]}")
    else:
        print("  None")

    print("\n=== FAILED / 4xx REQUESTS on Page B ===")
    if failed_requests:
        seen = set()
        for r in failed_requests:
            url = r.get('url', '')
            if url not in seen:
                seen.add(url)
                status = r.get('status', r.get('failure', '?'))
                print(f"  [{status}] {url}")
    else:
        print("  None")

    logs_path = os.path.join(screenshots_dir, "page_b_logs.json")
    with open(logs_path, 'w') as f:
        json.dump({'console_errors': console_errors, 'failed_requests': failed_requests}, f, indent=2)
    print(f"\nLogs saved: {logs_path}")


if __name__ == '__main__':
    main()
