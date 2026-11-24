import allure
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from pages.yandex_form_page import YandexFormPage


def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=False,
        help="Запускать Chrome без графического интерфейса",
    )
    parser.addoption(
        "--captcha-timeout",
        action="store",
        type=int,
        default=60,
        help="Сколько секунд ждать ручного прохождения капчи (0 - не ждать)",
    )


def _create_driver(chrome_options):
    """Создать драйвер через webdriver-manager, при ошибке - через Selenium Manager"""
    try:
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=chrome_options)
    except Exception:
        # Selenium >= 4.6 умеет сам подбирать chromedriver под версию браузера
        return webdriver.Chrome(options=chrome_options)


@pytest.fixture
def browser(request):
    # Настройка опций Chrome
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--lang=ru-RU")
    if request.config.getoption("--headless"):
        chrome_options.add_argument("--headless=new")

    # Инициализация драйвера
    driver = _create_driver(chrome_options)

    # Неявное ожидание
    driver.implicitly_wait(10)

    yield driver

    # Скриншот финального состояния страницы для отчета Allure
    try:
        allure.attach(
            driver.get_screenshot_as_png(),
            name="Финальное состояние страницы",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass

    # Закрытие браузера после теста
    driver.quit()


@pytest.fixture
def base_url():
    return "https://ya.ru"


@pytest.fixture
def captcha_timeout(request):
    return request.config.getoption("--captcha-timeout")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """При падении теста прикладывать к Allure скриншот и HTML страницы"""
    outcome = yield
    report = outcome.get_result()
    if report.when in ("setup", "call") and report.failed:
        driver = item.funcargs.get("browser")
        if driver is not None:
            try:
                captcha_shown = YandexFormPage(driver).is_captcha_shown()
            except Exception:
                captcha_shown = False
            if captcha_shown:
                report.outcome = "skipped"
                report.longrepr = (str(item.path), 0, "Skipped: Яндекс запросил капчу")
                return
    if report.when == "call" and report.failed:
        driver = item.funcargs.get("browser")
        if driver is not None:
            allure.attach(
                driver.get_screenshot_as_png(),
                name="Скриншот при падении",
                attachment_type=allure.attachment_type.PNG,
            )
            allure.attach(
                driver.page_source,
                name="HTML страницы",
                attachment_type=allure.attachment_type.HTML,
            )
