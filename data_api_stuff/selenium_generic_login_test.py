from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    pytest_html = item.config.pluginmanager.getplugin('html')
    outcome = yield
    report = outcome.get_result()
    extra = getattr(report, 'extra', [])
    if report.when == 'call' and report.failed:
        driver = item.funcargs.get('setup')
        if driver:
            screenshot = driver.get_screenshot_as_base64()
            html = f'<div><img src="data:image/png;base64,{screenshot}" style="width:600px;"></div>'
            extra.append(pytest_html.extras.html(html))
            report.extra = extra

@pytest.fixture()
def setup(request):
    url = getattr(request, 'param', None)
    if url is None:
        url = "https://example.com"
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()
    driver.implicitly_wait(10)
    yield driver
    driver.quit()

@pytest.fixture()
def browser_utils(setup):
    driver = setup
    def typeit(keys, by, locator):
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((by, locator)))
        element.send_keys(keys)

    def clickit(by, locator):
        wait = WebDriverWait(driver, 10)
        element = wait.until(EC.presence_of_element_located((by, locator)))
        element.click()
    return typeit, clickit

# Example test: you can add more param sets for different websites
login_test_configs = [
    {
        "url": "https://svburger1.co.il/#/HomePage",
        "login_button": (By.XPATH, "//a[@href='#/SignIn']/button"),
        "email_input": (By.XPATH, "//input[@placeholder ='Enter your email']"),
        "password_input": (By.XPATH, "//input[@placeholder ='Enter your password']"),
        "submit_button": (By.XPATH, "//button[@type ='submit']"),
        "success_indicator": (By.XPATH, "//div[@class='card3 text-center']"),
        "users": [["shay@project.com", "123456!"]],
    }
]

@pytest.mark.parametrize("cfg", login_test_configs)
@pytest.mark.parametrize("email,password", [["shay@project.com", "123456!"]])
def test_generic_login(cfg, email, password, request, browser_utils):
    request._fixturemanager._arg2fixturedefs['setup'][0].params = [cfg["url"]]
    typeit, clickit = browser_utils
    clickit(*cfg["login_button"])
    typeit(email, *cfg["email_input"])
    typeit(password, *cfg["password_input"])
    clickit(*cfg["submit_button"])
    assert request.node.funcargs['setup'].find_element(*cfg["success_indicator"]).is_displayed()

EH_login_test_configs = [
    {
        "url": "https://svburger1.co.il/#/HomePage",
        "login_button": (By.XPATH, "//a[@href='#/SignIn']/button"),
        "email_input": (By.XPATH, "//input[@placeholder ='Enter your email']"),
        "password_input": (By.XPATH, "//input[@placeholder ='Enter your password']"),
        "submit_button": (By.XPATH, "//button[@type ='submit']"),
        "alert": True,
        "users": [["nonereg@none.com", "123456!"], ["shay@project.com", "123456sa!"]],
        "alert_text": "Failed to log in"
    }
]

@pytest.mark.parametrize("cfg", EH_login_test_configs)
@pytest.mark.parametrize("email,password", [["nonereg@none.com", "123456!"], ["shay@project.com", "123456sa!"]])
def test_generic_login_error(cfg, email, password, request, browser_utils):
    request._fixturemanager._arg2fixturedefs['setup'][0].params = [cfg["url"]]
    typeit, clickit = browser_utils
    clickit(*cfg["login_button"])
    typeit(email, *cfg["email_input"])
    typeit(password, *cfg["password_input"])
    clickit(*cfg["submit_button"])
    if cfg.get("alert"):
        driver = request.node.funcargs['setup']
        WebDriverWait(driver, 10).until(EC.alert_is_present())
        alert = driver.switch_to.alert
        assert cfg["alert_text"] == alert.text
        alert.accept()