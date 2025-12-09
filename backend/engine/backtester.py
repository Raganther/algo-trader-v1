
import pandas as pd
from .strategy import Strategy
from .paper_trader import PaperTrader

class Backtester:
    def __init__(self, data, strategy_class, parameters=None, initial_capital=10000.0, spread=0.0, execution_delay=0, interval="1d"):
        self.data = data
        self.strategy_class = strategy_class
        self.parameters = parameters or {}
        self.initial_capital = initial_capital
        self.spread = spread
        self.execution_delay = execution_delay
        self.interval = interval
        # Reset Broker
        self.broker = PaperTrader(initial_capital=self.initial_capital, spread=self.spread)
        
        # Reset Strategy
        self.strategy = self.strategy_class(self.data, None, self.parameters, self.initial_capital, self.broker)
        self.results = {}

    def run(self):
        """
        Run the backtest simulation using PaperTrader.
        """
        # Initialize Paper Trader (Broker)
        # Initialize Paper Trader (Broker)
        # Check if spread is in parameters, default to 0.0
        spread = self.parameters.get('spread', 0.0)
        # Use self.spread if set in init, otherwise param
        if self.spread != 0.0:
            spread = self.spread
            
        self.broker = PaperTrader(initial_capital=self.initial_capital, spread=spread)
        
        # Initialize Strategy with Broker
        self.strategy = self.strategy_class(self.data, None, self.parameters, self.initial_capital, self.broker)
        
        # Convert to list for lookahead capability
        data_list = list(self.data.iterrows())
        
        # Simulation loop
        for i in range(len(data_list)):
            index, row = data_list[i]
            
            # 1. Update Broker with current price
            # We need the symbol. It's in parameters or metadata?
            # Strategy parameters usually have 'symbol'.
            symbol = self.parameters.get('symbol', 'Unknown')
            current_price = row['Close']
            self.broker.update_price(symbol, current_price)
            
            # 2. Check for economic events
            if self.strategy.events is not None and not self.strategy.events.empty:
                days_events = self.strategy.events[self.strategy.events['date'].dt.date == index.date()]
                for _, event_row in days_events.iterrows():
                    self.strategy.on_event(event_row)
            
            # 3. Call strategy on_data to generate signals
            # Strategy will call broker.place_order() internally
            # Execution Logic with Delay
            # If delay=0, we execute at 'i' (Close of current bar)
            # If delay=1, we execute at 'i' but using price from 'i+1' (Open of next bar) - Wait, this logic is tricky.
            # Standard Backtest Loop:
            # for i in range(len(data)):
            #   strategy.on_bar(data.iloc[i]) -> generates signal
            #   broker.execute(signal) -> fills at data.iloc[i]['Close'] (if Market)
            
            # To simulate Next Open:
            # We need to fill at data.iloc[i+1]['Open'].
            # But the loop is at 'i'. We can't see 'i+1' yet?
            # Actually, in a vectorized backtest we can. In event-driven, we can't.
            # But here we are iterating.
            # Option A: Strategy generates signal at 'i'. Broker queues it. Next iteration 'i+1', Broker fills it at 'Open'.
            # Option B (Cheat): We peek ahead. fill_price = data.iloc[i+execution_delay]['Open']
            
            # Let's use Option B for simplicity in this 'Backtester' class which seems to be a hybrid.
            # But wait, if we are at the last bar, we can't peek ahead.
            
            current_row = self.data.iloc[i]
            
            # Update Broker Price (for valuation)
            # self.broker.update_price(current_row['Close']) # If we had this method
            
            # Run Strategy Logic
            self.strategy.on_data(i, current_row)
            
            # Execution Logic (Simulated)
            # In this simple engine, the strategy calls broker.buy/sell directly.
            # To support delay without changing strategy code, we need to hack the execution price.
            # But the strategy passes the price explicitly! self.buy(price=row['Close'])
            
            # Wait, if we want to simulate "Next Open", we must ignore the price passed by the strategy
            # and use the Next Open price instead.
            
            if self.execution_delay > 0:
                # Check if we have orders to fill (that were just placed by on_data)
                # The PaperTrader executes immediately, so the orders are already filled at the wrong price!
                # This architecture makes it hard to intercept.
                
                # REFACTOR: We need to tell the Broker to use a different price.
                # But the Broker doesn't know about future data.
                
                # Alternative: We pass the "Next Open" price TO the strategy?
                # No, strategy logic shouldn't change.
                
                # Correct Approach for this Architecture:
                # We need to retroactively adjust the fill price of the last trade? No, messy.
                
                # Let's use the "Peek Ahead" approach but applied to the Broker.
                # We can set a "next_execution_price" on the broker before calling on_data.
                # If delay=1, next_execution_price = data[i+1]['Open'].
                # The Broker, when receiving an order, uses this price instead of the one passed?
                
                if i + self.execution_delay < len(self.data):
                    next_price = self.data.iloc[i + self.execution_delay]['Open']
                    self.broker.set_execution_override(next_price)
                else:
                    self.broker.set_execution_override(None)
            else:
                self.broker.set_execution_override(None)
            
            # Note: PaperTrader (MVP) executes immediately on place_order.
            # So we don't need a separate execution loop here for now.
            # In a more complex version, we'd call self.broker.process_orders() here.
            
            # Record Daily Equity (Mark-to-Market)
            # We want to capture the equity curve over time
            current_time = index
            current_equity = self.broker.get_equity()
            
            # For efficiency, maybe only record daily? 
            # But the loop runs on 'self.interval'. If 1h, we get hourly equity. That's fine.
            if self.interval == "1d":
                time_val = index.strftime('%Y-%m-%d')
            else:
                time_val = int(index.timestamp())
                
            # We store it in a list to be included in results
            if not hasattr(self, 'equity_history'):
                self.equity_history = []
            
            self.equity_history.append({
                "time": time_val,
                "equity": round(current_equity, 2)
            })
            
        self._calculate_results()
        return self.results

    def _calculate_results(self):
        """
        Calculate performance metrics from PaperTrader.
        """
        final_equity = self.broker.get_equity()
        return_pct = ((final_equity - self.initial_capital) / self.initial_capital) * 100
        
        # Get orders from broker
        # PaperTrader stores orders in self.broker.orders
        processed_orders = self.broker.orders

        # Format chart data based on interval
        chart_data = []
        for index, row in self.data.iterrows():
            if self.interval == "1d":
                time_val = index.strftime('%Y-%m-%d')
            else:
                # For intraday, use Unix timestamp
                time_val = int(index.timestamp())
            
            chart_data.append({
                "time": time_val,
                "open": row['Open'],
                "high": row['High'],
                "low": row['Low'],
                "close": row['Close']
            })

        # Calculate Trade Metrics (Win Rate, Avg Win/Loss)
        filled_orders = [o for o in processed_orders if o['status'] == 'filled']
        
        # Simple Trade Matching (FIFO)
        # We assume every 2 orders form a trade (Open -> Close) for this simple strategy
        # This is valid because the strategy only holds 1 position at a time.
        trades = []
        pnl_list = []
        
        # We need to look at the PaperTrader's trade_history if available, 
        # as it tracks realized PnL per trade.
        if hasattr(self.broker, 'trade_history') and self.broker.trade_history:
            for t in self.broker.trade_history:
                pnl = t['pnl']
                pnl_list.append(pnl)
                trades.append(t)
        
        winning_trades = [p for p in pnl_list if p > 0]
        losing_trades = [p for p in pnl_list if p <= 0]
        
        win_rate = (len(winning_trades) / len(trades)) if trades else 0.0
        avg_win = sum(winning_trades) / len(winning_trades) if winning_trades else 0.0
        avg_loss = sum(losing_trades) / len(losing_trades) if losing_trades else 0.0
        
        profit_factor = abs(sum(winning_trades) / sum(losing_trades)) if losing_trades and sum(losing_trades) != 0 else 0.0
        
        # Calculate Max Drawdown (Closed Trade Equity)
        equity_curve = [self.initial_capital]
        current_equity = self.initial_capital
        peak_equity = self.initial_capital
        max_drawdown = 0.0
        
        for pnl in pnl_list:
            current_equity += pnl
            equity_curve.append(current_equity)
            
            if current_equity > peak_equity:
                peak_equity = current_equity
            
            drawdown = (peak_equity - current_equity) / peak_equity
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                
        max_drawdown_pct = max_drawdown * 100

        self.results = {
            "initial_capital": self.initial_capital,
            "final_equity": round(final_equity, 2),
            "total_trades": len(trades),
            "return_pct": round(return_pct, 2),
            "win_rate": round(win_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(profit_factor, 2),
            "max_drawdown": round(max_drawdown_pct, 2),
            "equity_curve": getattr(self, 'equity_history', []), # Use the detailed history
            "orders": processed_orders,
            "trade_history": trades,
            "debug_history": getattr(self.strategy, 'debug_history', []),
            "chart_data": chart_data
        }
