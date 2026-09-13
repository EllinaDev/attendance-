import os
import time
import asyncio

os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""
os.environ["http_proxy"] = ""
os.environ["https_proxy"] = ""
os.environ["NO_PROXY"] = "*"
os.environ["no_proxy"] = "*"

from playwright.async_api import async_playwright

SCREENSHOT_DIR = "/Users/elinamamadalieva/.gemini/antigravity/brain/e63409cf-e341-479c-8b35-1e6961daf9d0/screenshots"
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

BASE_URL = "http://127.0.0.1:8080"

async def capture_screenshots():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        page = await context.new_page()

        print("1. Capturing Home page...")
        await page.goto(f"{BASE_URL}/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/01_home.png", full_page=True)

        print("2. Capturing Login page...")
        await page.goto(f"{BASE_URL}/login/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/02_login.png", full_page=True)

        print("3. Logging in as Teacher (prof_smith)...")
        await page.fill("input[name='username']", "prof_smith")
        await page.fill("input[name='password']", "password123")
        await page.check("input[name='role'][value='teacher']")
        await page.click("button[type='submit']")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/03_teacher_dashboard.png", full_page=True)

        print("4. Capturing Course Detail...")
        await page.goto(f"{BASE_URL}/course/1/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/04_course_detail.png", full_page=True)

        print("5. Capturing Live Dynamic QR Lesson Detail...")
        await page.goto(f"{BASE_URL}/lesson/1/")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=f"{SCREENSHOT_DIR}/05_lesson_qr_session.png", full_page=True)

        print("6. Logging in as Student (alex_dev)...")
        student_context = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=2)
        student_page = await student_context.new_page()
        await student_page.goto(f"{BASE_URL}/login/")
        await student_page.fill("input[name='username']", "alex_dev")
        await student_page.fill("input[name='password']", "password123")
        await student_page.check("input[name='role'][value='student']")
        await student_page.click("button[type='submit']")
        await student_page.wait_for_load_state("networkidle")
        await student_page.screenshot(path=f"{SCREENSHOT_DIR}/06_student_dashboard.png", full_page=True)

        print("7. Capturing Student Course Detail...")
        await student_page.goto(f"{BASE_URL}/student/course/1/")
        await student_page.wait_for_load_state("networkidle")
        await student_page.screenshot(path=f"{SCREENSHOT_DIR}/07_student_course_detail.png", full_page=True)

        print("8. Capturing Student Assignment View...")
        await student_page.goto(f"{BASE_URL}/assignment/1/")
        await student_page.wait_for_load_state("networkidle")
        await student_page.screenshot(path=f"{SCREENSHOT_DIR}/08_student_assignment.png", full_page=True)

        print("9. Capturing Mobile Check-in View...")
        mobile_context = await browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=3,
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 16_5 like Mac OS X) AppleWebKit/605.1.15"
        )
        mobile_page = await mobile_context.new_page()
        await mobile_page.goto(f"{BASE_URL}/login/")
        await mobile_page.fill("input[name='username']", "maria_tech")
        await mobile_page.fill("input[name='password']", "password123")
        await mobile_page.check("input[name='role'][value='student']")
        await mobile_page.click("button[type='submit']")
        await mobile_page.wait_for_load_state("networkidle")
        await mobile_page.screenshot(path=f"{SCREENSHOT_DIR}/09_mobile_student_dashboard.png")

        print("Screenshots captured successfully!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(capture_screenshots())
