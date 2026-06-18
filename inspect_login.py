import asyncio
import os
from playwright.async_api import async_playwright

# Load env variables
SAMSUNG_EMAIL = os.environ.get("SAMSUNG_EMAIL", "")
SAMSUNG_PASSWORD = os.environ.get("SAMSUNG_PASSWORD", "")

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        url = "https://account.smartthings.com/tokens"
        print(f"Navigating to {url}")
        await page.goto(url, wait_until="networkidle", timeout=30000)
        print(f"Landed at: {page.url}")
        
        await page.wait_for_timeout(3000)
        
        # Fill email
        print(f"Filling email field '#account' with '{SAMSUNG_EMAIL}'")
        await page.locator("#account").fill(SAMSUNG_EMAIL)
        
        # Look for next button
        next_btn = None
        for sel in ["#btnNext", "button:has-text('Next')", "button[type='submit']", ".btn-login"]:
            try:
                el = page.locator(sel).first
                if await el.is_visible():
                    next_btn = el
                    break
            except Exception:
                continue
                
        if next_btn:
            print("Clicking next button...")
            await next_btn.click()
            await page.wait_for_timeout(4000)
            
            # Fill password
            print("Filling password field '#password'")
            await page.locator("#password").fill(SAMSUNG_PASSWORD)
            print("Pressing Enter to submit password...")
            await page.locator("#password").press("Enter")
            await page.wait_for_timeout(5000)
            
            print(f"Landed at after Password submit: {page.url}")
            
            # Screenshot the 2FA page and save to /app/2fa_page.png so it mounts directly to host
            await page.screenshot(path="2fa_page_screenshot.png")
            print("Saved 2FA page screenshot to 2fa_page_screenshot.png")
            
            print("\n=== INPUTS (2FA Page) ===")
            inputs = await page.query_selector_all("input")
            for i, el in enumerate(inputs):
                print(f"Input {i}: tag={await el.evaluate('e => e.tagName')}, id={await el.get_attribute('id')}, name={await el.get_attribute('name')}, type={await el.get_attribute('type')}, placeholder={await el.get_attribute('placeholder')}, visible={await el.is_visible()}")
        else:
            print("Could not find Next button!")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
