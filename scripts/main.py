from selenium.webdriver.common.by import By
import undetected_chromedriver.v2 as uc
from time import sleep
from extract import assert_data, extract_data
from pubsub import publish
import os


#TEAM1 = "strongest"
#TEAM2 = "oriente"
TEAM1 = os.environ["TEAM1"]
TEAM2 = os.environ["TEAM2"]

TIME_WINDOW = 11  # Seconds
INTERVAL = int(7200 / TIME_WINDOW)
driver = uc.Chrome()

link = "https://www.bet365.com/#/IP/B1"
driver.get(link)

def delete_sign_in_msg():
    try:
        startup_message = driver.find_element(
            By.CLASS_NAME, "iip-IntroductoryPopup_Cross"
        )
        startup_message.click()
    except Exception:
        print("No sign-in message") 

def get_bet365():

    sleep(3)
    delete_sign_in_msg()

    for i, _ in enumerate(range(INTERVAL)):
        # Find all boxes that contain a match info
        driver.refresh()
        sleep(5)
        match_rectangle = driver.find_elements(By.CLASS_NAME, "ovm-Fixture_Container")
        for e in match_rectangle:
            if TEAM1.lower() in e.text.lower() and TEAM2.lower() in e.text.lower():
                print(f"Extracted data:\n{e.text}")

                raw_data = e.text.strip().split("\n")
                if not assert_data(raw_data):
                    sleep(TIME_WINDOW)
                    break

                data = extract_data(raw_data)
                publish(data)
                print(f"PUBLISHING DATA \n{data}")
                sleep(TIME_WINDOW)
                break


if __name__ == "__main__":
    get_bet365()
