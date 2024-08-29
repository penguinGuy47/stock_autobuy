import chase
import fidelity
import firstrade
import public
import robinhood
import schwaab
import sofi
import tornado
import tradier
import webull
import wellsfargo

def main():
    # ticker = input("Enter the ticker you would to purchase: ")
    ticker = 'AMC'
    chrome_path = r"C:\Users\kaile\AppData\Local\Google\Chrome\User Data" # add the path to your chrome
    chrome_profile = r"Profile 6" # change this accordingly

    # chase.buy(ticker)
    # tradier.buy(ticker)
    fidelity.buy(ticker)
    # firstrade.buy(ticker, chrome_path, chrome_profile)

if __name__ == "__main__":
    main()
