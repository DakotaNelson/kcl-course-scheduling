import os
import pickle

from time import sleep

import dataset

from BeautifulSoup import BeautifulSoup

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.action_chains import ActionChains

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def fill_course_form(module_code):
    department = module_code[1:4]
    # this works for all departments except CTEL

    # select the correct department
    department_dropdown = Select(driver.find_element_by_name("dlFilter"))
    search_string = '(' + department + ')'
    for option in department_dropdown.options:
        if search_string in option.text:
            option.click()
            break

    # select the right module
    module_dropdown = Select(driver.find_element_by_name("dlObject"))
    module_dropdown.deselect_all()
    for option in module_dropdown.options:
        if module_code in option.text:
            option.click()
            break

    # get a list view, not grid schedule view
    driver.find_element_by_id("RadioType_1").click()

    # submit the form
    submit = driver.find_element_by_name("bGetTimetable")
    submit.click()

def get_course_timetable():
    try:
        driver.find_element_by_id("tErrorTable")
        print(bcolors.FAIL + "[!] Error finding data" + bcolors.ENDC)
    except:
        pass
    class_title_html = driver.find_element_by_css_selector('td b')
    bs = BeautifulSoup(class_title_html.get_attribute('innerHTML'))
    class_title = bs.text.replace("&nbsp;", " ")[8:]
    module_code = class_title.split(" ")[0]
    class_data = {'code': module_code, 'title': class_title, 'times': []}

    class_times = driver.find_elements_by_css_selector('body table:not(:first-child) tr')
    for element in class_times:
        row = element.get_attribute('innerHTML')
        bs = BeautifulSoup(row)
        tds = bs.findAll('td')
        days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
        if tds[0].text not in days:
            continue
        data = {
            "day": tds[0].text,
            "start_time": tds[1].text,
            "end_time": tds[2].text,
            "activity": tds[3].text,
            "type": tds[5].text,
            "room": tds[6].text
        }
        class_data['times'].append(data)

    return class_data

######################################################

#db = dataset.connect('sqlite:///:memory:')
db = dataset.connect('sqlite:///schedule.db')
events_table = db['events']
courses_table = db['courses']

chrome_options = Options()
# timeout after 1 second
chrome_options.add_argument('--timeout 1000')

driver = webdriver.Chrome(chrome_options=chrome_options)
driver.set_page_load_timeout(5)

driver.get("https://timetables.kcl.ac.uk")

# give the user time to log in
element = WebDriverWait(driver, 120).until(
    EC.presence_of_element_located((By.ID, "LinkBtn_module"))
)

# navigate to the "view module timetable" form
element.click()

# get data for each course
with open("course_codes.txt", 'r') as f:
    for line in f.readlines():
        print(line.strip())
        try:
            fill_course_form(line.strip())
            sleep(1)
        except TimeoutException:
            pass

        # switch to the new tab
        driver.switch_to_window(driver.window_handles[-1])

        course_data = get_course_timetable()

        to_insert = {'code': course_data['code'], 'title': course_data['title']}
        courses_table.insert(to_insert)
        for event in course_data['times']:
            event['course_code'] = course_data['code']
            events_table.insert(event)

        # close our tab and switch back to the primary tab
        driver.close()
        driver.switch_to_window(driver.window_handles[0])

driver.quit()
