import os
import sys
import argparse
import multiprocessing
import logging
from concurrent.futures import ProcessPoolExecutor

def run_hulk(root_ip):
    import hulk  # Import hulk module here to avoid potential circular imports
    try:
        hulk.main(root_ip)  # Assuming hulk.py has a main function that takes root_ip as an argument
    except Exception as e:
        logging.exception(f"Error in hulk process: {e}")

def main():
    parser = argparse.ArgumentParser(description="Run multiple instances of hulk.py")
    parser.add_argument("--root_ip", default="localhost", help="Root IP address")
    parser.add_argument("--processes", type=int, default=os.cpu_count(), help="Number of processes to spawn")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    logging.info(f"Starting {args.processes} processes with root IP: {args.root_ip}")

    with ProcessPoolExecutor(max_workers=args.processes) as executor:
        futures = [executor.submit(run_hulk, args.root_ip) for _ in range(args.processes)]

        try:
            for future in futures:
                future.result()  # This will raise any exceptions from the processes
        except KeyboardInterrupt:
            logging.info("Interrupt received, shutting down...")
            executor.shutdown(wait=False, cancel_futures=True)
        except Exception as e:
            logging.exception(f"An error occurred: {e}")
        finally:
            logging.info("All processes completed or terminated")

if __name__ == "__main__":
    multiprocessing.freeze_support()  # For Windows support
    main()
