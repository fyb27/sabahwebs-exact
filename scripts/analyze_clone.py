import json
import os
from playwright.sync_api import sync_playwright

URL = "https://fyb27.github.io/sabahwebs-exact/"
SCREENSHOTS_DIR = r"Z:\sites\sabahwebs happycodes\sabahwebs\mirror\screenshots"

os.makedirs(SCREENSHOTS_DIR, exist_ok=True)

console_messages = []
failed_requests = []

def capture():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1920, "height": 1080})

        # Collect console messages
        page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text}))

        # Collect failed requests
        def on_request_failed(req):
            failed_requests.append({"url": req.url, "failure": req.failure})
        page.on("requestfailed", on_request_failed)

        # Also collect 404s via response
        responses_404 = []
        def on_response(resp):
            if resp.status == 404:
                responses_404.append(resp.url)
        page.on("response", on_response)

        page.goto(URL, wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2000)

        # Desktop screenshot (above fold)
        desktop_path = os.path.join(SCREENSHOTS_DIR, "clone_desktop.png")
        page.screenshot(path=desktop_path, full_page=False)

        # Full page screenshot
        full_path = os.path.join(SCREENSHOTS_DIR, "clone_full.png")
        page.screenshot(path=full_path, full_page=True)

        # --- TABS ANALYSIS ---
        # Get all tab panes and their computed display styles
        tab_data = page.evaluate("""() => {
            const panes = Array.from(document.querySelectorAll('.w-tab-pane'));
            return panes.map((pane, i) => {
                const cs = window.getComputedStyle(pane);
                return {
                    index: i,
                    hasActive: pane.classList.contains('w--tab-active'),
                    display: cs.display,
                    visibility: cs.visibility,
                    classList: Array.from(pane.classList).join(' '),
                    cardCount: pane.querySelectorAll('.w-dyn-item, [class*="card"], [class*="Card"]').length
                };
            });
        }""")

        # Get tab links
        tab_links = page.evaluate("""() => {
            const links = Array.from(document.querySelectorAll('.w-tab-link'));
            return links.map((link, i) => ({
                index: i,
                text: link.textContent.trim(),
                hasActive: link.classList.contains('w--current'),
                classList: Array.from(link.classList).join(' ')
            }));
        }""")

        # Screenshot before clicking second tab
        before_path = os.path.join(SCREENSHOTS_DIR, "clone_tabs_before.png")

        # Scroll to tabs section first
        page.evaluate("""() => {
            const tabEl = document.querySelector('.w-tab-pane');
            if (tabEl) tabEl.scrollIntoView({behavior: 'instant', block: 'center'});
        }""")
        page.wait_for_timeout(500)
        page.screenshot(path=before_path, full_page=False)

        # Click the second tab
        second_tab_clicked = False
        tab_links_els = page.query_selector_all(".w-tab-link")
        if len(tab_links_els) >= 2:
            tab_links_els[1].click()
            page.wait_for_timeout(800)
            second_tab_clicked = True

        after_path = os.path.join(SCREENSHOTS_DIR, "clone_tabs_after_click.png")
        page.screenshot(path=after_path, full_page=False)

        # Re-evaluate panes after click
        tab_data_after = page.evaluate("""() => {
            const panes = Array.from(document.querySelectorAll('.w-tab-pane'));
            return panes.map((pane, i) => {
                const cs = window.getComputedStyle(pane);
                return {
                    index: i,
                    hasActive: pane.classList.contains('w--tab-active'),
                    display: cs.display,
                    classList: Array.from(pane.classList).join(' ')
                };
            });
        }""")

        # --- BLOB / HEADER ANALYSIS ---
        blob_data = page.evaluate("""() => {
            // Look for SVG elements in hero/header area
            const heroSelectors = ['header', '.hero', '.hero-section', '.header', '[class*="hero"]', '[class*="blob"]'];
            let results = [];
            heroSelectors.forEach(sel => {
                const els = document.querySelectorAll(sel);
                els.forEach(el => {
                    const svgs = el.querySelectorAll('svg');
                    svgs.forEach(svg => {
                        const cs = window.getComputedStyle(svg);
                        const rect = svg.getBoundingClientRect();
                        results.push({
                            selector: sel,
                            fill: svg.getAttribute('fill'),
                            style: svg.getAttribute('style'),
                            computedColor: cs.color,
                            computedFill: cs.fill,
                            width: rect.width,
                            height: rect.height,
                            x: rect.x,
                            y: rect.y
                        });
                    });
                });
            });
            // Also check all SVGs in top 600px of page
            const allSvgs = document.querySelectorAll('svg');
            const topSvgs = Array.from(allSvgs).filter(svg => {
                const r = svg.getBoundingClientRect();
                return r.top < 600;
            }).map(svg => {
                const cs = window.getComputedStyle(svg);
                const r = svg.getBoundingClientRect();
                // Check if any path/circle inside is black
                const paths = svg.querySelectorAll('path, circle, ellipse');
                const fills = Array.from(paths).map(p => {
                    return {fill: p.getAttribute('fill'), computedFill: window.getComputedStyle(p).fill};
                });
                return {
                    fill: svg.getAttribute('fill'),
                    width: r.width, height: r.height,
                    x: r.x, y: r.y,
                    childFills: fills.slice(0, 5)
                };
            });
            return {heroSvgs: results, topSvgs: topSvgs};
        }""")

        # Check for black circles/dots specifically
        black_dots = page.evaluate("""() => {
            const circles = document.querySelectorAll('circle, ellipse');
            return Array.from(circles).filter(c => {
                const r = c.getBoundingClientRect();
                if (r.top > 800) return false;
                const cs = window.getComputedStyle(c);
                const fill = c.getAttribute('fill') || cs.fill || '';
                // Check if fill is black or very dark
                return fill === '#000' || fill === 'black' || fill === 'rgb(0, 0, 0)' ||
                       cs.fill === 'rgb(0, 0, 0)';
            }).map(c => {
                const r = c.getBoundingClientRect();
                const cs = window.getComputedStyle(c);
                return {
                    tag: c.tagName,
                    fill: c.getAttribute('fill'),
                    computedFill: cs.fill,
                    x: r.x, y: r.y, w: r.width, h: r.height
                };
            });
        }""")

        # Hero screenshot zoomed in
        hero_path = os.path.join(SCREENSHOTS_DIR, "clone_hero_zoom.png")
        page.evaluate("window.scrollTo(0, 0)")
        page.wait_for_timeout(300)
        page.screenshot(path=hero_path, full_page=False, clip={"x": 0, "y": 0, "width": 1920, "height": 600})

        browser.close()

        return {
            "tab_data_before": tab_data,
            "tab_data_after": tab_data_after,
            "tab_links": tab_links,
            "second_tab_clicked": second_tab_clicked,
            "blob_data": blob_data,
            "black_dots": black_dots,
            "console_messages": console_messages,
            "failed_requests": failed_requests,
            "responses_404": responses_404,
            "screenshots": {
                "desktop": desktop_path,
                "full": full_path,
                "hero": hero_path,
                "tabs_before": before_path,
                "tabs_after": after_path
            }
        }

results = capture()
print(json.dumps(results, indent=2))
