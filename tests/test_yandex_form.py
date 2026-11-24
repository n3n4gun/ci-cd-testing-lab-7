import allure
import pytest

from pages.yandex_form_page import CaptchaError, YandexFormPage

# Сколько первых результатов выдачи проверяем на наличие ожидаемого текста
TOP_RESULTS = 5


@allure.epic("Лабораторная работа №6")
@allure.feature("Форма поиска Яндекс")
@allure.suite("Тестирование поиска Яндекс")
@pytest.mark.ui
class TestYandexSearch:

    @allure.title("Тест поиска и проверки результатов: {search_query}")
    @allure.description("Этот тест проверяет функциональность поиска на Яндекс")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.regression
    @pytest.mark.parametrize("search_query,expected_text", [
        ("Selenium WebDriver", "Selenium"),
        ("Python автоматизация тестирования", "Python"),
        ("Тестирование программного обеспечения", "тестирование"),
    ])
    def test_yandex_search_functionality(self, browser, base_url, captcha_timeout,
                                         search_query, expected_text):
        with allure.step("Открыть главную страницу Яндекс"):
            form_page = YandexFormPage(browser)
            form_page.open_page(base_url)

        with allure.step(f"Выполнить поиск запроса: {search_query}"):
            try:
                form_page.perform_search(search_query, captcha_timeout)
            except CaptchaError as error:
                pytest.skip(str(error))

        with allure.step("Проверить наличие результатов поиска"):
            titles = form_page.get_results_titles()
            allure.attach("\n".join(titles), name="Заголовки результатов",
                          attachment_type=allure.attachment_type.TEXT)
            first_result = form_page.get_first_result_text()
            assert first_result is not None, "Результаты поиска не отобразились"

        with allure.step(f"Проверить, что в первых {TOP_RESULTS} результатах есть '{expected_text}'"):
            top = [title.lower() for title in titles[:TOP_RESULTS]]
            assert any(expected_text.lower() in title for title in top), \
                f"Ожидаемый текст '{expected_text}' не найден в результатах: {titles[:TOP_RESULTS]}"

    @allure.title("Тест отображения подсказок при вводе")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.smoke
    def test_suggest_display(self, browser, base_url):
        with allure.step("Открыть главную страницу Яндекс"):
            form_page = YandexFormPage(browser)
            form_page.open_page(base_url)

        with allure.step("Ввести текст в поисковую строку"):
            form_page.enter_search_text("автоматизация тестирования")

        with allure.step("Проверить отображение подсказок"):
            # Метод wait_for_suggest выбросит исключение если подсказки не появятся
            form_page.wait_for_suggest()
            suggests = form_page.get_suggest_items()
            allure.attach("\n".join(suggests), name="Подсказки",
                          attachment_type=allure.attachment_type.TEXT)
            assert suggests, "Список подсказок пуст"

    @allure.title("Тест очистки поисковой строки")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.smoke
    def test_search_input_clear(self, browser, base_url):
        with allure.step("Открыть главную страницу Яндекс"):
            form_page = YandexFormPage(browser)
            form_page.open_page(base_url)

        with allure.step("Ввести текст в поисковую строку"):
            form_page.enter_search_text("текст для очистки")
            assert form_page.get_search_input_value() == "текст для очистки"

        with allure.step("Очистить поле"):
            form_page.clear_search_input()
            value_after_clear = form_page.get_search_input_value()

        with allure.step("Проверить что поле очищено"):
            assert value_after_clear == '', f"Поле не очищено, значение: '{value_after_clear}'"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
