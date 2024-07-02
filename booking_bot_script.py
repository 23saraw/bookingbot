#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
import time
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
import sys

def extract_month_from_input_date(date_str):
    return datetime.strptime(date_str, "%a, %b %d, %Y").month

def find_element_with_retry(driver, by, value, retries=3):
    for attempt in range(retries):
        try:
            element = WebDriverWait(driver, 20).until(EC.element_to_be_clickable((by, value)))
            return element
        except StaleElementReferenceException:
            if attempt < retries - 1:
                time.sleep(0.5)  # wait a bit before retrying
                continue
            else:
                raise

#check for court availability
def wait_for_specific_reservation_to_be_available(driver, desired_court, desired_time, max_wait_minutes=2):
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60

    while True:
        try:
            # Construct a specific XPath expression for the desired court and time
            specific_xpath = f"//div[contains(@aria-label, 'Available') and contains(@aria-label, '{desired_court} Tennis Court {desired_time}') and @role='gridcell']"
            court = driver.find_element(By.XPATH, specific_xpath)
            return court
        except NoSuchElementException:
            pass

        elapsed_time = time.time() - start_time
        if elapsed_time > max_wait_seconds:
            print("Timed out waiting for reservations to become available.")
            return None
        
        print(f"Waiting for court {desired_court} at {desired_time} to become available...")
        time.sleep(1)  # short sleep time

#when to run program
target_time = datetime.strptime('08:00:00', '%H:%M:%S').time()

#run code at target_time
def wait_until(target_time):
    target_datetime = datetime.combine(datetime.today(), target_time)

    while True:
        current_time = datetime.now()
        time_diff = (target_datetime - current_time).total_seconds()

        if time_diff <= 0.001:
            break
        elif time_diff <= 0.01:
            time.sleep(0.001)
        elif time_diff <= 0.1:
            time.sleep(0.01)
        elif time_diff <= 5:
            time.sleep(0.1)
        else:
            time.sleep(1)
#if reservation cannot be in the past button comes up
def reservation_in_the_past():
    try:
        # wait for the modal header to be present
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//header[@class='modal-header']/h3[@class='modal-title' and text()='The reservation date cannot be in the past.']")))
        
        try:
            # try to find the OK button
            ok_button = driver.find_element(By.XPATH, "//button[@data-qa-id='quick-reservation-ok-button']")
            # click the OK button
            ok_button.click()
        except NoSuchElementException:
            print("OK button not found, moving on")
        
    except TimeoutException:
        print("Modal header not found, moving on")



if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python your_script.py <desired_time> <desired_court>")
        sys.exit(1)
    
    desired_time = sys.argv[1]
    desired_court = sys.argv[2]

    service = Service(executable_path="/Users/sarawan/booking_bot/chromedriver")
    driver = webdriver.Chrome(service=service)

    #put inputs
    #desired_date = input("Enter the desired date(e.g., Sun, Jun 23, 2024)")
    # desired_time = input("Enter the desired time (e.g., 11:00 AM): ")
    # desired_court = input("Enter the desired court number (e.g., 3): ")

    #sign in url
    driver.get("https://anc.apm.activecommunities.com/cupertino/reservation/landing?locale=en-US")

    #sign in
    wait = WebDriverWait(driver, 20)
    sign_in = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Sign In']")))
    sign_in.click()
    email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Enter your Email address']")))
    email_input.send_keys("bin_wan@yahoo.com")
    password_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
    password_input.send_keys("benjamin1966")
    sign_in_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@type='submit' and contains(., 'Sign in')]")))
    sign_in_button.click()

    #wait for page to load
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-bar__outer-box")))
    #click into reservatioins page
    max_retries = 2
    for i in range(max_retries):
        # locate parent element of "Reservations" span
        reservations_parent = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Reservations']/..")))

        # use javascript to click properly
        driver.execute_script("arguments[0].click();", reservations_parent)

        # wait for next page to load completely
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

    #click into 90 min. tennis courts page
    tennis_court_link = wait.until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Sports Center 90 min. Tennis Courts']/parent::a")))
    driver.execute_script("arguments[0].click();", tennis_court_link)
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-bar__outer-box")))

    #if reservation cannot be in the past page comes up
    reservation_in_the_past()

    #find the date one week ahead
    date_picker = wait.until(EC.element_to_be_clickable((By.XPATH, "//input[@aria-label='Date picker, current date']")))
    current_date = date.today()
    #desired date: one week ahead
    one_week_ahead = current_date + timedelta(weeks=1) 
    #one_week_ahead = current_date + relativedelta(months=1) 

    one_week_ahead_str = one_week_ahead.strftime("%b %-d, %Y") if one_week_ahead.day < 10 else one_week_ahead.strftime("%b %d, %Y")
    one_week_ahead_xpath = f"//div[@aria-label='{one_week_ahead_str}']"


    #put in event name: "tennis court"
    event_name_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@data-qa-id='quick-reservation-eventType-name']")))
    event_name_input.send_keys("tennis court")

    #select the date
    date_picker.click()

    current_date_value = date_picker.get_attribute("value")
    current_date_month = extract_month_from_input_date(current_date_value)

    # If the month is different, click the next month arrow
    if current_date_month != one_week_ahead.month:
        next_month_arrow = driver.find_element(By.XPATH, "//i[@class='icon icon-chevron-right' and @aria-label='Switch calendar to next month right arrow']")
        driver.execute_script("arguments[0].click();", next_month_arrow)
    # new_month = wait.until(EC.presence_of_element_located((By.XPATH, one_week_ahead_xpath)))

    one_week_ahead_date = wait.until(EC.element_to_be_clickable((By.XPATH, one_week_ahead_xpath)))
    driver.execute_script("arguments[0].click();", one_week_ahead_date)

    #load the new date's court availability8
    wait.until(EC.invisibility_of_element_located((By.CLASS_NAME, "loading-bar__outer-box")))


    desired_court_element = wait_for_specific_reservation_to_be_available(driver, desired_court, desired_time)

    #click earliest court
    if desired_court_element:

        driver.execute_script("arguments[0].click();", desired_court_element)
        confirm_bookings_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-qa-id='quick-reservation-ok-button']")))

        #click at 8am: GO GO GO!!
        wait_until(target_time)
        confirm_bookings_button.click()


        reserve_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-qa-id='quick-reservation-reserve-button']")))
        reserve_button.click()

        print(f"Reserve button clicked.")

        # clear_all_bookings_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[@data-qa-id='quick-reservation-clear-all-bookings-button']")))
        # driver.execute_script("arguments[0].click();", clear_all_bookings_button)
    else:
        print(f"No available courts found for court {desired_court} at {desired_time}.")

    # Pause to observe the actions (you can adjust the time as needed)
    time.sleep(20)

    # Close the browser
    driver.quit()