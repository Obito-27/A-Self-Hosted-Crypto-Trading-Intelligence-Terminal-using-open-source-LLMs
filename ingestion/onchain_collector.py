import logging
import os
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from storage.database import Database

logger = logging.getLogger(__name__)

KNOWN_EXCHANGES = {
    "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE": "Binance",
    "0xD551234Ae421e3BCBA99A0Da6d736074f22192FF": "Binance 2",
    "0x564286362092D8e7936f0549571a803B203aAceD": "Binance 3",
    "0xfE9e8709d3215310075d67E3ed32A380CCf451C8": "Binance 4",
}

class OnChainCollector:
    WHALE_THRESHOLD_ETH = 500  # ~$1M+

    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("ETHERSCAN_API_KEY")
        self.demo_mode = os.getenv("DEMO_MODE", "false").lower() == "true"

    def fetch_large_eth_txs(self) -> list:
        """Fetch recent transactions for a sample exchange wallet to find large movements."""
        if self.demo_mode or not self.api_key:
            return self.get_mock_data()

        # In a real scenario, we'd iterate multiple exchanges or use a specialized whale alert API
        # Here we sample Binance 1 for the hackathon
        address = "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE"
        url = f"https://api.etherscan.io/api?module=account&action=txlist&address={address}&startblock=0&endblock=99999999&page=1&offset=50&sort=desc&apikey={self.api_key}"
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                result = response.json().get("result", [])
                if isinstance(result, list):
                    return result
            logger.warning(f"Etherscan API failed: {response.status_code}")
        except Exception as e:
            logger.error(f"Error calling Etherscan: {e}")
        
        return self.get_mock_data()

    def get_mock_data(self) -> list:
        """Return some fake whale txs for demo."""
        return [
            {
                "hash": "0xmock1", "from": "0xwhale1", "to": "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE",
                "value": str(1000 * 10**18), "timeStamp": str(int(time.time()))
            },
            {
                "hash": "0xmock2", "from": "0x3f5CE5FBFe3E9af3971dD833D26bA9b5C936f0bE", "to": "0xwhale2",
                "value": str(1500 * 10**18), "timeStamp": str(int(time.time() - 3600))
            }
        ]

    def classify_transaction(self, tx: dict) -> str:
        """Returns EXCHANGE_INFLOW, EXCHANGE_OUTFLOW, or WALLET_TO_WALLET."""
        from_addr = tx.get("from", "").lower()
        to_addr = tx.get("to", "").lower()
        
        exchanges = [addr.lower() for addr in KNOWN_EXCHANGES.keys()]
        
        if from_addr in exchanges and to_addr in exchanges:
            return "EXCHANGE_TRANSFER"
        elif to_addr in exchanges:
            return "EXCHANGE_INFLOW"
        elif from_addr in exchanges:
            return "EXCHANGE_OUTFLOW"
        else:
            return "WALLET_TO_WALLET"

    def run_once(self, db: Database) -> list:
        """Fetch and store whale txs."""
        raw_txs = self.fetch_large_eth_txs()
        stored_txs = []
        
        for tx in raw_txs:
            value_eth = float(tx.get("value", 0)) / 1e18
            if value_eth >= self.WHALE_THRESHOLD_ETH:
                direction = self.classify_transaction(tx)
                record = {
                    "tx_hash": tx.get("hash"),
                    "symbol": "ETH",
                    "from_address": tx.get("from"),
                    "to_address": tx.get("to"),
                    "value_usd": value_eth * 3500, # Approximate price for whale detection
                    "direction": direction,
                    "timestamp": datetime.utcfromtimestamp(int(tx.get("timeStamp", 0)))
                }
                db.insert_whale_tx(record)
                stored_txs.append(record)
        
        logger.info(f"On-chain collection complete. Found {len(stored_txs)} whale transactions.")
        return stored_txs
