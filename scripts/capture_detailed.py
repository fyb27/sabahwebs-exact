from playwright.sync_api import sync_playwright
import time
import os
import json

def main():
    screenshots_dir = r"Z:\sites\sabahwebs happycodes\sabahwebs\mirror\screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(args=['--ignore-certificate-errors'])
        ctx = browser.new_context(
            viewport={'width': 1440, 'height': 900},
            ignore_https_errors=True
        )
        page = ctx.new_page()

        try:
            page.goto("https://fyb27.github.io/sabahwebs-exact/", wait_until='networkidle', timeout=60000)
        except Exception as e:
            print(f"networkidle timeout: {e}")
        time.sleep(3)

        # --- Hero blob area: top 800px ---
        page.evaluate("window.scrollTo(0, 0)")
        time.sleep(0.5)
        page.screenshot(
            path=os.path.join(screenshots_dir, "page_b_hero_800.png"),
            clip={'x': 0, 'y': 0, 'width': 1440, 'height': 800}
        )
        print("Saved hero 800px")

        # --- Find the exact Y position of the tabs section ---
        tab_info = page.evaluate("""
            () => {
                const tabMenu = document.querySelector('.w-tab-menu, [data-current]');
                if (!tabMenu) return null;
                const rect = tabMenu.getBoundingClientRect();
                const scrollY = window.scrollY;
                return { top: rect.top + scrollY, height: rect.height };
            }
        """)
        print(f"Tab menu position: {tab_info}")

        # Scroll to tabs and capture a wide crop showing full section
        tab_pane_info = page.evaluate("""
            () => {
                const panes = document.querySelectorAll('.w-tab-pane');
                const results = [];
                for (const pane of panes) {
                    const rect = pane.getBoundingClientRect();
                    const scrollY = window.scrollY;
                    const style = getComputedStyle(pane);
                    results.push({
                        id: pane.id,
                        classes: pane.className,
                        scrollTop: rect.top + scrollY,
                        scrollBottom: rect.bottom + scrollY,
                        height: rect.height,
                        display: style.display,
                        opacity: style.opacity,
                        visibility: style.visibility,
                        overflow: style.overflow,
                        position: style.position
                    });
                }
                return results;
            }
        """)
        print("\nTab pane detailed info:")
        for p_info in tab_pane_info:
            print(f"  {p_info}")

        # Scroll to show the tabs area
        if tab_info:
            page.evaluate(f"window.scrollTo(0, {max(0, tab_info['top'] - 100)})")
            time.sleep(0.8)
            page.screenshot(
                path=os.path.join(screenshots_dir, "page_b_tabs_section.png"),
                full_page=False
            )
            print("Saved tabs section")

        # Now scroll down to show all 4 panes - are they all visible at once?
        if tab_pane_info:
            # Find the first pane's top
            first_top = tab_pane_info[0]['scrollTop']
            last_bottom = tab_pane_info[-1]['scrollBottom']
            total_height = last_bottom - first_top
            print(f"\nAll panes span: {first_top:.0f}px to {last_bottom:.0f}px ({total_height:.0f}px total)")

            # If total height > ~500px, content from ALL panes is likely visible
            if total_height > 600:
                print("WARNING: All pane content likely spans full page height = tabs probably NOT hiding inactive panes")
            else:
                print("Pane height looks normal = only active pane content visible")

            # Capture the area from tabs to end of panes
            page.evaluate(f"window.scrollTo(0, {max(0, first_top - 150)})")
            time.sleep(0.8)
            page.screenshot(
                path=os.path.join(screenshots_dir, "page_b_tabs_full_view.png"),
                full_page=False
            )

        # Also check the CSS on the w-tab-pane elements
        css_check = page.evaluate("""
            () => {
                const styleSheets = Array.from(document.styleSheets);
                const rules = [];
                for (const sheet of styleSheets) {
                    try {
                        const cssRules = Array.from(sheet.cssRules || []);
                        for (const rule of cssRules) {
                            if (rule.selectorText && rule.selectorText.includes('w-tab-pane')) {
                                rules.push({ selector: rule.selectorText, css: rule.cssText });
                            }
                        }
                    } catch(e) {}
                }
                return rules;
            }
        """)
        print(f"\nCSS rules for .w-tab-pane:")
        for rule in css_check:
            print(f"  {rule['selector']}: {rule['css'][:200]}")

        ctx.close()
        browser.close()

if __name__ == '__main__':
    main()
