# Binance Futures Testnet Trading Bot

A Python CLI app for placing `MARKET` and `LIMIT` orders on Binance Futures Testnet (USDT-M). It supports both `BUY` and `SELL`, validates user input, and logs API requests, responses, and errors.

## Features

- Place `MARKET` and `LIMIT` orders on Binance Futures Testnet
- Support both `BUY` and `SELL`
- Validate symbol, side, order type, quantity, and price
- Log requests, responses, and errors to `logs/trading_bot.log`
- Handle invalid input, API errors, and network failures
- Includes a simple interactive CLI mode

## Approach

I kept the project as a small CLI app with a separate client, validation layer, and order manager. For this assignment, that felt like the most practical approach because the app only needs to do a few things well: take input, validate it, place an order, and show a clear result.

I used direct REST calls instead of a heavier wrapper so the request flow stays explicit and easy to reason. That will also make logging, signing, and error handling more transparent, which is useful in a project like this.

## Project Structure

```text
trading_bot/
  bot/
    __init__.py
    client.py
    logging_config.py
    orders.py
    validators.py
  logs/
  .env.example
  cli.py
  README.md
  requirements.txt
```

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\activate
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your Binance Futures Testnet API credentials:

```powershell
Copy-Item .env.example .env
```

## How to Run

Show CLI help:

```powershell
python cli.py --help
```

Place a market order:

```powershell
python cli.py place-order --symbol BTCUSDT --side BUY --order-type MARKET --quantity 0.001
```

Place a limit order:

```powershell
python cli.py place-order --symbol BTCUSDT --side SELL --order-type LIMIT --quantity 0.001 --price 120000
```

Run in interactive mode:

```powershell
python cli.py interactive
```

## Output

The CLI shows:

- order request summary
- order response details
- success or failure message
- log file location

## Logging

All runs append to:

```text
logs/trading_bot.log
```

Sample logs included in the repository:

- `logs/market_order_example.log`
- `logs/limit_order_example.log`

## Assumptions

- Only USDT-M futures symbols are accepted
- `LIMIT` orders use `GTC`
- `MARKET` orders must not include a price
- API keys are loaded from environment variables or `.env`

## Quick Checks

- `python -m compileall .`
- `python cli.py --help`

## Next Improvement

If I had to extend it further, I would add exchange info validation against Binance symbol filters. This would allow quantity and price to be checked against the actual lot size and tick size before placing an order.
