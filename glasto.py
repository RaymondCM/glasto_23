# simple python script to open multiple glasto proxy pages and wait for input if you're on the registration page
import time
import threading

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.firefox.options import Options

try:
    import chrome_driver
except ImportError:
    from . import chrome_driver


# Negative matching may be a better default because we do not know the page source ahead of time
def worker(opts, proxy, caps, negative_matching=True):
    url = "https://glastonbury.seetickets.com/content/extras"

    # Either look for a phrase that determines you're on the booking page
    matching_phrases = ["buy", "register"]
    # Or look for a phrase that determines you're not on the waiting page
    if negative_matching:
        matching_phrases = ["You will be held at this page"]

    # Proxy all browser sessions so the max is 2*N_Proxies
    opts.add_argument('--incognito')
    opts.add_argument('--proxy-server={}'.format(proxy))
    driver = webdriver.Chrome(chrome_options=opts, desired_capabilities=caps)

    while True:
        try:
            driver.get(url)
            current_site = driver.page_source
            if negative_matching and any([phrase not in current_site for phrase in matching_phrases]):
                print("Negative match not found!")
                break
            else:
                matches = [x for x in matching_phrases if (x in current_site and not negative_matching)]
                if len(matches):
                    print("Match found for {}: {}".format(proxy, ', '.join(matches)))
                    break
            print("Refreshing {}".format(url))
            time.sleep(2)
        except Exception as e:
            print("Skipping Error: {}".format(e))
            continue

    print("Page Loaded")
    while True:
        print("Fill in your details!")
        time.sleep(10)


def main():
    options = Options()
    options.add_argument(
       "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36"
    )
    capabilities = DesiredCapabilities().CHROME
    capabilities["pageLoadStrategy"] = "none"

    chrome_driver.install()

    max_clients = 2
    proxy_list = ["8.8.8.8", "1.1.1.1", "76.76.2.0", "9.9.9.9", "208.67.222.222"]
    threading_engine = threading.Thread

    for _ in range(max_clients):
        for proxy in proxy_list:
            t = threading_engine(target=worker, args=(options, proxy, capabilities))
            t.start()
            time.sleep(1)
        time.sleep(2)

    try:
        while True:
            print("Waiting for tickets")
            time.sleep(100)
    except KeyboardInterrupt:
        print("Exiting")


if __name__ == '__main__':
    main()
