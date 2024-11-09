# main_bot.py

# 导入必要的库
from dotenv import load_dotenv
import os
import ccxt
import time
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 加载 .env 文件
load_dotenv()

# 从 .env 文件中读取 API 密钥
api_key = os.getenv('API_KEY')
secret_key = os.getenv('SECRET_KEY')

# 初始化Gate交易所
exchange = ccxt.gate({
    'apiKey': api_key,
    'secret': secret_key,
    'options': {
        'createMarketBuyOrderRequiresPrice': False  # 设置此选项为False
    }
})

# 加载市场数据
try:
    markets = exchange.load_markets()
    logging.info("市场数据加载成功。")
except Exception as e:
    logging.error(f"加载市场数据失败: {e}")
    exit(1)

# 检查市场状态
def is_market_open(symbol):
    try:
        market = exchange.market(symbol)
        return True
    except ccxt.BaseError as e:
        logging.warning(f"市场 {symbol} 不可用: {e}")
        return False

# 获取当前市场价格
def get_current_price(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        logging.error(f"获取 {symbol} 的最新价格失败: {e}")
        return None

# 计算下单数量
def calculate_amount(symbol, amount_to_spend):
    price = get_current_price(symbol)
    if price is None:
        return None
    amount = amount_to_spend / price
    min_order_value = 3  # 最小订单金额
    if amount * price < min_order_value:
        amount = min_order_value / price
    return amount

# 获取账户余额
def get_account_balance():
    try:
        balance = exchange.fetch_balance()
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        logging.info(f"当前 USDT 余额: {usdt_balance}")
        return usdt_balance
    except Exception as e:
        logging.error(f"获取账户余额失败: {e}")
        return 0

# 下单买入
def place_buy_order(symbol, amount_to_spend):
    usdt_balance = get_account_balance()
    if usdt_balance < amount_to_spend:
        logging.error(f"USDT 余额不足。所需: {amount_to_spend}，可用: {usdt_balance}")
        return

    amount = calculate_amount(symbol, amount_to_spend)
    if amount is None:
        logging.error("计算下单数量失败。")
        return

    try:
        order = exchange.create_market_buy_order(symbol, amount)
        logging.info(f"买单成功。购买了 {order['amount']} {symbol.split('/')[0]}，平均价格为 {order['average']}。")
    except Exception as e:
        error_message = str(e)
        if "BALANCE_NOT_ENOUGH" in error_message:
            logging.error(f"下单失败: 余额不足。所需: {amount_to_spend}，可用: {usdt_balance}")
        else:
            logging.error(f"下单失败: {error_message}")

# 主程序
def run_bot(symbol, amount_to_spend):
    if symbol not in exchange.symbols:
        logging.error(f"无效的交易对: {symbol}")
        return

    while not is_market_open(symbol):
        logging.info("市场尚未开放。等待...")
        time.sleep(1)  # 每1秒检查一次

    logging.info("市场已开放！准备下单...")
    place_buy_order(symbol, amount_to_spend)

if __name__ == "__main__":
    symbol = 'X/USDT'  # 交易对，例如 'X/USDT'
    amount_to_spend = 10  # 调整为较小的金额，确保有足够的余额
    run_bot(symbol, amount_to_spend)