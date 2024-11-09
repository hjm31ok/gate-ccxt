# config.py

# 导入必要的库
from main_bot import run_bot

# 交易对
symbol = 'X/USDT'  # 交易对，例如 'BTC/USDT'

# 交易详情
amount_to_spend = 1  # 你希望花费的资金量，单位为USDT

# 执行交易
if __name__ == "__main__":
    run_bot(symbol, amount_to_spend)