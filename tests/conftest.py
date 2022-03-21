import os
import time

import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions


def pytest_addoption(parser):
    parser.addoption('--browser_name', action='store', default="chrome",
                     help="Choose browser: chrome or firefox")
    parser.addoption('--language', action='store', default="en",
                     help="Choose browser language")
    parser.addoption('--headless', action='store', default="true",
                     help="Choose launch mode")
    parser.addoption('--window', action='store', default="0,0",
                     help="Choose launch mode")


@pytest.fixture(scope="function")
def browser(request):
    browser_name = request.config.getoption("browser_name")
    user_language = request.config.getoption("language")
    headless = request.config.getoption("headless")
    x, y = request.config.getoption("window").split(',')
    x, y = int(x), int(y)

    if browser_name == "chrome":
        options = ChromeOptions()
        options.add_experimental_option('prefs', {'intl.accept_languages': user_language})
        if headless == "true":
            options.add_argument('headless')
        if x == 0 and y == 0:
            options.add_argument("window-size=1920,1080")
            print("\nstart chrome browser for test..")
            browser = webdriver.Chrome(options=options)
        else:
            print("\nstart chrome browser for test..")
            browser = webdriver.Chrome(options=options)
            browser.set_window_size(x, y)
        request.cls.driver = browser
    elif browser_name == "firefox":
        fp = webdriver.FirefoxProfile()
        fp.set_preference("intl.accept_languages", user_language)
        options = FirefoxOptions()
        if headless == "true":
            options.headless = True
        if x == 0 and y == 0:
            options.add_argument("window-size=1920,1080")
            print("\nstart chrome browser for test..")
            browser = webdriver.Firefox(firefox_profile=fp, options=options)
        else:
            print("\nstart chrome browser for test..")
            browser = webdriver.Firefox(firefox_profile=fp, options=options)
            browser.set_window_size(x, y)
        request.cls.driver = browser
    else:
        raise pytest.UsageError("--browser_name should be chrome or firefox")
    yield browser
    print("\nquit browser..")
    browser.quit()


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
    return rep


@pytest.fixture(autouse=True)
def take_screenshot_if_test_fail(request, browser):
    yield request.cls.driver
    directory = os.path.join(os.path.dirname(__file__), '../failures-screenshots/')
    if not os.path.exists(directory):
        os.mkdir(directory)
    if request.node.rep_setup.failed:
        try:
            allure.attach(
                request.cls.driver.get_screenshot_as_png(),
                name='screenshot',
                attachment_type=allure.attachment_type.PNG
            )
            request.cls.driver.save_screenshot(os.path.join(directory, 'screenshot' + str(time.time()) + '.png'))
        except:
            pass
    elif request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            try:
                allure.attach(
                    request.cls.driver.get_screenshot_as_png(),
                    name='screenshot',
                    attachment_type=allure.attachment_type.PNG
                )
                request.cls.driver.save_screenshot(os.path.join(directory, 'screenshot' + str(time.time()) + '.png'))
            except:
                pass
    else:
        raise Exception
