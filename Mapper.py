#!/usr/bin/env python3
import sys

# Mapper function
def mapper():
    for line in sys.stdin:
        # Ignore the header row
        if "Open_time" in line:
            continue
        
        # Split the line into fields
        fields = line.strip().split(',')
        open_time, open_price, high, low, close, volume = fields[0], fields[1], fields[2], fields[3], fields[4], fields[5]

        # Emit necessary data for VWAP, RSI, and MA
        try:
            open_price = float(open_price)
            high = float(high)
            low = float(low)
            close = float(close)
            volume = float(volume)

            # Output for VWAP (Price * Volume, Volume)
            print(f"VWAP\t{(high + low + close) / 3 * volume}\t{volume}")

            # Output for MA (Closing price for moving average)
            print(f"MA\t{close}")

            # Output for RSI (Calculate change and flag for gain/loss)
            print(f"RSI\t{close}\t{open_time}")

        except ValueError:
            continue

if __name__ == "__main__":
    mapper()
