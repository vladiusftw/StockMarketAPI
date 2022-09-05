from selenium import webdriver
from selenium.webdriver.common.by import By
import os
import shutil
import time
import pandas
import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request
import numpy as np

df = pandas.read_csv("test.csv", index_col=0)
options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.getcwd()}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(
    executable_path=os.getcwd()+'/chromedriver.exe', chrome_options=options)
driver.minimize_window()


def download_stock_data():
    print("starting download")
    global df
    global driver
    driver.get(
        "https://www.nasdaq.com/market-activity/stocks/screener?exchange=NASDAQ&render=download")
    while True:
        try:
            download_csv = driver.find_element(
                By.CSS_SELECTOR, 'body > div.dialog-off-canvas-main-canvas > div > main > div.page__content > article > div:nth-child(3) > div.layout--main > div > div > div.nasdaq-screener__content-container > div:nth-child(2) > div.nasdaq-screener__download > div > button')
            download_csv.click()
            time.sleep(5)
            print('downloaded')
            break
        except:
            print('invalid')

    while True:
        try:
            filename = max(
                [os.getcwd() + "\\" + f for f in os.listdir(os.getcwd())], key=os.path.getctime)
            print(filename)
            shutil.move(os.path.join(os.getcwd(), filename), "test.csv")
            print('done')
            break
        except:
            print("failed rename")

    df = pandas.read_csv("test.csv", index_col=0)


scheduler = BackgroundScheduler()
scheduler.add_job(func=download_stock_data, trigger="interval", seconds=10)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
atexit.register(lambda: driver.close())

app = Flask(__name__)


def get_stock_details(symbol):
    global df
    tempDF = df.filter(items=[symbol], axis=0).reset_index()
    return (tempDF[["Symbol", "Name", "Last Sale", 'Net Change', '% Change', 'Market Cap', 'Volume', 'Sector', 'Industry']]).replace(np.nan, "", regex=True).values.tolist()


def get_stocks_by_search(symbol):
    global df
    tempDF = df.filter(like=symbol, axis=0).reset_index()
    return (tempDF[["Symbol", "Name", "Last Sale", 'Net Change', '% Change', 'Market Cap', 'Volume', 'Sector', 'Industry']]).replace(np.nan, "", regex=True).head(100).values.tolist()


@app.route("/quote")
def display_stock():
    symbol = request.args.get("symbol", default="AAPL")
    return get_stock_details(symbol)


@app.route("/search")
def search_stocks():
    symbol = request.args.get("symbol", default="")
    return get_stocks_by_search(symbol)


if __name__ == "__main__":
    app.run()
