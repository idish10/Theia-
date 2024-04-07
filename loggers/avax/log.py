import requests
import os
from pycoingecko import CoinGeckoAPI
from pattrn_robust_tracking.utils.util import coralogix_decorator

def get_wonderland_balance(address):
    cg = CoinGeckoAPI()
    MEMO = "0x136acd46c134e8269052c62a67042d6bdedde3c9"
    API_TOKEN = '36JFZ8IY9DAGGIRIZH6XDBXVU5FNS1M97W'
    balance_request = requests.get(
        f'https://api.snowtrace.io/api?module=account&action=tokenbalance&contractaddress={MEMO}&address={address}&tag=latest&apikey={API_TOKEN}').json()
    wonderland_amount = float(
        balance_request['result'][0] + '.' + balance_request['result'][1:])
    wonderlnd_price = cg.get_price(ids='wonderland', vs_currencies='usd')[
        'wonderland']['usd']
    return wonderland_amount*wonderlnd_price
    
@coralogix_decorator(client=os.environ["CLIENT"], wallet_type="avax")
def main():
    wonderland_balance = get_wonderland_balance(os.environ['ADDRESS'])
    print(f"Wonderland balance: {wonderland_balance}")
    field_name = f"{os.environ['CLIENT']}_wonderland_balance"
    return wonderland_balance
		


if __name__ == '__main__':
	main()
	
	
	
   
