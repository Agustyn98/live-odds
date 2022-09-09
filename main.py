from selenium.webdriver.common.by import By
import undetected_chromedriver.v2 as uc
from avro.io import DatumWriter
import avro
import io
import json
from google.api_core.exceptions import NotFound
from google.cloud.pubsub import PublisherClient
from google.pubsub_v1.types import Encoding
import datetime
from time import sleep


project_id = "marine-bison-360321"
topic_id = "match_bets"
avsc_file = "schema_avro.json"

TEAM = "strongest"
TIME_WINDOW = 11  # Seconds
INTERVAL = int(7200 / TIME_WINDOW)
ERRORS = 0
MAX_ERRORS = 4
driver = uc.Chrome()
driver.maximize_window()


def publish(record):
    publisher_client = PublisherClient()
    topic_path = publisher_client.topic_path(project_id, topic_id)

    # Prepare to write Avro records to the binary output stream.
    avro_schema = avro.schema.parse(open(avsc_file, "rb").read())
    writer = DatumWriter(avro_schema)
    bout = io.BytesIO()

    try:
        # Get the topic encoding type.
        topic = publisher_client.get_topic(request={"topic": topic_path})
        encoding = topic.schema_settings.encoding

        # Encode the data
        if encoding == Encoding.JSON:
            data_str = json.dumps(record)
            print(f"Preparing a JSON-encoded message:\n{data_str}")
            data = data_str.encode("utf-8")
        else:
            print(f"No encoding specified in {topic_path}. Abort.")
            exit(0)

        future = publisher_client.publish(topic_path, data)
        print(f"Published message ID: {future.result()}")

    except NotFound:
        print(f"{topic_id} not found.")


def _assert_data(data):
    # Check if scraped values are correct
    for i in range(-5, 0, 1):
        number = data[i].split(".")
        if not number[0].isnumeric():
            return False

    return True


def assert_data(data):
    global ERRORS
    if not _assert_data(data):
        ERRORS += 1
        print(f"Number of errors: {ERRORS}")
        if ERRORS >= MAX_ERRORS:
            print(f"Scraping failed {MAX_ERRORS} times...")
            exit(0)
        else:
            return False

    ERRORS = 0
    return True


def extract_data(data):
    results = {}
    results["team1"] = data[0]
    results["team2"] = data[1]
    results["time"] = data[2]
    results["team1_score"] = int(data[-5])
    results["team2_score"] = int(data[-4])
    results["team1_odds"] = float(data[-3])
    results["draw_odds"] = float(data[-2])
    results["team2_odds"] = float(data[-1])
    results["datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return results


def get_bet365():
    link = "https://www.bet365.com/#/IP/B1"
    link = r"file:///home/agus/Desktop/bet365%20-%20Apuestas%20deportivas%20en%20la%20red.html"
    driver.get(link)
    sleep(3)
    try:
        startup_message = driver.find_element(
            By.CLASS_NAME, "iip-IntroductoryPopup_Cross"
        )
        startup_message.click()
    except Exception:
        print("No sign-in message")

    for _ in range(INTERVAL):
        # Find all boxes that contain a match info
        match_rectangle = driver.find_elements(By.CLASS_NAME, "ovm-Fixture_Container")
        for e in match_rectangle:
            if TEAM.lower() in e.text.lower():
                print(f"Extracted data:\n{e.text}")

                raw_data = e.text.strip().split("\n")
                if not assert_data(raw_data):
                    sleep(TIME_WINDOW)
                    break

                data = extract_data(raw_data)
                #publish(data)
                print(f"PUBLISHING DATA \n{data}")
                sleep(TIME_WINDOW)
                break


if __name__ == "__main__":
    get_bet365()
