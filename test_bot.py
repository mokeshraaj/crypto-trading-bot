import logging
from binance.client import Client
from binance.enums import *
import os
import argparse

# Logging configuration
logging.basicConfig(
    filename="trading_bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class BasicBot:
    def __init__(self, api_key, api_secret, testnet=True, simulate=False):
        self.simulate = simulate
        if not simulate:
            self.client = Client(api_key, api_secret)
            if testnet:
                self.client.FUTURES_URL = 'https://testnet.binancefuture.com/fapi'
            try:
                self.client.ping()
                logging.info("Connected to Binance Testnet.")
            except Exception as e:
                logging.error(f"Connection failed: {e}")
                raise
        else:
            logging.info("Simulation mode ON — no real orders will be placed.")

    def place_order(self, symbol, side, order_type, quantity, price=None, stop_price=None):
        params = {
            "symbol": symbol,
            "side": side,
            "quantity": quantity
        }
        if order_type == 'MARKET':
            params["type"] = ORDER_TYPE_MARKET
        elif order_type == 'LIMIT':
            params.update({
                "type": ORDER_TYPE_LIMIT,
                "price": price,
                "timeInForce": TIME_IN_FORCE_GTC
            })
        elif order_type == 'STOP_LIMIT':
            params.update({
                "type": ORDER_TYPE_STOP_MARKET,
                "stopPrice": stop_price,
                "price": price,
                "timeInForce": TIME_IN_FORCE_GTC,
                "workingType": "CONTRACT_PRICE"
            })
        else:
            raise ValueError("Unsupported order type")

        if self.simulate:
            # Log and print a simulated order
            logging.info(f"[SIMULATED] Order params: {params}")
            return {"simulated": True, "params": params}

        try:
            order = self.client.futures_create_order(**params)
            logging.info(f"Order placed: {order}")
            return order
        except Exception as e:
            logging.error(f"Error placing order: {e}")
            return None

def get_user_input():
    print("=== Binance Futures Testnet Bot ===")
    symbol = input("Enter trading pair (e.g., BTCUSDT): ").upper()
    side_input = input("Enter side (BUY/SELL): ").upper()
    if side_input not in ['BUY', 'SELL']:
        print("Invalid side. Must be BUY or SELL.")
        return None

    order_type_input = input("Order type (MARKET / LIMIT / STOP_LIMIT): ").upper()
    if order_type_input not in ['MARKET', 'LIMIT', 'STOP_LIMIT']:
        print("Invalid order type.")
        return None

    quantity = float(input("Enter quantity: "))
    price = None
    stop_price = None

    if order_type_input == 'LIMIT':
        price = input("Enter limit price: ")
    elif order_type_input == 'STOP_LIMIT':
        stop_price = input("Enter stop price: ")
        price = input("Enter limit price after trigger: ")

    return symbol, side_input, order_type_input, quantity, price, stop_price

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--simulate", action="store_true",
                        help="Run in simulation mode (no real API calls).")
    args = parser.parse_args()

    # You can still plug in real keys later if permissions are fixed
    API_KEY    = "JKGoMQHGoK8aREeLPO1HPEQskIuFJcJSKblndwMUKcskoh6VYWsxKPfWoUpH6RaA"
    API_SECRET = "8lW39pft3v1D9AV91qUHQe1FtYcoWaTwhgTnN0g5Tw1CNyCDYWEyU54FcC3jhK5I"

    bot = BasicBot(API_KEY, API_SECRET, simulate=args.simulate)

    user_input = get_user_input()
    if user_input:
        symbol, side, order_type, quantity, price, stop_price = user_input
        order = bot.place_order(
            symbol=symbol,
            side=SIDE_BUY if side=='BUY' else SIDE_SELL,
            order_type=order_type,
            quantity=quantity,
            price=price, stop_price=stop_price
        )
        if order:
            print("✅ Order placed successfully!" if not args.simulate
                  else "🧪 Simulation: order parameters logged.")
        else:
            print("❌ Failed to place order. Check logs.")
