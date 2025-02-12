from services.chase import buy as chase_buy, sell as chase_sell
from services.fidelity import buy as fidelity_buy, sell as fidelity_sell
from services.firstrade import buy as firstrade_buy, sell as firstrade_sell
from services.public import buy as public_buy, sell as public_sell
from services.robinhood import buy as robinhood_buy, sell as robinhood_sell
from services.schwab import buy as schwab_buy, sell as schwab_sell
from services.sofi import *
from services.webull import buy as webull_buy
from services.wellsfargo import *

import re

def main():
    # ticker = input("Enter the ticker you would to purchase: ")
    BUY_TICKERS = ['AMC','NIO']

    chrome_path = r"C:\Users\kaile\AppData\Local\Google\Chrome\User Data" # add the path to your chrome
    chrome_profile = r"Profile 5" # chawddnge this accordingly


    webull_buy(BUY_TICKERS, chrome_path, chrome_profile, 1, '9173858088', 'password')




if __name__ == "__main__":
    main()
