from selenium import webdriver
import os
import shutil
import time
import pandas
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask,request

df = pandas.read_csv("test.csv",index_col=0)

def download_stock_data():
    print("starting download")
    global df
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory":os.getcwd()}
    options.add_experimental_option("prefs",prefs)

    driver = webdriver.Chrome(executable_path='chromedriver.exe',chrome_options=options)
    driver.minimize_window()
    while True:
        try:
            driver.get("https://www.nasdaq.com/market-activity/stocks/screener?exchange=NASDAQ&render=download")

            download_csv = driver.find_element_by_css_selector("body > div.dialog-off-canvas-main-canvas > div > main > div.page__content > article > div:nth-child(3) > div.layout--main > div > div > div.nasdaq-screener__content-container > div:nth-child(2) > div.nasdaq-screener__download > div > button")
            download_csv.click()
            time.sleep(5)
            driver.close()
            print('downloaded')
            break
        except:
            print('invalid')

    while True:
        try:
            filename = max([os.getcwd() + "\\" + f for f in os.listdir(os.getcwd())],key=os.path.getctime)
            print(filename)
            shutil.move(os.path.join(os.getcwd(),filename),"test.csv")
            print('done')
            break
        except:
            print("failed rename")

    df = pandas.read_csv("test.csv",index_col=0)


def get_stock_details(symbol):
    global df
    row = df.loc[symbol]
    price = row["Last Sale"]
    change = row["Net Change"]
    percentChange = row["% Change"]
    name = row["Name"]
    return [price,change,percentChange,name]


scheduler = BackgroundScheduler()
scheduler.add_job(func=download_stock_data, trigger="interval", seconds=60)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())

app = Flask(__name__)

@app.route("/quote")
def display_stock():
    symbol = request.args.get("symbol",default="AAPL")
    return get_stock_details(symbol)
    
if __name__ == "__main__":
    app.run()



