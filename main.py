"""
CryptoTerminal AI — Main Entry Point

Usage:
    python main.py --mode train      # Train ML models
    python main.py --mode pipeline   # Run data collection once
    python main.py --mode dashboard  # Launch Streamlit UI
    python main.py --mode web        # Launch High-Fidelity Web UI
    python main.py --mode demo       # Full demo with seeded data
    python main.py --mode backtest   # Run backtests and print results
    python main.py --mode validate   # Validate sentiment model accuracy
"""

import argparse
import logging
import subprocess
import os
import sys
import time
import webbrowser
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()

def print_banner():
    """Print ASCII art banner using rich"""
    banner = """
    ██████╗██████╗ ██╗   ██╗██████╗ ████████╗ ██████╗ 
   ██╔════╝██╔══██╗╚██╗ ██╔╝██╔══██╗╚══██╔══╝██╔═══██╗
   ██║     ██████╔╝ ╚████╔╝ ██████╔╝   ██║   ██║   ██║
   ██║     ██╔══██╗  ╚██╔╝  ██╔═══╝    ██║   ██║   ██║
   ╚██████╗██║  ██║   ██║   ██║        ██║   ╚██████╔╝
    ╚═════╝╚═╝  ╚═╝   ╚═╝   ╚═╝        ╚═╝    ╚═════╝ 
              TERMINAL AI  |  NMIMS INNOVATHON 2026
    """
    console.print(Panel(banner, style="bold cyan"))

def mode_train(args):
    """Train all ML models and print performance"""
    console.print("[bold yellow]🧠 Training ML Models...[/]")
    
    from storage.database import Database
    from prediction.trainer import ModelTrainer
    
    db_path = os.getenv("DB_PATH", "./data/crypto_terminal.db")
    db = Database(db_path)
    trainer = ModelTrainer()
    
    # Check if we have price data
    if not db.get_price_data("BTC", hours=1):
        console.print("[yellow]No data found. Seeding synthetic data...[/]")
        subprocess.run([sys.executable, "-m", "scripts.seed_data"])
    
    results = trainer.train_all_symbols(db)
    
    # Print results table
    table = Table(title="Model Training Results")
    table.add_column("Symbol", style="cyan")
    table.add_column("1h Accuracy", style="green")
    table.add_column("4h Accuracy", style="green")
    table.add_column("24h Accuracy", style="green")
    table.add_column("Status", style="bold")
    
    for symbol, result in results.items():
        if not result: continue
        acc_1h = f"{result.get('1h', {}).get('accuracy', 0):.1%}"
        acc_4h = f"{result.get('4h', {}).get('accuracy', 0):.1%}"
        acc_24h = f"{result.get('24h', {}).get('accuracy', 0):.1%}"
        status = "✅ Good" if result.get('1h', {}).get('accuracy', 0) > 0.55 else "⚠️ Below target"
        table.add_row(symbol, acc_1h, acc_4h, acc_24h, status)
    
    console.print(table)
    
def mode_pipeline(args):
    """Run data collection pipeline once"""
    console.print("[bold yellow]📡 Running Data Pipeline...[/]")
    
    from storage.database import Database
    from ingestion.pipeline import DataPipeline
    
    db_path = os.getenv("DB_PATH", "./data/crypto_terminal.db")
    db = Database(db_path)
    pipeline = DataPipeline(db)
    status = pipeline.run_once()
    
    # Print collection summary
    for source, stat in status.items():
        icon = "✅" if stat == "OK" else "⚠️"
        console.print(f"  {icon} {source}: {stat}")

def mode_backtest(args):
    """Run backtests and display results"""
    console.print("[bold yellow]📊 Running Strategy Backtests...[/]")
    from storage.database import Database
    from backtesting.engine import BacktestEngine
    from backtesting.metrics import print_backtest_report
    
    db_path = os.getenv("DB_PATH", "./data/crypto_terminal.db")
    db = Database(db_path)
    engine = BacktestEngine()
    
    for symbol in ["BTC", "ETH"]:
        results = engine.run_quick_backtest(db, symbol)
        print_backtest_report(results, symbol)

def mode_validate(args):
    """Validate sentiment model accuracy on validation set"""
    console.print("[bold yellow]🔍 Validating Sentiment Model...[/]")
    from sentiment.analyzer import SentimentAnalyzer
    from sentiment.prompts import validate_analyzer
    
    analyzer = SentimentAnalyzer()
    validate_analyzer(analyzer)

def mode_demo(args):
    """Seed data + train + launch dashboard"""
    console.print("[bold green]🚀 Starting DEMO MODE...[/]")
    subprocess.run([sys.executable, "-m", "scripts.seed_data"])
    mode_train(args)
    mode_backtest(args)
    console.print("[bold green]✅ Launching dashboard...[/]")
    subprocess.run(["streamlit", "run", "dashboard/app.py"])

def mode_web(args):
    """Launch FastAPI backend and open high-fidelity website"""
    console.print("[bold cyan]🌐 Launching CRYPTEX High-Fidelity Terminal...[/]")
    
    # Start FastAPI
    backend_cmd = [sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
    proc = subprocess.Popen(backend_cmd)
    
    # Give it time to start
    time.sleep(2)
    
    # Open the website
    index_path = os.path.abspath("index.html")
    console.print(f"[green]Opening: {index_path}[/]")
    webbrowser.open(f"file:///{index_path}")
    
    console.print("[yellow]Press Ctrl+C to stop the backend server.[/]")
    try:
        proc.wait()
    except KeyboardInterrupt:
        proc.terminate()
        console.print("\n[bold red]Server stopped.[/]")

if __name__ == "__main__":
    print_banner()
    parser = argparse.ArgumentParser(description="CryptoTerminal AI")
    parser.add_argument("--mode", choices=["train", "pipeline", "dashboard", "demo", "backtest", "validate", "web"], default="demo")
    parser.add_argument("--symbol", default="BTC", help="Symbol to process")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()
    
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    mode_funcs = {
        "train": mode_train,
        "pipeline": mode_pipeline,
        "demo": mode_demo,
        "backtest": mode_backtest,
        "validate": mode_validate,
        "dashboard": lambda a: subprocess.run(["streamlit", "run", "dashboard/app.py"]),
        "web": mode_web
    }
    
    mode_funcs[args.mode](args)
