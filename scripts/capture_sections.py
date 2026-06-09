from playwright.sync_api import sync_playwright
import time
import os

def main():
    screenshots_dir = r"Z:\sites\sabahwebs happycodes\sabahwebs\mirror\screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--ignore-certificate-errors'])

        # ---- Try Page A via http (redirect) or with different TLS ----
        print("Trying Page A with http://...")
        ctx_a = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            ignore_https_errors=True
        )
        page_a = ctx_a.new_page()
        loaded_a = False
        for url_try in ["http://sabahwebs.com/", "https://www.sabahwebs.com/"]:
            try:
                page_a.goto(url_try, wait_until='domcontentloaded', timeout=30000)
                time.sleep(3)
                loaded_a = True
                print(f"  Loaded A via: {url_try}")
                break
            except Exception as e:
                print(f"  Failed {url_try}: {e}")

        if loaded_a:
            page_a.screenshot(path=os.path.join(screenshots_dir, "page_a_hero_v2.png"), full_page=False)
            # Scroll to resources
            try:
                # look for the tabbed resources section
                page_a.evaluate("() => { const els = Array.from(document.querySelectorAll('*')); const el = els.find(e => e.innerText && e.innerText.includes('E-commerce') && e.offsetHeight > 20); if(el) el.scrollIntoView(); }")
                time.sleep(1)
                page_a.screenshot(path=os.path.join(screenshots_dir, "page_a_resources_v2.png"), full_page=False)
                print("  Saved A resources")
            except Exception as e:
                print(f"  A resources failed: {e}")

            # Capture hero section specifically via clip
            page_a.evaluate("window.scrollTo(0, 0)")
            time.sleep(0.5)
            # Hero clip: top 700px
            page_a.screenshot(
                path=os.path.join(screenshots_dir, "page_a_hero_clip.png"),
                clip={'x': 0, 'y': 0, 'width': 1440, 'height': 700}
            )
            print("  Saved A hero clip")
        ctx_a.close()

        # ---- Page B sections ----
        print("\nCapturing Page B sections...")
        ctx_b = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            ignore_https_errors=True
        )
        page_b = ctx_b.new_page()

        # Collect all network events
        all_requests = []
        def on_response(resp):
            if resp.status >= 400:
                all_requests.append((resp.status, resp.url))
        page_b.on('response', on_response)

        try:
            page_b.goto("https://fyb27.github.io/sabahwebs-exact/", wait_until='networkidle', timeout=60000)
        except Exception as e:
            print(f"  B networkidle timeout: {e}")
        time.sleep(3)

        # Hero / above-fold clip
        page_b.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
        page_b.screenshot(
            path=os.path.join(screenshots_dir, "page_b_hero_clip.png"),
            clip={'x': 0, 'y': 0, 'width': 1440, 'height': 700}
        )
        print("  Saved B hero clip")

        # Find resources/tabs section
        # Try scrolling to the tabs using JS
        result = page_b.evaluate("""
            () => {
                // Look for elements with tab-related text
                const selectors = [
                    '[data-current]',
                    '.w-tab-link',
                    '.tabs-menu',
                    '[role="tab"]'
                ];
                for (const sel of selectors) {
                    const el = document.querySelector(sel);
                    if (el) {
                        el.scrollIntoView({block: 'center'});
                        return {found: true, selector: sel, text: el.innerText || el.textContent};
                    }
                }
                // Try by text
                const allEls = document.querySelectorAll('div, a, button');
                for (const el of allEls) {
                    if (el.textContent.includes('E-commerce') && el.offsetHeight > 10) {
                        el.scrollIntoView({block: 'center'});
                        return {found: true, tag: el.tagName, text: el.textContent.substring(0,100)};
                    }
                }
                return {found: false};
            }
        """)
        print(f"  Resources scroll result: {result}")
        time.sleep(1.5)
        page_b.screenshot(
            path=os.path.join(screenshots_dir, "page_b_resources_clip.png"),
            full_page=False
        )
        print("  Saved B resources clip")

        # Also check DOM state of the tabs
        tabs_info = page_b.evaluate("""
            () => {
                const info = {};
                // Webflow tabs
                const tabLinks = document.querySelectorAll('.w-tab-link');
                info.tabLinks = Array.from(tabLinks).map(el => ({
                    text: el.textContent.trim(),
                    classes: el.className,
                    ariaSelected: el.getAttribute('aria-selected')
                }));
                // Tab panes
                const tabPanes = document.querySelectorAll('.w-tab-pane');
                info.tabPanes = Array.from(tabPanes).map(el => ({
                    id: el.id,
                    classes: el.className,
                    display: getComputedStyle(el).display,
                    opacity: getComputedStyle(el).opacity,
                    childCount: el.children.length
                }));
                // Blob/decorative elements in hero
                const blobs = document.querySelectorAll('[class*="blob"], [class*="shape"], [class*="circle"]');
                info.blobCount = blobs.length;
                info.blobSample = Array.from(blobs).slice(0,5).map(el => ({
                    tag: el.tagName,
                    classes: el.className,
                    display: getComputedStyle(el).display,
                    opacity: getComputedStyle(el).opacity,
                    transform: getComputedStyle(el).transform,
                    position: getComputedStyle(el).position
                }));
                // Hero section - look for IX2 animated elements
                const heroSection = document.querySelector('.hero, [class*="hero"], section:first-of-type');
                if (heroSection) {
                    info.heroClasses = heroSection.className;
                    info.heroVisibility = getComputedStyle(heroSection).visibility;
                }
                return info;
            }
        """)

        import json
        with open(os.path.join(screenshots_dir, "page_b_dom_info.json"), 'w') as f:
            json.dump(tabs_info, f, indent=2)
        print("  Saved DOM info")
        print(f"  Tab links found: {len(tabs_info.get('tabLinks', []))}")
        print(f"  Tab panes found: {len(tabs_info.get('tabPanes', []))}")
        if tabs_info.get('tabPanes'):
            for pane in tabs_info['tabPanes']:
                print(f"    Pane: {pane.get('id','')} | classes: {pane.get('classes','')} | display: {pane.get('display')} | opacity: {pane.get('opacity')} | children: {pane.get('childCount')}")
        if tabs_info.get('tabLinks'):
            for link in tabs_info['tabLinks']:
                print(f"    Tab: {link.get('text','')} | classes: {link.get('classes','')} | aria-selected: {link.get('ariaSelected')}")

        print(f"  Blob elements: {tabs_info.get('blobCount', 0)}")
        for blob in tabs_info.get('blobSample', []):
            print(f"    {blob}")

        ctx_b.close()
        browser.close()

    print("\nDone.")

if __name__ == '__main__':
    main()
