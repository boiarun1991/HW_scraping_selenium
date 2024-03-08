import json
from pprint import pprint

from tqdm import tqdm
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By


chrome_path = ChromeDriverManager().install()
browser_service = Service(executable_path=chrome_path)
browser = Chrome(service=browser_service)


def get_vacancy(browser):
    browser.get('https://spb.hh.ru/search/vacancy?text=python&area=1&area=2')
    serp_elements = browser.find_element(By.CLASS_NAME, value='HH-MainContent').\
        find_elements(By.CLASS_NAME, value='serp-item')

    parsed_data = []
    for serp_item in serp_elements:
        vacancy_header = serp_item.find_element(By.CLASS_NAME, value='vacancy-serp-item-body'). \
            find_element(By.TAG_NAME, 'div')
        h3_tag = vacancy_header.find_element(By.TAG_NAME, 'h3')
        a_tag = h3_tag.find_element(By.TAG_NAME, 'a')

        vacancy_link = a_tag.get_attribute('href')
        vacancy_title = h3_tag.text

        vacancy_dict = {
            "vacancy_title": vacancy_title,
            "vacancy_link": vacancy_link}
        parsed_data.append(vacancy_dict)

    result_list = []
    count_vacancies = int(input(f'{len(parsed_data)} vacancies found, how many vacancies to check '
                                f'for compliance with the request?:\n'))
    print('Search vacancies...')
    for vacancy_dict in tqdm(parsed_data[:count_vacancies]):
        link = vacancy_dict["vacancy_link"]
        browser.get(link)
        vacancy_description = browser.find_element(By.CLASS_NAME, value='HH-MainContent'). \
            find_element(By.CLASS_NAME, value='vacancy-description').text.lower().split('\n')

        if 'django' in vacancy_description or 'flask' in vacancy_description:
            get_salary = browser.find_element(By.CLASS_NAME, value='HH-MainContent'). \
                find_element(By.CLASS_NAME, value='vacancy-title')
            salary = get_salary.text.split('\n')
            vacancy_company_title = browser.find_element(By.CLASS_NAME, value='HH-MainContent'). \
                find_element(By.CLASS_NAME, value='vacancy-company-name').text
            company_location = browser.find_element(By.CLASS_NAME, value='HH-MainContent'). \
                find_element(By.CLASS_NAME, value='vacancy-company-redesigned').text.split('\n')[-1]
            result = {
                'vacancy_title': vacancy_dict['vacancy_title'],
                'link': link,
                'company_title': vacancy_company_title,
                'salary': None,
                'company_location': company_location
            }
            if len(salary) > 1:
                result['salary'] = salary[1]
            result_list.append(result)

        else:
            continue
    print(f'{len(result_list)} vacancies found and written down')
    return result_list


def create_json_file(result_list):
    with open('hh_parser.json', 'w', encoding='utf-8') as file:
        json.dump(result_list, file, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    create_json_file(get_vacancy(browser))
