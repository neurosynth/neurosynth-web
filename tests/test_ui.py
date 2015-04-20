''' UI tests via selenium. '''
from selenium import webdriver
from nsweb.initializers import settings
from pytest import fixture


@fixture
def driver():
    return webdriver.Chrome()


def test_front_page_loads(driver):
    driver.get(settings.TEST_URL)
    assert "Neurosynth" in driver.title
    driver.close()
