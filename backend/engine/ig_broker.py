"""
IG Broker — Live/Demo trading on IG via the trading-ig library.
Drop-in replacement for LiveBroker (Alpaca) with matching interface.

Usage:
    broker = IGBroker(symbol='GLD', paper=True)
    broker.buy(price=2900, size=0.5)  # size in £/point for spread betting
"""

import os
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()


class IGBroker:
    """
    Adapts trading-ig to match the LiveBroker interface expected by strategies.
    Supports both DEMO and LIVE IG accounts.
    """

    # Map our symbols to IG epics (same as IGDataLoader)
    EPIC_MAP = {
        'GOLD': 'CS.D.CFDGOLD.CFDGC.IP',
        'GLD': 'CS.D.CFDGOLD.CFDGC.IP',
        'XAUUSD': 'CS.D.CFDGOLD.CFDGC.IP',
        'IAU': 'CS.D.CFDGOLD.CFDGC.IP',
        'SILVER': 'CS.D.USCSI.TODAY.IP',
        'SLV': 'CS.D.USCSI.TODAY.IP',
        'XAGUSD': 'CS.D.USCSI.TODAY.IP',
        'EURUSD': 'CS.D.EURUSD.MINI.IP',
        'GBPUSD': 'CS.D.GBPUSD.MINI.IP',
        'USDJPY': 'CS.D.USDJPY.MINI.IP',
    }

    # Currency code per instrument (IG requires matching currency)
    CURRENCY_MAP = {
        'GOLD': 'USD', 'GLD': 'USD', 'XAUUSD': 'USD', 'IAU': 'USD',
        'SILVER': 'USD', 'SLV': 'USD', 'XAGUSD': 'USD',
        'EURUSD': 'USD', 'GBPUSD': 'USD', 'USDJPY': 'JPY',
    }

    def __init__(self, symbol, paper=True, iteration_index=None):
        self.symbol = symbol
        self.paper = paper
        self.iteration_index = iteration_index

        # IG credentials
        self.api_key = os.getenv('IG_API_KEY')
        self.username = os.getenv('IG_USERNAME')
        self.password = os.getenv('IG_PASSWORD')
        self.acc_type = 'DEMO' if paper else os.getenv('IG_ACC_TYPE', 'LIVE')

        if not all([self.api_key, self.username, self.password]):
            raise ValueError("IG credentials not found in .env (need IG_API_KEY, IG_USERNAME, IG_PASSWORD)")

        # Resolve epic and currency
        self.epic = self.EPIC_MAP.get(symbol.upper())
        if not self.epic:
            raise ValueError(f"No IG epic mapping for symbol '{symbol}'. Add it to IGBroker.EPIC_MAP.")
        self.currency = self.CURRENCY_MAP.get(symbol.upper(), 'GBP')

        # Connect
        self.ig_service = None
        self._connect()

        # State
        self.trades = []
        self.new_trades = []
        self.positions = {}
        self.equity = 0.0
        self.initial_balance = 0.0

        # Initial sync
        self.refresh()
        self.initial_balance = self.equity

    def _connect(self):
        """Authenticate with IG API."""
        from trading_ig import IGService

        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                self.ig_service = IGService(
                    username=self.username,
                    password=self.password,
                    api_key=self.api_key,
                    acc_type=self.acc_type,
                )
                self.ig_service.create_session()
                print(f"✅ IGBroker connected ({self.acc_type} account)")
                return
            except Exception as e:
                print(f"⚠️ IG connection error (attempt {attempt+1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    raise ConnectionError(f"❌ Failed to connect to IG after {max_retries} attempts")

    def refresh(self):
        """Fetch latest account info and positions from IG."""
        try:
            # Get account balance
            accounts = self.ig_service.fetch_accounts()
            if accounts is not None and not accounts.empty:
                # Use the first account (or match by acc_type)
                acc = accounts.iloc[0]
                self.equity = float(acc.get('balance', 0))
                print(f"[IG] Equity: £{self.equity:.2f}")
            else:
                print("⚠️ Could not fetch IG account info")

            # Get open positions
            positions_response = self.ig_service.fetch_open_positions()
            self.positions = {}

            if positions_response is not None and not positions_response.empty:
                for _, pos in positions_response.iterrows():
                    epic = pos.get('epic', '')
                    direction = pos.get('direction', '')
                    size = float(pos.get('size', 0))
                    level = float(pos.get('level', 0))  # Entry price
                    deal_id = pos.get('dealId', '')

                    # Convert direction to signed size
                    if direction == 'SELL':
                        size = -size

                    # Store by epic AND by our symbol names (reverse lookup)
                    pos_data = {
                        'size': size,
                        'price': level,
                        'deal_id': deal_id,
                        'epic': epic,
                    }
                    self.positions[epic] = pos_data

                    # Also map back to our symbol names
                    for sym, ep in self.EPIC_MAP.items():
                        if ep == epic:
                            self.positions[sym] = pos_data

        except Exception as e:
            print(f"⚠️ Error refreshing IG positions: {e}")

    def get_equity(self):
        return self.equity

    def get_positions(self):
        return self.positions

    def get_position(self, symbol):
        """Return position size for a specific symbol."""
        # Try exact match
        if symbol in self.positions:
            return self.positions[symbol]['size']

        # Try uppercase
        if symbol.upper() in self.positions:
            return self.positions[symbol.upper()]['size']

        # Try epic
        epic = self.EPIC_MAP.get(symbol.upper(), symbol)
        if epic in self.positions:
            return self.positions[epic]['size']

        return 0.0

    def get_new_trades(self):
        """Return and clear new trades list."""
        trades_to_return = []
        for t in self.new_trades:
            t['iteration_index'] = self.iteration_index
            trades_to_return.append(t)
        self.new_trades = []
        return trades_to_return

    def set_entry_metadata(self, symbol, metadata):
        """Attach metadata to the last trade."""
        if self.new_trades:
            self.new_trades[-1].update(metadata)
        else:
            print(f"⚠️ set_entry_metadata called but no new trades for {symbol}")

    def buy(self, price, size, timestamp=None, stop_loss=None, take_profit=None, exit_reason=None):
        """
        Execute a BUY order on IG.
        size: position size in IG units (e.g., £/point for spread betting, or contracts for CFD)
        """
        return self._place_ig_order('BUY', price, size, stop_loss, take_profit)

    def sell(self, price, size, timestamp=None, stop_loss=None, take_profit=None, exit_reason=None):
        """
        Execute a SELL order on IG.
        For closing a long position: sell with the same size.
        """
        return self._place_ig_order('SELL', price, size, stop_loss, take_profit)

    def _place_ig_order(self, direction, price, size, stop_loss=None, take_profit=None):
        """
        Core order placement via IG REST API.
        direction: 'BUY' or 'SELL'
        """
        print(f"IG {direction}: {size} units of {self.symbol} (epic: {self.epic})")

        try:
            # Calculate stop/limit distances (IG uses distances from entry, not absolute levels)
            stop_distance = None
            limit_distance = None

            if stop_loss and price and price > 0:
                stop_distance = round(abs(price - stop_loss), 1)
                if stop_distance < 0.1:
                    stop_distance = None

            if take_profit and price and price > 0:
                limit_distance = round(abs(take_profit - price), 1)
                if limit_distance < 0.1:
                    limit_distance = None

            # IG create_open_position requires ALL positional args
            # CFD accounts use expiry='-', spread bet accounts use 'DFB'
            expiry = '-' if self.acc_type == 'DEMO' else 'DFB'

            result = self.ig_service.create_open_position(
                currency_code=self.currency,
                direction=direction,
                epic=self.epic,
                expiry=expiry,
                force_open=True,
                guaranteed_stop=False,
                level=None,                 # None for market orders
                limit_distance=limit_distance,
                limit_level=None,           # Use distance instead
                order_type='MARKET',
                quote_id=None,              # Not needed for market orders
                size=round(size, 2),
                stop_distance=stop_distance,
                stop_level=None,            # Use distance instead
                trailing_stop=False,
                trailing_stop_increment=None,
            )

            deal_ref = result.get('dealReference', 'unknown') if isinstance(result, dict) else str(result)
            print(f"📋 Order submitted: {deal_ref}")

            # Confirm the deal
            confirmation = self.ig_service.fetch_deal_by_deal_reference(deal_ref)
            if confirmation:
                deal_id = confirmation.get('dealId', deal_ref)
                deal_status = confirmation.get('dealStatus', 'UNKNOWN')
                level = confirmation.get('level', price)

                if deal_status == 'ACCEPTED':
                    print(f"✅ IG {direction} FILLED: {level} (deal: {deal_id})")

                    self.new_trades.append({
                        'symbol': self.symbol,
                        'side': direction.lower(),
                        'qty': size,
                        'signal_price': price,
                        'fill_price': float(level) if level else price,
                        'slippage': (float(level) - price) if level and price else 0.0,
                        'deal_id': deal_id,
                        'timestamp': datetime.now().isoformat(),
                    })

                    self.refresh()
                    return {'id': deal_id, 'status': 'filled', 'filled_avg_price': level}
                else:
                    reason = confirmation.get('reason', 'unknown')
                    print(f"❌ IG order REJECTED: {deal_status} — {reason}")
                    return None
            else:
                print(f"⚠️ Could not confirm deal {deal_ref}")
                return None

        except Exception as e:
            print(f"❌ IG {direction} order failed: {e}")
            return None

    def place_order(self, symbol, side, quantity, order_type='market', price=None, stop_loss=None, take_profit=None, **kwargs):
        """
        Unified interface matching PaperTrader/LiveBroker signature.
        """
        if side.lower() == 'buy':
            return self.buy(price=price or 0.0, size=quantity, stop_loss=stop_loss, take_profit=take_profit)
        elif side.lower() == 'sell':
            return self.sell(price=price or 0.0, size=quantity, stop_loss=stop_loss, take_profit=take_profit)
        else:
            print(f"Error: Unknown side {side}")
            return None
