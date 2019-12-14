import time
import selenium.common
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from utils import log


class Driver:
    def __init__(self):
        """ Creates chromedriver with options for the object. """
        log(f"Starting web driver")
        # Setup chrome options
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')

        # Remove unwanted logs
        chrome_options.add_argument("--log-level=3")
        self.driver = webdriver.Chrome(chrome_options = chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        log(f"Web driver started")

    def get(self, url):
        """ Loads a given url with the chromedriver. """
        self.driver.get(url)

    def get_html(self, url = None):
        """ Gets the page source of a given url. """
        if url is not None:
            self.driver.get(url)

        return self.driver.page_source

    def send_keys(self, selector, keys):
        """ Sends keys to a given element.

        :selector: the css selector to get the target element.
        :keys: The keys to be sent to the target element. """
        element = self.find_element(selector)
        element.send_keys(keys)

    def find_element(self, css_selector: str, wait: bool = True):
        """ Finds a single element on a webpage using a css selector.

        :param wait: Wether or not to wait for the element to load in.
        :param css_selector: The css selector to locate the target element.
        :return: Single html element that matches the provided css selector.
        """
        if wait:
            self.wait_for(css_selector)
        return self.driver.find_element_by_css_selector(css_selector)

    def find_elements(self, css_selector):
        """ Finds all elements on a webpage that match a given css selector.

        :param css_selector: The css selector to locate the target elements.
        :return: All html elements that match the provided css selector.
        """
        self.wait_for(css_selector)
        return self.driver.find_elements_by_css_selector(css_selector)

    def click(self, css_selector, log_click_error: bool = True):
        """ Sends a click event to the target element using a css selector.

        :param css_selector: The css selector to locate the target element.
        :param log_click_error: Whether or not to log when a click fails.
        """
        try:
            self.wait.until(ec.element_to_be_clickable((By.CSS_SELECTOR, css_selector)))
            ele = self.find_element(css_selector)

            attempts = 0
            while attempts < 5:
                try:
                    attempts += 1
                    ele.click()
                except WebDriverException:
                    time.sleep(1)
                    continue
                break

        except TimeoutException:
            if log_click_error:
                log(f"Failed to click element. {css_selector}")

    def wait_for(self, css_selector: str) -> bool:
        """ Waits for an element to be loaded or become visible on the webpage.

        :param css_selector: The css selector to locate the target element.
        """
        try:
            self.wait.until(ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector)))
            return True
        except selenium.common.exceptions.TimeoutException:
            return False

    def element_exists(self, css_selector, wait: bool = True) -> bool:
        """ Checks to see if the element is visible on the webpage.

        :param wait: Whether or not to wait for the element to load in.
        :param css_selector: The css selector to locate the target element.
        """
        try:
            self.find_element(css_selector, wait)
            return True
        except selenium.common.exceptions.TimeoutException and selenium.common.exceptions.NoSuchElementException:
            return False

    def accept_privacy_notices(self):
        notice_clicked = False

        while not notice_clicked:
            log("Checking for notices")
            # Larger privacy notice
            if notice_clicked := self.element_exists('.details_save--1ja7w', False):
                self.click('.details_save--1ja7w', False)

            # Click the medium privacy notice
            elif notice_clicked := self.element_exists('.intro_acceptAll--23PPA', False):
                self.click('.intro_acceptAll--23PPA', False)

            # First small privacy notice
            elif notice_clicked := self.element_exists('button', False):
                self.click('button', False)

            else:
                # No notices were found
                notice_clicked = True
            log("Notices done")

    def login_myanimelist(self, mal_username: str, mal_password: str):
        if self.logged_in(wait = False):
            return

        for i in range(1, 6):
            log(f"Logging into MyAnimeList attempt: {i}")
            self.get(f"https://myanimelist.net/login.php?from=%2F")
            self.accept_privacy_notices()
            # Enter login information
            self.send_keys('#loginUserName', mal_username)
            self.send_keys('#login-password', mal_password)
            self.click('.pt16 .btn-form-submit')  # Click login button

            if self.logged_in():
                log(f"Logged in successfully as user {mal_username}")
                break

    def logged_in(self, wait: bool = True) -> bool:
        log("Checking if login was successful")
        return self.element_exists(".header-profile-link", wait)

    def load_anime_page(self, mal_id: str) -> bool:
        log("Loading anime page")
        self.get(f"https://myanimelist.net/anime/{mal_id}")
        self.accept_privacy_notices()

        log("Checking if page loaded")
        return self.element_exists('.js-scrollfix-bottom .ac')

    def add_to_list(self):
        # Click the add to list button if it exists
        if self.element_exists('#showAddtolistAnime', wait = False):
            self.click('#showAddtolistAnime')

    def select_watch_status(self, watch_status: str):
        status_conversion = {'watching'     : 1,
                             'completed'    : 2,
                             'on hold'      : 3,
                             'dropped'      : 4,
                             'plan to watch': 6}
        # Click the watched status
        self.click(f"#myinfo_status > option:nth-child({status_conversion.get(watch_status)})")

    def enter_episodes_seen(self, watched_episodes: str):
        # Enter episodes seen
        self.send_keys('#myinfo_watchedeps', [Keys.CONTROL, 'a'])
        self.send_keys('#myinfo_watchedeps', watched_episodes)

    def confirm_update(self):
        # Click add or update
        if self.element_exists('.js-anime-add-button'):
            self.click('.js-anime-add-button')
        else:
            self.click('.js-anime-update-button')

    def quit(self):
        """ Close the driver. """
        self.driver.quit()
