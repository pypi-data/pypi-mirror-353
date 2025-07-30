import sys
import os
import multiprocessing
from stocksim.simulation import simulate_batch

def simulate_batch_unpack(args):
    return simulate_batch(*args)

def main():
    import warnings
    warnings.filterwarnings("ignore", category=UserWarning, module="pkg_resources")
    warnings.filterwarnings("ignore")

    multiprocessing.freeze_support()
    if hasattr(multiprocessing, "set_start_method"):
        try:
            multiprocessing.set_start_method("spawn")
        except RuntimeError:
            pass

    import argparse
    import re
    import numpy as np
    import yfinance as yf
    import concurrent.futures
    import math
    import time

    # Optional: Detect system RAM
    try:
        import psutil
        def get_system_ram_gb():
            return psutil.virtual_memory().total / (1024 ** 3)
    except ImportError:
        psutil = None
        def get_system_ram_gb():
            return None

    def fetch_crypto_data(symbol, period=None, interval="1d"):
        data = yf.download(
            symbol, period=period, interval=interval, progress=False, auto_adjust=True
        )
        if "Adj Close" in data.columns:
            prices = data["Adj Close"]
        elif "Close" in data.columns:
            prices = data["Close"]
        else:
            raise ValueError(f"No price data found for {symbol}.")
        prices = prices.dropna()
        if prices.empty:
            raise ValueError(f"No valid price data available for {symbol} after dropping NA.")
        return prices

    def compute_annualized_return_and_volatility(prices):
        log_returns = np.log(prices / prices.shift(1)).dropna()
        mean_daily = float(log_returns.mean())
        std_daily = float(log_returns.std())
        mean_annual = mean_daily * 252
        std_annual = std_daily * np.sqrt(252)
        return mean_annual, std_annual

    def get_cpu_count():
        try:
            import psutil
            count = psutil.cpu_count(logical=True)
        except ImportError:
            try:
                import os
                count = os.cpu_count()
            except Exception:
                count = 1
        return max(1, (count or 1) - 1)

    def get_ram_fraction(simsize):
        if simsize == "large":
            return 0.70
        elif simsize == "medium":
            return 0.50
        else:
            return 0.25

    def get_max_ram_gb():
        sys_ram = get_system_ram_gb()  # however you detect system RAM
        if sys_ram:
            return min(sys_ram, 2048)  # cap at 2TB for sanity
        else:
            print(
                "WARNING: System RAM could not be detected after several attempts.\n"
                "Using default values: 8GB for small, 16GB for medium, 32GB for large simulations."
            )
            return 32.0  # fallback

    def monte_carlo_simulation(
        start_price, mean_return, volatility, years=1, percent_step=3, max_gb=4, n_workers=None, total_simulations=None
    ):
        import numpy as np
        import time
        import concurrent.futures

        ram_gb = get_max_ram_gb()
        ram_fraction = get_ram_fraction(args.simsize)
        usable_bytes = int(ram_gb * 1024**3 * ram_fraction)

        usable_bytes = int(max_gb * 1024**3 * 0.7)  # Always use 70% of allowed RAM
        n_steps = int(252 * years)
        float_bytes = 4  # np.float32

        def estimate_batch_bytes(batch_size):
            return int((2 * batch_size * n_steps * float_bytes + batch_size * float_bytes) * 1.2)

        # Find the largest total_simulations that fits in usable_bytes
        if total_simulations is not None:
            if estimate_batch_bytes(total_simulations) > usable_bytes:
                left, right = 1000, total_simulations
                best_total_batch_size = 1000
                while left <= right:
                    mid = (left + right) // 2
                    if estimate_batch_bytes(mid) <= usable_bytes:
                        best_total_batch_size = mid
                        left = mid + 1
                    else:
                        right = mid - 1
                total_simulations = best_total_batch_size
                print(f"WARNING: Requested simulations exceeds available RAM. Running {total_simulations:,} simulations (max for 70% of available RAM).")
            else:
                print(f"INFO: Running {total_simulations:,} simulations as requested.")
        else:
            left, right = 1000, int(1e9)
            best_total_batch_size = 1000
            while left <= right:
                mid = (left + right) // 2
                if estimate_batch_bytes(mid) <= usable_bytes:
                    best_total_batch_size = mid
                    left = mid + 1
                else:
                    right = mid - 1
            total_simulations = best_total_batch_size
            print(f"INFO: Running {total_simulations:,} simulations (max for 70% of available RAM).")

        n_workers = max(1, n_workers or 1)
        # Divide simulations as evenly as possible among workers
        base_batch_size = total_simulations // n_workers
        batch_sizes = [base_batch_size] * n_workers
        for i in range(total_simulations % n_workers):
            batch_sizes[i] += 1

        est_bytes_total = estimate_batch_bytes(total_simulations)
        est_bytes_per_worker = [estimate_batch_bytes(bs) for bs in batch_sizes]

        print(f"The computer is NOT frozen. Running {total_simulations:,} simulations for {years} year(s).")
        print(f"Estimated RAM used (total): {est_bytes_total / (1024 ** 3):.2f} GB (plus overhead).")
        print(f"Using {n_workers} CPU core(s) for parallel processing.")

        # Prepare arguments for each worker
        batch_args = [
            (start_price, mean_return, volatility, years, bs)
            for bs in batch_sizes
        ]

        start_time = time.time()

        total_count = 0
        gain_count = 0
        min_price = float('inf')
        max_price = float('-inf')
        median_candidates = []

        MEDIAN_SAMPLE_SIZE = 1_000_000

        completed = 0
        percent_last = 0

        with concurrent.futures.ProcessPoolExecutor(max_workers=n_workers) as executor:
            results = executor.map(simulate_batch_unpack, batch_args)
            for batch_result in results:
                batch_len = len(batch_result)
                completed += batch_len

                gain_count += np.sum(batch_result > start_price)
                min_price = min(min_price, float(np.min(batch_result)))
                max_price = max(max_price, float(np.max(batch_result)))
                if len(median_candidates) < MEDIAN_SAMPLE_SIZE:
                    needed = MEDIAN_SAMPLE_SIZE - len(median_candidates)
                    if batch_len <= needed:
                        median_candidates.extend(batch_result)
                    else:
                        median_candidates.extend(np.random.choice(batch_result, needed, replace=False).astype(np.float32))
                total_count += batch_len

                percent_now = int(completed * 100 / total_simulations)
                if percent_now // percent_step > percent_last // percent_step:
                    elapsed = time.time() - start_time
                    est_total = elapsed / (percent_now / 100) if percent_now > 0 else 0
                    est_left = est_total - elapsed if percent_now > 0 else 0
                    print(f"\r{percent_now}% complete - Elapsed: {elapsed:.1f}s, Est. left: {est_left:.1f}s", end='', flush=True)
                    percent_last = percent_now

        total_time = time.time() - start_time
        print()  # Move to the next line after progress
        print(f"Simulation complete! Total time: {total_time:.1f} seconds.")
        print("Processing results... (Your PC is NOT frozen, please wait while results are processed.)")

        median_ending = float(np.median(median_candidates)) if median_candidates else float('nan')
        prob_gain = gain_count / total_count if total_count else float('nan')

        print(f"Total simulations run: {total_count:,}")
        print(f"Number of CPU core(s) used: {n_workers}")
        print(f"Average batch size: {int(np.mean(batch_sizes)):,}")

        return {
            "prob_gain": prob_gain,
            "median_ending": median_ending,
            "min_price": min_price,
            "max_price": max_price,
            "total_count": total_count
        }

    def show_summary(ending_stats, start_price, years, symbol):
        prob_gain = ending_stats["prob_gain"]
        median_ending = ending_stats["median_ending"]
        min_price = ending_stats["min_price"]
        max_price = ending_stats["max_price"]
        try:
            current_price = float(yf.Ticker(symbol).history(period="1d")["Close"][-1])
        except Exception:
            current_price = start_price
        percent_gain = ((median_ending - current_price) / current_price) * 100 if current_price else float('nan')
        print(f"\n--- Results for {symbol} after {years} year(s) ---")
        print(f"Probability {symbol} gains value: {prob_gain:.2%}")
        print(f"Median simulated ending price (estimated): ${median_ending:,.2f}")
        print(f"Min/Max simulated ending price: ${min_price:,.2f} / ${max_price:,.2f}")
        print(f"Total percent gain from today's price (${current_price:,.2f}) to median simulated ending price: {percent_gain:.2f}%")

    def input_with_timeout(prompt, timeout):
        import msvcrt
        sys.stdout.write(prompt)
        sys.stdout.flush()
        start_time = time.time()
        input_str = ''
        while True:
            if msvcrt.kbhit():
                char = msvcrt.getwche()
                if char in ('\r', '\n'):
                    sys.stdout.write('\n')
                    return input_str
                elif char == '\003':
                    raise KeyboardInterrupt
                elif char == '\b':
                    input_str = input_str[:-1]
                    sys.stdout.write('\b \b')
                else:
                    input_str += char
            if (time.time() - start_time) > timeout:
                print("\nNo input detected. Defaulting to 5 years of historical data.")
                return ''
            time.sleep(0.05)

    parser = argparse.ArgumentParser(
        description="Monte Carlo Simulation for Crypto Price Gain Probability"
    )
    parser.add_argument(
        "--symbol",
        type=str,
        required=False,
        help="Ticker symbol (e.g., BTC-USD, ETH-USD, AAPL, SPX:IND, EURUSD:CUR)"
    )
    parser.add_argument(
        "--years",
        type=float,
        required=False,
        help="Investment period in years (e.g., 1)"
    )
    parser.add_argument(
        "--simsize",
        type=str,
        choices=["small", "medium", "large"],
        required=False,
        help="Simulation size: small, medium, or large"
    )
    args = parser.parse_args()

    print(
        "\nMonte Carlo Stock/Crypto Price Simulation Tool\n"
        "------------------------------------------------\n"
        "This program estimates the probability that a stock, cryptocurrency, or index will gain value\n"
        "over a chosen investment period using a Monte Carlo simulation based on historical price data.\n"
        "You can enter any ticker supported by Yahoo Finance (e.g., BTC-USD, AAPL, EURUSD=X).\n"
        "The simulation uses your system's CPU and RAM efficiently to run millions of price scenarios,\n"
        "and provides the probability of gain, median outcome, and min/max simulated prices.\n"
    )

    print("You can exit the program at any time by typing 'exit' and pressing Enter.")

    while True:
        if not args.symbol:
            symbol_input = input("Enter ticker (e.g., BTC-USD, ETH-USD, AAPL, MSFT, EURUSD=X, GC=F, SPX:IND): ").strip()
            if symbol_input.lower() == "exit":
                print("Exit requested. Terminating program immediately...")
                os._exit(0)
            symbol_input = symbol_input.upper()
        else:
            symbol_input = args.symbol.strip().upper()
        if symbol_input.lower() == "exit":
            print("Exit requested. Terminating program immediately...")
            os._exit(0)
        yf_pattern = r"^\^?[A-Z0-9][A-Z0-9\-\.=]{0,14}$"
        bloomberg_pattern = r"^[A-Z0-9]{1,7}:[A-Z]{1,8}$"
        tv_pattern = r"^[A-Z0-9][A-Z0-9\-\.=:]{0,14}$"
        original_input = symbol_input
        if re.fullmatch(bloomberg_pattern, symbol_input):
            bloomberg_map = {
                "SPX:IND": "^GSPC",
                "NDX:IND": "^NDX",
                "DJI:IND": "^DJI",
                "RUT:IND": "^RUT",
                "VIX:IND": "^VIX",
                "UKX:IND": "^FTSE",
                "DAX:IND": "^GDAXI",
                "HSI:IND": "^HSI",
                "SENSEX:IND": "^BSESN",
                "NIFTY:IND": "^NSEI",
            }
            if symbol_input in bloomberg_map:
                symbol_input = bloomberg_map[symbol_input]
            elif symbol_input.endswith(":CUR"):
                symbol_input = symbol_input.replace(":CUR", "=X")
            elif symbol_input.endswith(":US"):
                symbol_input = symbol_input.replace(":US", "")
        elif re.fullmatch(tv_pattern, symbol_input):
            if ":CUR" in symbol_input:
                symbol_input = symbol_input.replace(":CUR", "=X")
            elif symbol_input.endswith("USD") and "-" not in symbol_input and len(symbol_input) > 6:
                symbol_input = symbol_input[:-3] + "-" + symbol_input[-3:]
        if not re.fullmatch(yf_pattern, symbol_input):
            print("ERROR: Invalid input. Please enter a valid ticker symbol as used by Yahoo Finance, Bloomberg, or TradingView (e.g., BTC-USD, ETH-USD, AAPL, MSFT, EURUSD=X, GC=F, SPX:IND, EURUSD:CUR).")
            args.symbol = None
            continue

        while True:
            lookback_input = input_with_timeout(
                "How many years of historical data do you want to use for this simulation? (Recommended: 5, Max: 20 if available): ",
                10
            ).strip()
            if lookback_input == "":
                lookback_years = 5
                break
            if lookback_input.lower() == "exit":
                print("Exit requested. Terminating program immediately...")
                os._exit(0)
            try:
                lookback_years = int(lookback_input)
                if not (1 <= lookback_years <= 20):
                    raise ValueError
                break
            except ValueError:
                print("Invalid input. Please enter a number between 1 and 20, or press Enter for default (5 years).")

        try:
            prices = fetch_crypto_data(symbol_input, period=f"{lookback_years}y")
        except Exception:
            print(f"ERROR: Invalid input. Ticker '{original_input}' (converted to '{symbol_input}') not found on Yahoo Finance or no data available. Please try again.")
            args.symbol = None
            continue

        if len(prices) == 0:
            print("ERROR: No price data available. Please try another ticker.")
            args.symbol = None
            continue

        args.symbol = symbol_input
        break

    # Prompt for years if not provided
    while args.years is None:
        years_input = input("Enter investment period in years (e.g., 1): ").strip()
        if years_input.lower() == "exit":
            print("Exit requested. Terminating program immediately...")
            os._exit(0)
        try:
            args.years = float(years_input)
            if args.years <= 0:
                raise ValueError
            if args.years != int(args.years):
                print("WARNING: For best results, use whole numbers for years (e.g., 1, 2, 5).")
            args.years = int(args.years)
            break
        except ValueError:
            print("Invalid input. Please enter a positive number for years, or type 'exit' to quit.")

    # Determine simulation size and RAM allocation
    if args.simsize is None:
        while True:
            simsize_input = input("Enter simulation size (small, medium, or large): ").strip().lower()
            if simsize_input.lower() == "exit":
                print("Exit requested. Terminating program immediately...")
                os._exit(0)
            if simsize_input in ["small", "medium", "large"]:
                args.simsize = simsize_input
                break
            else:
                print("Invalid input. Please enter small, medium, or large for simulation size.")

    # Calculate mean return and volatility for the selected symbol and period
    try:
        mean_return, volatility = compute_annualized_return_and_volatility(prices)
    except Exception as e:
        print(f"ERROR: Error calculating return and volatility: {e}")
        return

    cpu_cores = get_cpu_count()
    max_ram_large = get_max_ram_gb("large")
    ram_gb = get_max_ram_gb()

    n_workers = max(1, get_cpu_count())

    # Set base number of simulations by simsize (doubled)
    base_simulations = 1231225 * 2
    if args.simsize == "large":
        requested_simulations = base_simulations * 3
    elif args.simsize == "medium":
        requested_simulations = base_simulations * 2
    else:
        requested_simulations = base_simulations

    # For "large", always maximize up to RAM limit
    def estimate_batch_bytes(batch_size):
        n_steps = int(252 * args.years)
        float_bytes = 4  # np.float32
        return int((2 * batch_size * n_steps * float_bytes + batch_size * float_bytes) * 1.2)

    if args.simsize == "large":
        # Find the largest total_batch_size that fits in usable_bytes (all RAM)
        left, right = 1000, requested_simulations
        best_total_batch_size = 1000
        usable_bytes = int(ram_gb * 1024**3 * 0.7)
        while left <= right:
            mid = (left + right) // 2
            if estimate_batch_bytes(mid) <= usable_bytes:
                best_total_batch_size = mid
                left = mid + 1
            else:
                right = mid - 1
        total_simulations = best_total_batch_size
        if total_simulations < requested_simulations:
            print(f"WARNING: Requested {requested_simulations:,} simulations exceeds available RAM. Running {total_simulations:,} simulations (max for 70% of available RAM).")
        else:
            print(f"INFO: Running {total_simulations:,} simulations as requested.")
    else:
        total_simulations = requested_simulations

    # Display settings
    print("\n--- Settings ---")
    print(f"Symbol: {args.symbol}")
    time.sleep(0.2)
    print(f"Years: {args.years}")
    time.sleep(0.2)
    print(f"Simulation Size: {args.simsize}")
    time.sleep(0.2)
    print("Detecting system RAM...")
    time.sleep(1)
    print(f"Max system RAM available for use: {max_ram_large:.2f} GB")
    time.sleep(0.2)
    print(f"CPU cores allocated for simulation: {cpu_cores}")
    time.sleep(0.2)
    print(f"Detected Annualized Return: {mean_return * 100:.2f}%")
    time.sleep(0.2)
    print(f"Detected Annualized Volatility: {volatility * 100:.2f}%")
    time.sleep(0.2)
    print(f"Number of Data Points Used: {len(prices)}")
    time.sleep(0.2)
    print(f"Price Data Range: {prices.index[0].date()} to {prices.index[-1].date()}")
    time.sleep(0.2)
    last_close = prices.iloc[-1]
    if hasattr(last_close, "item"):
        last_close = last_close.item()

    print(f"Last Closing Price: ${float(last_close):,.2f}")
    time.sleep(0.5)

    # Run Monte Carlo simulation
    ending_prices = monte_carlo_simulation(
        start_price=float(last_close),
        mean_return=mean_return,
        volatility=volatility,
        years=args.years,
        max_gb=ram_gb,
        n_workers=cpu_cores,
        total_simulations=total_simulations,  # <-- add this
    )

    # Show summary of results
    show_summary(ending_prices, float(last_close), args.years, args.symbol)
    print("\nThank you for using the Monte Carlo Simulation tool.\n")

if __name__ == "__main__":
    main()