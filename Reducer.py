#!/usr/bin/env python3
import sys
import datetime

# Initialize variables for VWAP, MA, and RSI calculations
total_price_volume = 0
total_volume = 0
price_list = []  # For MA calculation (closing prices)
gains_list = []  # For RSI calculation
losses_list = []  # For RSI calculation
previous_close = None
n_period = 14  # Period for RSI and MA

def calculate_ma(prices, period):
    """Calculate Moving Average (MA) over a period."""
    if len(prices) >= period:
        return sum(prices[-period:]) / period, prices[-period:]  # Return the list of used prices as well
    return None, []

def calculate_rsi(gains, losses, period):
    """Calculate RSI over a period."""
    if len(gains) >= period and len(losses) >= period:
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        rs = avg_gain / avg_loss if avg_loss != 0 else 0  # Avoid division by zero
        rsi = 100 - (100 / (1 + rs))
        return rsi, gains[-period:], losses[-period:]  # Return the list of used gains and losses as well
    return None, [], []

def timestamp_to_date(timestamp):
    """Convert timestamp in milliseconds to a readable date format."""
    return datetime.datetime.utcfromtimestamp(int(timestamp) / 1000).strftime('%Y-%m-%d %H:%M:%S')

def reducer():
    global total_price_volume, total_volume, price_list, gains_list, losses_list, previous_close

    for line in sys.stdin:
        line = line.strip()
        # Skip empty lines
        if not line:
            continue

        # Split the line into components
        parts = line.split('\t')
        if len(parts) < 2:
            continue

        key = parts[0]
        value1 = parts[1]

        # Extract additional values
        values = parts[2:]  # Remaining parts
        date = values[0] if len(values) > 0 else "unknown_date"  # Default date if not present

        if key == "VWAP":
            try:
                price_volume = float(value1)
                volume = float(values[0]) if len(values) > 0 else 0
                total_price_volume += price_volume
                total_volume += volume
            except ValueError:
                continue

        elif key == "MA" or key == "RSI":
            try:
                close_price = float(value1)
                price_list.append(close_price)

                # Calculate gains and losses for RSI
                if previous_close is not None:
                    change = close_price - previous_close
                    if change > 0:
                        gains_list.append(change)
                        losses_list.append(0)
                    else:
                        gains_list.append(0)
                        losses_list.append(abs(change))
                previous_close = close_price

                # Limit the lists to n_period
                if len(price_list) > n_period:
                    price_list.pop(0)
                if len(gains_list) > n_period:
                    gains_list.pop(0)
                if len(losses_list) > n_period:
                    losses_list.pop(0)

                # Calculate MA and RSI for the current point
                ma, ma_values = calculate_ma(price_list, n_period)
                rsi, rsi_gains, rsi_losses = calculate_rsi(gains_list, losses_list, n_period)

                if ma is not None and rsi is not None:
                    date = timestamp_to_date(date)  # Convert timestamp to date
                    vwap_value = total_price_volume / total_volume if total_volume > 0 else 0
                    # Print the results
                    print(f"{date},{vwap_value},{ma},{rsi},{','.join(map(str, ma_values))},{','.join(map(str, rsi_gains))},{','.join(map(str, rsi_losses))}")

            except ValueError:
                continue

if __name__ == "__main__":
    reducer()
