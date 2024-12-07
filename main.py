from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from lxml import html
import json

# Определение запроса
books_to_find = input("Введите запрос для поиска (категория, название, автор и т.д.): ")

# Определение классов и опций
options = Options()
options.add_argument("start-maximized")
driver = webdriver.Chrome(options=options)
action = ActionChains(driver)

# открытие стартовой страницы
driver.get('https://www.litres.ru')
action.pause(5).perform()

# Ввод запроса в строку поиска
search_line = driver.find_element(By.XPATH, "//input[contains(@class, 'SearchForm')]")
search_line.send_keys(books_to_find)
search_line.send_keys(Keys.ENTER)

# Находим чекбокс для выбора текствых книг в найденном
try:
    checkbox_text = driver.find_element(By.XPATH, "//label[@for='art_types-text_book']//div[contains(@class, 'Checkbox_check')]")
    action.scroll_to_element(checkbox_text).move_to_element(checkbox_text).perform()
    checkbox_text.click()
except Exception as e:
    print(f"Чекбокс не выбран, ошибка: {e}")

    action.pause(0.5).perform()
# Находим чекбокс для выбора книг на русском языке
try:
    checkbox_rus = driver.find_element(By.XPATH, "//label[@for='languages-ru']//div[contains(@class, 'Checkbox_fakeCheckbox')]")
    action.scroll_to_element(checkbox_rus).move_to_element(checkbox_rus).perform()
    checkbox_rus.click()
except Exception as e:
    print(f"Чекбокс не выбран, ошибка: {e}")

# Работа с данными
while True:
    # Полученная точка входа и отправка запроса
    url = driver.current_url
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 YaBrowser/24.10.0.0 Safari/537.36'}
    session = requests.session()
    
    # Получение ответа сервера и преобразование в дерево html
    response = session.get(url=url, headers=headers)
    tree = html.fromstring(html=response.content)
    
    # Получение ссылок всех книг на странице
    books =driver.find_elements(By.XPATH, "//div[contains(@class, 'ArtDefault_wrapper')]")
    
    # Получение информации о книгах
    for book in books:
        book_url = book.find_element(By.XPATH, ".//div/a").get_attribute("href")
        response = session.get(url=book_url, headers=headers)
        book_page = html.fromstring(html=response.content)
        title = book_page.xpath("//h1/text()")
        authors = book_page.xpath("//div//a[contains(@class, 'BookAuthor_author__name')]//span/text()")
        price = book_page.xpath("//strong[@data-testid='book-sale-block__discount--art--price']/text()")
        book_info = {"title": title, "authors": authors, "price": price}
        
        # Сохранение информации о книге в файл json
        try:
            with open(f"books_{books_to_find}.json", 'a', encoding='utf-8') as file:
                json.dump(book_info, file, ensure_ascii=False, indent=1)
            print(f"Книга {book_info['title']} успешно сохранена")
        except:
            print(f"Не удалось сохранить книгу {book_info['title']}")

    # Обработка перехода на следующую старницу
    try:
        button_next_page = driver.find_element(By.XPATH, "//button[@data-testid='paginator__nextLabel']")
        action.scroll_to_element(button_next_page).click(button_next_page).perform()
        if url == driver.current_url:
            break
    except:
        break
