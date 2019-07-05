import selenium.common
from colorama import Fore
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

from config import CHROMEDRIVER_PATH, MAL_USERNAME, MAL_PASSWORD
from utils import log


class Driver:
    def __init__(self):
        """ Creates chromedriver with options for the object. """
        log(f"Starting web driver", Fore.CYAN)
        # Setup chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

        # Remove unwanted logs
        chrome_options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(chrome_options = chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        log(f"Web driver started", Fore.GREEN)

    def get(self, url):
        """ Loads a given url with the chromedriver. """
        self.driver.get(url)

    def get_html(self, url):
        """ Gets the page source of a given url. """
        self.get(url)
        return self.driver.page_source

    def send_keys(self, selector, keys):
        """ Sends keys to a given element.

        :selector: the css selector to get the target element.
        :keys: The keys to be sent to the target element. """
        element = self.find_element(selector)
        element.send_keys(keys)

    def find_element(self, css_selector):
        """ Finds a single element on a webpage using a css selector.

        :param css_selector: The css selector to locate the target element.
        :return: Single html element that matches the provided css selector.
        """
        self.wait_for(css_selector)
        return self.driver.find_element_by_css_selector(css_selector)

    def find_elements(self, css_selector):
        """ Finds all elements on a webpage that match a given css selector.

        :param css_selector: The css selector to locate the target elements.
        :return: All html elements that match the provided css selector.
        """
        self.wait_for(css_selector)
        return self.driver.find_elements_by_css_selector(css_selector)

    def click(self, css_selector):
        """ Sends a click event to the target element using a css selector.

        :param css_selector: The css selector to locate the target element.
        """
        try:
            ele = self.find_element(css_selector)
            self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            ele.click()

        except TimeoutException:
            log("Failing to click element, moving on.")

    def wait_for(self, css_selector):
        """ Waits for an element to be loaded or become visible on the webpage.

        :param css_selector: The css selector to locate the target element.
        """
        self.wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))

    def element_exists(self, css_selector):
        """ Checks to see if the element is visible on the webpage.

        :param css_selector: The css selector to locate the target element.
        """
        try:
            self.driver.find_element_by_css_selector(css_selector)
            return True
        except selenium.common.exceptions.NoSuchElementException:
            return False

    def myanimelist_login(self):
        """ Loads the myanimelist login page and logs in with users credentials. """
        username, password = MAL_USERNAME, MAL_PASSWORD

        # Load login page
        log("Logging into myanimelist", Fore.CYAN)
        self.get('https://myanimelist.net/login.php?from=%2F')

        # Add cookies to prevent gdpr popups
        self.driver.add_cookie({'name': 'm_gdpr_mdl', 'value': '1'})
        self.driver.add_cookie({'name' : 'euconsent',
                                'value': 'BOjNYfhOjNYfhAnADAENCaAAAAAo1rv___7__9_-____9uz7Ov_v_f__33e87_9v_h_7_-___u_-3zd4u_1vf99yfm1-7ctr3tp_87uesm_Xur__59__3z3_9phPr8k89r6337EwwEA'})
        self.driver.add_cookie({'name': 'pubconsent', 'value': 'BOjNYfhOjNYfhAnCaABAAAABAA'})
        # Refresh to apply cookies
        self.driver.refresh()

        # Enter login information
        self.send_keys('#loginUserName', username)
        self.send_keys('#login-password', password)

        self.click('.pt16 .btn-form-submit')  # Click login button
        log(f"Logged in successfully as user {MAL_USERNAME}", Fore.GREEN)

    def quit(self):
        """ Close the driver. """
        self.driver.quit()
