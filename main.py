import chase
import fidelity
import firstrade
import public
import robinhood
import schwab
import sofi
import tornado
import tradier
import webull
import wellsfargo

def main():
    # ticker = input("Enter the ticker you would to purchase: ")
    ticker = 'GME'
    chrome_path = r"C:\Users\kaile\AppData\Local\Google\Chrome\User Data" # add the path to your chrome
    chrome_profile = r"Profile 5" # change this accordingly
    trade_share_count = '1'
    # buy_share_count = '1'
    # sell_share_count = input("How many shares would you like to sell? For all shares, type 'all', else enter an amount: ")

    # chase.buy(ticker)

    # tradier.buy(ticker)
    # fidelity.buy(ticker, chrome_path, chrome_profile)
    # fidelity.sell(ticker, chrome_path, chrome_profile)

    # firstrade.buy(ticker, chrome_path, chrome_profile)

    # schwab.buy(ticker, chrome_path, chrome_profile)

    # sofi.buy(ticker, chrome_path, chrome_profile)

    # robinhood.buy(ticker, chrome_path, chrome_profile, trade_share_count)
    robinhood.sell(ticker, chrome_path, chrome_profile, trade_share_count)


if __name__ == "__main__":
    main()
