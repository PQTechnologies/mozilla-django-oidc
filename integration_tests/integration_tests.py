import unittest
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class IntegrationTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(IntegrationTest, self).__init__(*args, **kwargs)

        self.account = {
            "username": "example_username",
            "password": "example_p@ssw0rd",
            "email": "example@example.com",
        }

    def get_browser(self):
        """Get a browser instance with proper configuration"""
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        service = Service("/usr/bin/geckodriver")
        return webdriver.Firefox(service=service, options=options)

    def setUp(self):
        """Create test account in `testprovider` instance"""
        driver = self.get_browser()
        try:
            driver.get("http://testprovider:8080/account/signup")

            # Wait for elements to be present and fill them
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "#id_username"))
            )

            driver.find_element(By.CSS_SELECTOR, "#id_username").send_keys(
                self.account["username"]
            )
            driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys(
                self.account["password"]
            )
            driver.find_element(By.CSS_SELECTOR, "#id_password_confirm").send_keys(
                self.account["password"]
            )
            driver.find_element(By.CSS_SELECTOR, "#id_email").send_keys(
                self.account["email"]
            )
            driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()
        finally:
            driver.quit()

    def tearDown(self):
        """Remove test account from `testprovider` instance"""
        driver = self.get_browser()
        try:
            self.perform_login(driver)
            driver.get("http://testprovider:8080/account/delete")

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-danger"))
            )
            driver.find_element(By.CSS_SELECTOR, ".btn-danger").click()
        finally:
            driver.quit()

    def perform_login(self, driver):
        """Perform login using webdriver"""
        driver.get("http://testrp:8081")

        # Wait for login link and click it
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div > a"))
        )
        driver.find_element(By.CSS_SELECTOR, "div > a").click()

        # Fill login form
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "#id_username"))
        )
        driver.find_element(By.CSS_SELECTOR, "#id_username").send_keys(
            self.account["username"]
        )
        driver.find_element(By.CSS_SELECTOR, "#id_password").send_keys(
            self.account["password"]
        )
        driver.find_element(By.CSS_SELECTOR, ".btn-primary").click()

    def perform_logout(self, driver):
        """Perform logout using webdriver"""
        driver.get("http://testrp:8081")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'input[value="Logout"]'))
        )
        driver.find_element(By.CSS_SELECTOR, 'input[value="Logout"]').click()

    def test_login(self):
        """Test logging in `testrp` using OIDC"""
        driver = self.get_browser()
        try:
            # Check that user is not logged in
            driver.get("http://testrp:8081")
            self.assertNotIn("Current user:", driver.page_source)

            # Perform login
            self.perform_login(driver)

            # Accept scope
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="allow"]'))
            )
            driver.find_element(By.CSS_SELECTOR, 'input[name="allow"]').click()

            # Check that user is now logged in
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Current user:')]")
                )
            )
            self.assertIn("Current user:", driver.page_source)
        finally:
            driver.quit()

    def test_logout(self):
        """Test logout functionality of OIDC lib"""
        driver = self.get_browser()
        try:
            # Check that user is not logged in
            driver.get("http://testrp:8081")
            self.assertNotIn("Current user:", driver.page_source)

            self.perform_login(driver)

            # Accept scope
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[name="allow"]'))
            )
            driver.find_element(By.CSS_SELECTOR, 'input[name="allow"]').click()

            # Check that user is now logged in
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//*[contains(text(), 'Current user:')]")
                )
            )
            self.assertIn("Current user:", driver.page_source)

            self.perform_logout(driver)

            # Check that user is now logged out
            WebDriverWait(driver, 10).until(
                lambda d: "Current user:" not in d.page_source
            )
            self.assertNotIn("Current user:", driver.page_source)
        finally:
            driver.quit()


if __name__ == "__main__":
    unittest.main()
