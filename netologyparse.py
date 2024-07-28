import time
import json
import os
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains


def initselenium():
    path = os.getcwd()
    s = Service(rf'{path}\chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=s)
    return driver


def openbrowser(driver):
    driver.get('https://spb.hh.ru/search/vacancy?text=python+django+flask&salary=&ored_clusters=true&area=1&area=2'
               '&hhtmFrom=vacancy_search_list&hhtmFromLabel=vacancy_search_line')


def scrolldown(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def searchitems(driver, jsondict=None):
    vacancy_class_name = 'vacancy-name'
    salary_class_name = 'compensation-text'
    company_class_name = 'company-info-text'
    city_class_name = 'vacancy-serp__vacancy-address'
    link_class_name = 'bloko-link'
    vacancies = driver.find_elements(By.XPATH, f"//*[contains(@class, '{vacancy_class_name}')]")
    salaries = driver.find_elements(By.XPATH, f"//*[contains(@class, '{salary_class_name}')]")
    companies = driver.find_elements(By.XPATH, f"//*[contains(@class, '{company_class_name}')]")
    cities = driver.find_elements(By.XPATH, f"//*[contains(@data-qa, '{city_class_name}')]")
    links = driver.find_elements(By.XPATH, f"//*[contains(@class, '{link_class_name}')]")

    citiesitog = []
    for city in cities:
        if city.text != '':
            citiesitog.append(city.text)

    links1 = []
    for element in links:
        if element.get_attribute('href') is not None:
            if 'https://spb.hh.ru/vacancy/' in element.get_attribute('href'):
                links1.append(element.get_attribute('href'))

    salaries1 = []
    for salary in salaries:
        if salary.text != '':
            salaries1.append(salary.text)

    for city, vacancy, salary, company, link in zip(citiesitog, vacancies, salaries, companies, links1):
        print(f'Город:{city}, Вакансия: {vacancy.text},'
              f' Зарплата: {salary.text}, Компания: {company.text}, Ссылка: {link}')
        jsondict[vacancy.text] = {'Город': city, 'Зарплата': salary.text.replace(u"\u202F", " "),
                                  'Компания': company.text, 'Ссылка': link}

    return jsondict


def nextpage(driver):
    nextpage_class = 'pager-next'
    try:
        dalshe = driver.find_element(By.XPATH, f"//*[contains(@data-qa, '{nextpage_class}')]")
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(dalshe))
        button.click()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Кнопка не найдена: {e}")
        return False


def write_to_json(jsondict):
    with open('vacansies.json', 'w', encoding='utf-8') as file:
        json.dump(jsondict, file, indent=4, ensure_ascii=False)


def main():
    driver = initselenium()
    openbrowser(driver)
    dictj = {}
    a = True
    while a:
        time.sleep(3)
        scrolldown(driver)
        time.sleep(3)
        result = searchitems(driver, dictj)
        time.sleep(10)
        dictj.update(result)
        a = nextpage(driver)
    else:
        write_to_json(dictj)


if __name__ == '__main__':
    main()
