import datetime

ERRORS = 0
MAX_ERRORS = 4 
FIRST_HALF = False
SECOND_HALF = False



def _assert_data(data):
    # Check if scraped values are correct
    for i in range(-5, 0, 1):
        number = data[i].split(".")
        if not number[0].isnumeric():
            return False

    if "TE" not in data[2] and "ET" not in data[2] and len(data[2].split(':')) < 2:
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


def extract_time(time1, time2):
    global FIRST_HALF
    global SECOND_HALF

    if "ET" in time1 or "TE" in time1:
        return time2

    if time1 >= "90":
        extra_time = time1.split(':')
        extra_m = int(extra_time[0]) - 90
        extra_s = extra_time[1]
        return f"90:00+{str(extra_m)}:{extra_s}"
    
    if time1 == "45:00" and FIRST_HALF:
        SECOND_HALF = True
        return "45:00HT"

    if time1 >= "45:00" and not SECOND_HALF:
        FIRST_HALF = True
        extra_time = time1.split(':')
        extra_m = int(extra_time[0]) - 45
        extra_s = extra_time[1]
        return f"45:00+{str(extra_m)}:{extra_s}"
    
    return time1


def extract_data(data):
    results = {}
    results["team1"] = data[0]
    results["team2"] = data[1]
    results["time"] = extract_time(data[2], data[3])
    results["team1_score"] = int(data[-5])
    results["team2_score"] = int(data[-4])
    results["team1_odds"] = float(data[-3])
    results["draw_odds"] = float(data[-2])
    results["team2_odds"] = float(data[-1])
    #results["datetime"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results["datetime"] = int(datetime.datetime.now().strftime("%Y%m%d"))
    return results
