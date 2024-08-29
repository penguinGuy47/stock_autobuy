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

    # chase.buy(ticker)
    # tradier.buy(ticker)
    fidelity.buy(ticker)

if __name__ == "__main__":
    main()
