from rich.console import Console
from rich.table import Table
import pandas as pd

console = Console()

def print_backtest_report(results: dict, symbol: str):
    """Print beautiful backtest report."""
    if not results:
        console.print(f"[red]No backtest results available for {symbol}.[/red]")
        return

    table = Table(title=f"BACKTEST RESULTS: {symbol} (30 days)")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta")

    table.add_row("Total Trades", str(results.get("total_trades", 0)))
    
    win_rate = results.get("win_rate", 0)
    win_rate_str = f"{win_rate:.1%} {'✅' if win_rate > 0.55 else ''}"
    table.add_row("Win Rate", win_rate_str)
    
    sharpe = results.get("sharpe_ratio", 0)
    sharpe_str = f"{sharpe:.2f} {'✅' if sharpe > 1.5 else ''}"
    table.add_row("Sharpe Ratio", sharpe_str)
    
    pnl = results.get("total_pnl_pct", 0)
    pnl_str = f"{pnl:+.1%}"
    table.add_row("Total P&L", pnl_str)
    
    dd = results.get("max_drawdown_pct", 0)
    table.add_row("Max Drawdown", f"{dd:.1%}")

    console.print(table)

def compare_to_buy_hold(backtest_results: dict, price_data: pd.DataFrame) -> dict:
    """Compare strategy P&L vs simple buy-and-hold."""
    if price_data.empty:
        return {"strategy_pnl": 0, "bh_pnl": 0, "alpha": 0}
        
    start_price = price_data.iloc[0]['close']
    end_price = price_data.iloc[-1]['close']
    bh_pnl = (end_price - start_price) / start_price
    
    strat_pnl = backtest_results.get("total_pnl_pct", 0)
    
    return {
        "strategy_pnl": strat_pnl,
        "bh_pnl": bh_pnl,
        "alpha": strat_pnl - bh_pnl
    }
