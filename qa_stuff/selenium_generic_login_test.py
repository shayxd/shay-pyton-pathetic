import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

class SeleniumGenericLoginTest:
    def __init__(self, driver_path, url, username, password):
        self.driver = webdriver.Chrome(driver_path)
        self.url = url
        self.username = username
        self.password = password

    def login(self):
        self.driver.get(self.url)
        time.sleep(2)  # wait for the page to load

        username_field = self.driver.find_element(By.NAME, 'username')
        password_field = self.driver.find_element(By.NAME, 'password')

        username_field.send_keys(self.username)
        password_field.send_keys(self.password)
        password_field.send_keys(Keys.RETURN)

        time.sleep(2)  # wait for login to complete

    def close(self):
        self.driver.quit()