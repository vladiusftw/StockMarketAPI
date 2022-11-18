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
import glob

options = webdriver.ChromeOptions()
prefs = {"download.default_directory": os.getcwd()}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(
    executable_path=os.getcwd()+'/chromedriver.exe', chrome_options=options)
driver.minimize_window()


def download_stock_data():
    print("starting download")
    driver.get(
        "https://www.nasdaq.com/market-activity/stocks/screener?exchange=NASDAQ&render=download")
    while True:
        try:
            download_csv = driver.find_element(
                By.CSS_SELECTOR, 'body > div.dialog-off-canvas-main-canvas > div > main > div.page__content > article > div:nth-child(3) > div.layout--main > div > div > div.nasdaq-screener__content-container > div:nth-child(2) > div.nasdaq-screener__download > div > button')
            download_csv.click()
            time.sleep(5)
            print('downloaded')
            try:
                list_of_files = glob.glob(os.getcwd() + "/*.csv")
                list_of_files.remove(max(list_of_files, key=os.path.getctime))
                for filename in list_of_files:
                    filename_relPath = os.path.join(os.getcwd(),filename)
                    print(filename)
                    os.remove(filename_relPath)
            except Exception as e:
                print(e)
            break
        except:
            print('invalid')
    

scheduler = BackgroundScheduler()
scheduler.add_job(func=download_stock_data, trigger="interval", seconds=30)
scheduler.start()

atexit.register(lambda: scheduler.shutdown())
atexit.register(lambda: driver.close())

app = Flask(__name__)


def get_stock_details(symbol):
    list_of_files = glob.glob(os.getcwd() + "/*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    tempDF = pandas.read_csv(latest_file, index_col=0).filter(items=[symbol], axis=0).reset_index()
    return (tempDF[["Symbol", "Name", "Last Sale", 'Net Change', '% Change', 'Market Cap', 'Volume', 'Sector', 'Industry']]).replace(np.nan, "", regex=True).values.tolist()


def get_stocks_by_search(symbol):
    list_of_files = glob.glob(os.getcwd() + "/*.csv")
    latest_file = max(list_of_files, key=os.path.getctime)
    tempDF = pandas.read_csv(latest_file, index_col=0).filter(like=symbol, axis=0).reset_index()
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
