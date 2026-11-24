import time

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class CaptchaError(Exception):
    """Яндекс показал капчу вместо результатов поиска"""


class YandexFormPage:
    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    # Локаторы элементов формы
    # На ya.ru поисковая строка - это textarea#text (input с тем же классом скрыт)
    SEARCH_INPUT = (By.CSS_SELECTOR, "textarea#text, textarea[name='text'], input#text")
    SUGGEST_LIST = (By.CSS_SELECTOR, ".mini-suggest__popup-content, .mini-suggest__popup")
    SUGGEST_ITEMS = (By.CSS_SELECTOR, ".mini-suggest__item")
    SEARCH_BUTTON = (
        By.CSS_SELECTOR,
        "button.search3__button, button.mini-suggest__button, button[type='submit']",
    )
    SEARCH_RESULTS = (By.CSS_SELECTOR, "#search-result .serp-item")
    # Только органические результаты: у блока "Быстрый ответ Алисы AI" есть скрытый h2
    RESULT_TITLES = (By.CSS_SELECTOR, "#search-result .serp-item .OrganicTitle-LinkText")

    def open_page(self, url):
        """Открыть указанный URL"""
        self.driver.get(url)
        return self

    def enter_search_text(self, text):
        """Ввести текст в поисковую строку"""
        search_input = self.wait.until(EC.element_to_be_clickable(self.SEARCH_INPUT))
        search_input.clear()
        search_input.send_keys(text)
        return self

    def get_search_input_value(self):
        """Получить текущее значение поисковой строки"""
        return self.driver.find_element(*self.SEARCH_INPUT).get_attribute("value")

    def clear_search_input(self):
        """Очистить поисковую строку"""
        search_input = self.driver.find_element(*self.SEARCH_INPUT)
        search_input.clear()
        # clear() не всегда вызывает JS-события, поэтому дополнительно стираем с клавиатуры
        if search_input.get_attribute("value"):
            search_input.send_keys(Keys.CONTROL, "a")
            search_input.send_keys(Keys.DELETE)
        return self

    def wait_for_suggest(self):
        """Дождаться появления списка подсказок"""
        self.wait.until(EC.visibility_of_element_located(self.SUGGEST_LIST))
        return self

    def get_suggest_items(self):
        """Получить тексты подсказок"""
        self.wait.until(EC.visibility_of_element_located(self.SUGGEST_ITEMS))
        items = self.driver.find_elements(*self.SUGGEST_ITEMS)
        return [item.text for item in items if item.text.strip()]

    def click_search_button(self):
        """Нажать кнопку поиска"""
        search_button = self.wait.until(EC.element_to_be_clickable(self.SEARCH_BUTTON))
        search_button.click()
        return self

    def is_captcha_shown(self):
        """Проверить, показал ли Яндекс капчу"""
        url = self.driver.current_url
        return "showcaptcha" in url or "captcha" in url.split("?")[0]

    def wait_for_search_results(self, captcha_timeout=0):
        """Дождаться появления результатов поиска.

        Если Яндекс показал капчу, ждем до captcha_timeout секунд,
        пока пользователь пройдет ее вручную в окне браузера.
        """
        if self.is_captcha_shown():
            deadline = time.time() + captcha_timeout
            while self.is_captcha_shown() and time.time() < deadline:
                time.sleep(1)
            if self.is_captcha_shown():
                raise CaptchaError("Яндекс запросил капчу, результаты поиска недоступны")
        try:
            self.wait.until(EC.visibility_of_element_located(self.SEARCH_RESULTS))
        except TimeoutException:
            if self.is_captcha_shown():
                raise CaptchaError("Яндекс запросил капчу, результаты поиска недоступны")
            raise
        return self

    def get_results_titles(self):
        """Получить заголовки результатов поиска"""
        titles = self.wait.until(EC.visibility_of_any_elements_located(self.RESULT_TITLES))
        return [title.text for title in titles if title.text.strip()]

    def get_first_result_text(self):
        """Получить текст первого результата поиска"""
        titles = self.get_results_titles()
        return titles[0] if titles else None

    def perform_search(self, search_text, captcha_timeout=0):
        """Выполнить полный цикл поиска"""
        (self.enter_search_text(search_text)
         .wait_for_suggest()
         .click_search_button()
         .wait_for_search_results(captcha_timeout))
        return self
