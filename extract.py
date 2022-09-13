import datetime

ERRORS = 0
MAX_ERRORS = 5

def _assert_data(data):
    # Check if scraped values are correct
    for i in range(-5, 0, 1):
        number = data[i].split(".")
        if not number[0].isnumeric():
            return False

    if len(data[2].split(':')) < 2:
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
    #results["datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["datetime"] = int(datetime.datetime.now().strftime("%Y%m%d"))
    return results