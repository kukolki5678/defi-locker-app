"""
Exit Watcher — находит первую исходящую транзакцию с Bitcoin-адреса.
"""

import requests
import sys

def get_transactions(address):
    url = f"https://blockstream.info/api/address/{address}/txs"
    r = requests.get(url)
    r.raise_for_status()
    return r.json()

def find_first_spend(txs, address):
    for tx in reversed(txs):  # от старых к новым
        for vin in tx.get("vin", []):
            if vin.get("prevout", {}).get("scriptpubkey_address", "") == address:
                return {
                    "txid": tx.get("txid"),
                    "timestamp": tx.get("status", {}).get("block_time"),
                }
    return None

def main(address):
    print(f"📤 Проверка первой исходящей транзакции с адреса: {address}")
    try:
        txs = get_transactions(address)
    except Exception as e:
        print("❌ Ошибка при получении транзакций:", e)
        return

    first_spend = find_first_spend(txs, address)
    if first_spend:
        from datetime import datetime
        ts = datetime.utcfromtimestamp(first_spend["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        print(f"🔎 Первая исходящая транзакция найдена:")
        print(f"🆔 TXID: {first_spend['txid']}")
        print(f"📅 Дата (UTC): {ts}")
    else:
        print("✅ Адрес пока не тратил средства.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python exit_watcher.py <bitcoin_address>")
        sys.exit(1)
    main(sys.argv[1])
