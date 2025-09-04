import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="function")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

def test_login_success(browser):
    page = browser.new_page()
    page.goto("https://svburger1.co.il/#/HomePage")
    page.click("//a[@href='#/SignIn']/button")
    page.fill("//input[@placeholder ='Enter your email']", "shay@project.com")
    page.fill("//input[@placeholder ='Enter your password']", "123456!")
    page.click("//button[@type ='submit']")
    success_selector = "//div[@class='card3 text-center']"
    assert page.is_visible(success_selector)
    page.close()

def test_login_fail(browser):
    page = browser.new_page()
    page.goto("https://svburger1.co.il/#/HomePage")
    page.click("//a[@href='#/SignIn']/button")
    page.fill("//input[@placeholder ='Enter your email']", "nonereg@none.com")
    page.fill("//input[@placeholder ='Enter your password']", "123456!")
    page.click("//button[@type ='submit']")
    try:
        page.wait_for_event("dialog", timeout=5000)
        dialog = page.expect_event("dialog")
        assert "Failed to log in" in dialog.value.message
        dialog.value.accept()
    except:
        assert False, "Login error dialog not shown"
    page.close()