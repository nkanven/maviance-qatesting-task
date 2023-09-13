import os
import time
import unittest
import HtmlTestRunner
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, \
    ElementClickInterceptedException
from dotenv import load_dotenv
import tracemalloc

tracemalloc.start()

load_dotenv()


class TestSmobilpay(unittest.TestCase):
    chrome_options = None

    @classmethod
    def setUp(self):
        self.chrome_options = Options()
        self.chrome_options.add_experimental_option("detach", True)
        self.ignored_exceptions = (NoSuchElementException, StaleElementReferenceException,)
        self.driver = webdriver.Chrome(options=self.chrome_options)


    def locate_element(self, tag: str, name: str, delay: int = 15):
        return WebDriverWait(self.driver, delay, ignored_exceptions=self.ignored_exceptions).until(
            ec.presence_of_element_located((tag, name)))

    def locate_elements(self, tag: str, name: str, delay: int = 15):
        return WebDriverWait(self.driver, delay, ignored_exceptions=self.ignored_exceptions).until(
            ec.presence_of_all_elements_located((tag, name)))

    def login(self, _user, _password):
        # Give browser time to load
        self.driver.maximize_window()
        self.driver.get(os.getenv("url") + "/login")
        # time.sleep(10)
        user = self.locate_element(By.ID, 'username')
        password = self.locate_element(By.ID, 'password')
        user.send_keys(_user)
        password.send_keys(_password)

        while True:
            try:
                submit = self.locate_element(By.TAG_NAME, 'button')
                submit.click()
                break
            except ElementClickInterceptedException:
                print('Not clickable')
                pass

        send_remit = self.locate_element(By.CSS_SELECTOR, 'a.MuiMenuItem-root[data-testid="remittance_send-menu-item"]')
        send_remit.click()

    def test_login(self):
        # Logged on first step
        self.login(os.getenv("user"), os.getenv("password"))
        mui_active = self.locate_elements(By.CLASS_NAME, "Mui-active")[1]
        self.assertEquals(mui_active.get_attribute("innerText"), "Amount & Delivery Method")
        self.driver.quit()

    def test_fields_check(self):
        self.login(os.getenv("user"), os.getenv("password"))
        check_result = True
        # 4 fields should be found for sending remittance
        try:
            self.locate_element(By.ID, "sender_amount")
            self.locate_elements(By.ID, "country-select-demo")
            self.locate_element(By.ID, "recipient_amount")
        except NoSuchElementException:
            check_result = False

        self.assertTrue(check_result)
        self.driver.quit()

    def test_check_inputs(self):
        self.login(os.getenv("user"), os.getenv("password"))
        # Sender amount should not be more than 9 digits
        # Sender amount should be only digits not string
        amount = 1000000
        sender_amount = self.locate_element(By.ID, "sender_amount")
        sender_amount.send_keys(amount)
        sender_sends = self.locate_element(By.XPATH, "/html/body/div[1]/div/div/div/main/div[2]/div[2]/form/div[1]/div[2]/div/div[4]/div[2]/h6")
        sender_sends_amount = sender_sends.get_attribute("innerText").replace(" XAF", "").replace(",", "")
        self.assertEquals(int(sender_sends_amount), amount)
        receiving_country = self.locate_elements(By.ID, "country-select-demo")[1]

        # Couldn't finish all the test cases in time :-(
        self.driver.quit()


if __name__ == "__main__":
    unittest.main(testRunner=HtmlTestRunner.HTMLTestRunner(output='reports'))
    # unittest.main()
