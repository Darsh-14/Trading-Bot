from typing import Optional

import typer

from bot.logging_config import LOG_FILE
from bot.logging_config import setup_logging
from bot.orders import OrderManager

app = typer.Typer(
    add_completion=False,
    help="Place Binance Futures Testnet orders from the command line.",
    no_args_is_help=True,
)
logger = setup_logging()


def render_summary(request: dict[str, object], response: dict[str, object]) -> None:
    typer.echo("Order request summary")
    typer.echo(f"  Symbol: {request['symbol']}")
    typer.echo(f"  Side: {request['side']}")
    typer.echo(f"  Type: {request['order_type']}")
    typer.echo(f"  Quantity: {request['quantity']}")
    if request["price"] is not None:
        typer.echo(f"  Price: {request['price']}")

    typer.echo("")
    typer.echo("Order response details")
    typer.echo(f"  Order ID: {response.get('orderId', 'N/A')}")
    typer.echo(f"  Status: {response.get('status', 'N/A')}")
    typer.echo(f"  Executed Quantity: {response.get('executedQty', 'N/A')}")
    typer.echo(f"  Average Price: {response.get('avgPrice', 'N/A')}")


@app.command("place-order")
def place_order(
    symbol: str = typer.Option(..., "--symbol", "-s", help="Trading symbol, for example BTCUSDT."),
    side: str = typer.Option(..., "--side", help="Order side: BUY or SELL."),
    order_type: str = typer.Option(..., "--order-type", "-t", help="Order type: MARKET or LIMIT."),
    quantity: str = typer.Option(..., "--quantity", "-q", help="Order quantity, for example 0.001."),
    price: Optional[str] = typer.Option(None, "--price", "-p", help="Limit price. Required only for LIMIT orders."),
) -> None:
    """Place a market or limit order on Binance Futures Testnet."""
    try:
        manager = OrderManager()
        result = manager.place_order(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price)
    except Exception as exc:
        logger.exception("cli_place_order_failed")
        typer.secho(f"Order failed: {exc}", fg=typer.colors.RED, err=True)
        typer.echo(f"Check logs for details: {LOG_FILE}")
        raise typer.Exit(code=1) from exc

    request = result["request"]
    response = result["response"]
    render_summary(request, response)
    typer.secho("\nOrder placed successfully.", fg=typer.colors.GREEN)
    typer.echo(f"Log file: {LOG_FILE}")


@app.command()
def interactive() -> None:
    """Prompt for order inputs interactively."""
    symbol = typer.prompt("Symbol").strip()
    side = typer.prompt("Side (BUY/SELL)").strip()
    order_type = typer.prompt("Order type (MARKET/LIMIT)").strip()
    quantity = typer.prompt("Quantity").strip()
    price: Optional[str] = None

    if order_type.strip().upper() == "LIMIT":
        price = typer.prompt("Price").strip()

    place_order(symbol=symbol, side=side, order_type=order_type, quantity=quantity, price=price)


if __name__ == "__main__":
    app()
