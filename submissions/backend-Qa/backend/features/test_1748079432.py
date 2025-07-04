from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytest

# tests/conftest.py
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

@pytest.fixture(scope="class")
def driver():
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

@pytest.fixture(scope="class")
def base_url():
    return "https://example.com"

@pytest.fixture(scope="class")
def login_url(base_url):
    return f"{base_url}/login"

@pytest.fixture(scope="class")
def register_url(base_url):
    return f"{base_url}/register"

@pytest.fixture(scope="class")
def search_url(base_url):
    return f"{base_url}/search"

@pytest.fixture(scope="class")
def cart_url(base_url):
    return f"{base_url}/cart"

@pytest.fixture(scope="class")
def order_history_url(base_url):
    return f"{base_url}/order-history"