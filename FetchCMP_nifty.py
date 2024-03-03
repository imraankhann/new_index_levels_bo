from pickle import NONE
import time
from httplib2 import Credentials
import requests
import json
import math
from datetime import datetime
import shutil
from pytz import timezone
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2 import service_account
from pathlib import Path
import re
import numpy as np

def strRed(skk): return "\033[91m {}\033[00m".format(skk)
def strGreen(skk): return "\033[92m {}\033[00m".format(skk)
def strYellow(skk): return "\033[93m {}\033[00m".format(skk)
def strLightPurple(skk): return "\033[94m {}\033[00m".format(skk)
def strPurple(skk): return "\033[95m {}\033[00m".format(skk)
def strCyan(skk): return "\033[96m {}\033[00m".format(skk)
def strLightGray(skk): return "\033[97m {}\033[00m".format(skk)
def strBlack(skk): return "\033[98m {}\033[00m".format(skk)
def strBold(skk): return "\033[1m {}\033[0m".format(skk)


now = datetime.now()
format = "%d-%m-%Y %H:%M:%S %Z%z"
now_utc = datetime.now(timezone('UTC'))
now_asia = now_utc.astimezone(timezone('Asia/Kolkata'))
ocTime = now_asia.strftime(format)
fName = now_asia.strftime(format)
curWeekday = datetime.today().weekday()
isHolidayNxtDay = ""
reqTime = ocTime[11:16]
print(reqTime)
reqSec = ocTime[14:16]
intTime = int(reqTime[0:2])
intSec = int(reqSec)
nowTime = fName.split(" IST")
print(nowTime[0])
print(fName)
if intTime >= 9 and intTime < 16:
    while(intTime!=15 ):
        print("Time: "+str(intTime))
    # NiftyTomorroLevels = "22386"
    # BankNiftyTomorrowLevels = "47172"

        PE_NiftyTomorroLevels = 22366
        PE_BankNiftyTomorrowLevels = 22406

        CE_NiftyTomorroLevels=22398
        CE_BankNiftyTomorrowLevels=47317

        # Method to get nearest strikes
        def round_nearest(x, num=50): return int(math.ceil(float(x)/num)*num)
        def nearest_strike_bnf(x): return round_nearest(x, 100)
        def nearest_strike_nf(x): return round_nearest(x, 50)


        # Urls for fetching Data
        url_oc = "https://www.nseindia.com/option-chain"
        url_bnf = 'https://www.nseindia.com/api/option-chain-indices?symbol=BANKNIFTY'
        url_nf = 'https://www.nseindia.com/api/option-chain-indices?symbol=NIFTY'
        url_finNif = 'https://www.nseindia.com/api/option-chain-indices?symbol=FINNIFTY'
        url_indices = "https://www.nseindia.com/api/allIndices"

        # Headers
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36',
                'accept-language': 'en,gu;q=0.9,hi;q=0.8',
                'accept-encoding': 'gzip, deflate, br'}

        sess = requests.Session()
        cookies = dict()

        # Local methods

        def set_cookie():
            request = sess.get(url_oc, headers=headers, timeout=5)
            cookies = dict(request.cookies)


        def get_data(url):
            set_cookie()
            response = sess.get(url, headers=headers, timeout=5, cookies=cookies)
            if (response.status_code == 401):
                set_cookie()
                response = sess.get(url_nf, headers=headers,
                                    timeout=5, cookies=cookies)
            if (response.status_code == 200):
                return response.text
            return ""


        def set_header():
            global bnf_ul
            global nf_ul
            global bnf_nearest
            global nf_nearest
            response_text = get_data(url_indices)
            data = json.loads(response_text)
            for index in data["data"]:
                if index["index"] == "NIFTY 50":
                    nf_ul = index["last"]
                    print("nifty")
                if index["index"] == "NIFTY BANK":
                    bnf_ul = index["last"]
                    print("banknifty")
            bnf_nearest = nearest_strike_bnf(bnf_ul)
            nf_nearest = nearest_strike_nf(nf_ul)


        # Showing Header in structured format with Last Price and Nearest Strike
        def print_header(index="", ul=0, nearest=0):
            print(strPurple(index.ljust(12, " ") + " => ") + strLightPurple(" Last Price: ") +
                strBold(str(ul)) + strLightPurple(" Nearest Strike: ") + strBold(str(nearest)))


        def print_hr():
            print(strYellow("|".rjust(70, "-")))

        def send_lastprice():
            global nf_ul
            global nf_nearest
            response_text = get_data(url_indices)
            data = json.loads(response_text)
            nf_nearest = 0
            nf_ul = 0
            for index in data["data"]:
                if index["index"] == "NIFTY 50":
                    nf_ul = index["last"]
                    #print(nf_ul)
                    nf_nearest = nearest_strike_nf(nf_ul)
            return nf_ul

        def send_Bnflastprice():
            global bnf_ul
            global bnf_nearest
            response_text = get_data(url_indices)
            data = json.loads(response_text)
            bnf_nearest = 0
            bnf_ul = 0
            for index in data["data"]:
                if index["index"] == "NIFTY BANK":
                    bnf_ul = index["last"]
                    #print(bnf_ul)
                    bnf_nearest = nearest_strike_bnf(bnf_ul)
            return bnf_ul

        #print_header("Nifty", nf_ul, nf_nearest)
        print(send_lastprice())
        print(send_Bnflastprice())

        niftyLastPrice_pe = int(send_lastprice()-20)
        niftyLastPrice_ce = int(send_lastprice()+20)
        bnfLastPrice_pe = int(send_Bnflastprice()-20)
        bnfLastPrice_ce = int(send_Bnflastprice()+20)
        if(niftyLastPrice_pe==PE_NiftyTomorroLevels):
            t_url = "https://api.telegram.org/bot6377307246:AAEuJAlBiQgDQEa03yNmKQJmZbXyQ0WINOk/sendMessage?chat_id=-996001230&text="+"======================\n"+nowTime[0]+"\n======================\n"+"PYTHON-BOT FOR TODAY's LEVELS\n"+"======================\n"+"NIFTY TRADING NEAR PE BO: "+str(niftyLastPrice_pe)+"\n"+"=========================\n"
            requests.post(t_url)
        elif(niftyLastPrice_ce==CE_NiftyTomorroLevels):
            t_url = "https://api.telegram.org/bot6377307246:AAEuJAlBiQgDQEa03yNmKQJmZbXyQ0WINOk/sendMessage?chat_id=-996001230&text="+"======================\n"+nowTime[0]+"\n======================\n"+"PYTHON-BOT FOR TODAY's LEVELS\n"+"======================\n"+"NIFTY TRADING NEAR CE BO: "+str(niftyLastPrice_ce)+"\n"+"=========================\n"
            requests.post(t_url)

        if(bnfLastPrice_pe==PE_BankNiftyTomorrowLevels):
            t_url = "https://api.telegram.org/bot6377307246:AAEuJAlBiQgDQEa03yNmKQJmZbXyQ0WINOk/sendMessage?chat_id=-996001230&text="+"======================\n"+nowTime[0]+"\n======================\n"+"PYTHON-BOT FOR TODAY's LEVELS\n"+"======================\n"+"BANK-NIFTY TRADING NEAR PE BO: "+str(bnfLastPrice_pe)+"\n"+"=========================\n"
            requests.post(t_url)

        elif(bnfLastPrice_ce==PE_BankNiftyTomorrowLevels):
            t_url = "https://api.telegram.org/bot6377307246:AAEuJAlBiQgDQEa03yNmKQJmZbXyQ0WINOk/sendMessage?chat_id=-996001230&text="+"======================\n"+nowTime[0]+"\n======================\n"+"PYTHON-BOT FOR TODAY's LEVELS\n"+"======================\n"+"BANK-NIFTY TRADING NEAR CE BO: "+str(bnfLastPrice_ce)+"\n"+"=========================\n"
            requests.post(t_url)
        time.sleep(120)
        if(intTime>16):
            exit()

