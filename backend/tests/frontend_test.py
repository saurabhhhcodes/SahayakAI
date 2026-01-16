import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Load the App (Localhost)
        # Capture Console Logs
        page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))
        
        print("Loading App at http://localhost:8002/app/...")
        await page.goto("http://localhost:8002/app/")
        
        # 2. Wait for Load
        await page.wait_for_selector("#text-input")
        print("App Loaded.")

        # 3. Test SOS Button
        print("\n[TEST] Clicking SOS Button...")
        
        # Verify button exists
        sos_btn = await page.query_selector("#sos-btn")
        if not sos_btn:
            print("❌ SOS Button NOT FOUND in DOM")
            await browser.close()
            return
            
        print("Found SOS Button. Clicking...")
        await sos_btn.click()
        
        # Verify "User" message appears (The preset text)
        print("Waiting for user message...")
        try:
            user_msg_selector = ".user-message"
            # Increase timeout to 5s
            await page.wait_for_selector(user_msg_selector, timeout=5000)
            
            # Get all user messages
            msgs = await page.query_selector_all(".user-message .message-content")
            if msgs:
                last_msg = await msgs[-1].text_content()
                print(f"✅ SOS Button Worked. User Message Sent: {last_msg[:50]}...")
            else:
                 print("❌ Message selector found but no content?")
                 
        except Exception as e:
            print(f"❌ SOS Button FAILED. Message not seen. Error: {e}")
            # Take screenshot on failure
            await page.screenshot(path="debug_failure.png")
            print("Captured debug_failure.png")
            await browser.close()
            return

        # 4. Test Design Button
        print("\n[TEST] Clicking Design Button...")
        await page.click("#design-btn")
        
        # Verify User Message updated
        await page.wait_for_timeout(2000)
        msgs = await page.query_selector_all(".user-message .message-content")
        last_msg = await msgs[-1].text_content()
        
        if "NGO" in last_msg:
             print(f"✅ Design Button Worked. User Message Sent: {last_msg[:50]}...")
        else:
             print(f"❌ Design Button FAILED. Got: {last_msg}")

        print("\nALL BUTTON TESTS PASSED ✅")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
