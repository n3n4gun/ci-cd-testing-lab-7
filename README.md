# Лабораторная работа №7: Простой CI/CD пайплайн

## Описание проекта
Автоматизированные тесты для проверки функциональности формы поиска на сайте Яндекс (https://ya.ru)
с использованием Selenium WebDriver, паттерна Page Object Model, параллельного запуска
(pytest-xdist) и системы отчетности Allure.

## Технологический стек
- Python 3.8+
- Selenium WebDriver
- pytest
- pytest-xdist (параллельный запуск)
- Allure Framework (allure-pytest)
- webdriver-manager
- Page Object Pattern

## Структура проекта
```
lab6_automation/
├── pages/
│   ├── __init__.py
│   └── yandex_form_page.py   # Page Object формы поиска Яндекс
├── tests/
│   ├── __init__.py
│   └── test_yandex_form.py   # Тестовые сценарии
├── conftest.py               # Фикстуры pytest, скриншоты для Allure
├── pytest.ini                # Конфигурация pytest и маркеры
├── requirements.txt          # Зависимости проекта
└── README.md
```

## Тестовые сценарии
| Тест | Маркеры | Что проверяет |
|------|---------|---------------|
| `test_yandex_search_functionality` (3 набора параметров) | `ui`, `regression` | Ввод запроса, появление подсказок, нажатие «Найти», наличие ожидаемого слова в первых результатах выдачи |
| `test_suggest_display` | `ui`, `smoke` | Появление и непустой список подсказок при вводе текста |
| `test_search_input_clear` | `ui`, `smoke` | Ввод текста в поисковую строку и ее очистку |

Всего 5 тестов.

## Установка

1. Установите [Python 3.8+](https://www.python.org/downloads/) и браузер Google Chrome.
2. Создайте виртуальное окружение и установите зависимости:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux / macOS
   source .venv/bin/activate

   pip install -r requirements.txt
   ```
3. Установите Allure (нужна Java 8+):
   ```bash
   # Windows (через Chocolatey или Scoop)
   choco install allure
   scoop install allure
   # macOS
   brew install allure
   # Linux
   sdk install allure
   ```

ChromeDriver подбирается автоматически через `webdriver-manager`; если он не сработает,
используется встроенный в Selenium механизм Selenium Manager.

## Запуск тестов
Все команды выполняются из папки `lab6_automation`.

```bash
# Обычный запуск
pytest tests/test_yandex_form.py -v

# Параллельный запуск (2 потока)
pytest tests/test_yandex_form.py -n 2 -v

# Запуск без окна браузера
pytest tests/test_yandex_form.py -v --headless

# Запуск только smoke-тестов
pytest -m smoke -v

# Запуск с генерацией Allure-результатов
pytest tests/test_yandex_form.py --alluredir=allure-results -v

# Параллельно и с Allure
pytest tests/test_yandex_form.py -n 2 --alluredir=allure-results -v
```

### Дополнительные параметры
| Параметр | По умолчанию | Описание |
|----------|--------------|----------|
| `--headless` | выключен | Запуск Chrome без графического интерфейса |
| `--captcha-timeout N` | `60` | Сколько секунд ждать, пока капча будет пройдена вручную в окне браузера |

## Allure-отчет
```bash
# Создать и сразу открыть отчет
allure serve allure-results

# Сгенерировать статический отчет в папку allure-report
allure generate allure-results -o allure-report --clean
allure open allure-report
```

В отчет автоматически прикладываются:
- скриншот финального состояния страницы для каждого теста;
- скриншот и HTML страницы при падении теста;
- список заголовков результатов поиска и список подсказок.

## Особенности и отличия от шаблона из задания
- **Локаторы обновлены** под текущую верстку ya.ru: CSS-селекторы с несколькими вариантами
  (поисковая строка ya.ru сейчас является элементом `<textarea id="text">`, а не `<input>`,
  поэтому локатор из шаблона `By.ID`/`input` ее не находит), чтобы тесты не ломались при небольших изменениях страницы.
- **Проверка результатов**: ожидаемое слово ищется в заголовках первых 5 результатов, а не
  только в первом — первым результатом бывает реклама или колдунщик. Учитываются только
  органические результаты (`.OrganicTitle-LinkText`): блок «Быстрый ответ Алисы AI»
  содержит скрытый заголовок, из-за которого ожидание видимости падало по таймауту.
- **Капча**: при большом количестве запросов Яндекс может показать капчу. В обычном режиме тест
  ждет `--captcha-timeout` секунд, чтобы ее можно было пройти вручную; если капча не пройдена
  (например, в `--headless`), тест помечается как пропущенный (`skipped`), а не упавший.
- Версии в `requirements.txt` обновлены до более новых, чем в шаблоне, для совместимости
  с актуальными Chrome и pytest.

## Результаты выполнения
Результаты Allure сохраняются в папку `allure-results`, отчет — в `allure-report`.
Скриншоты выполнения тестов и Allure-отчета приложены к отчету по лабораторной работе.
