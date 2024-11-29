import configparser
import os
import time
from datetime import datetime
from stellar_sdk import Server, Keypair, TransactionBuilder, Network, Asset, exceptions
import schedule

# Configuration
config = configparser.ConfigParser()
config.read('config.txt')

DISTRIBUTOR_SECRET_KEY = config['DEFAULT']['DISTRIBUTOR_SECRET_KEY']
INTERVAL_HOURS = float(config['DEFAULT'].get('INTERVAL_HOURS', 3))

# Constants
RECEIVER_ADDRESS = "GDPQWQ37LPPLJJ4SWG5KMHEISATFMD4QTZFWN25UGGHFJ34BY5WTT3DN"
NETWORK_PASSPHRASE = Network.PUBLIC_NETWORK_PASSPHRASE
HORIZON_URL = "https://horizon.stellar.org"

# Stellar SDK Setup
server = Server(HORIZON_URL)
distributor_keypair = Keypair.from_secret(DISTRIBUTOR_SECRET_KEY)

def send_payment(amount):
    """Send native XLM to the specified receiver."""
    try:
        # Load the distributor's account
        distributor_account = server.load_account(distributor_keypair.public_key)

        # Fetch the base fee
        base_fee = server.fetch_base_fee()

        # Build the transaction
        transaction = (
            TransactionBuilder(
                source_account=distributor_account,
                network_passphrase=NETWORK_PASSPHRASE,
                base_fee=base_fee
            )
            .append_payment_op(
                destination=RECEIVER_ADDRESS,
                amount=str(amount),
                asset=Asset.native()
            )
            .set_timeout(100)
            .build()
        )

        # Sign and submit the transaction
        transaction.sign(distributor_keypair)
        response = server.submit_transaction(transaction)

        if response.get('successful', False):
            print(f"Transaction to {RECEIVER_ADDRESS} for {amount} XLM: Success")
        else:
            print(f"Transaction failed: {response}")
    except Exception as e:
        print(f"Error sending payment: {e}")

def job():
    """Scheduled job to send payment."""
    try:
        amount = 0.0001  # Set the amount of XLM to send
        print(f"Starting transaction at {datetime.now()}")
        send_payment(amount)
    except Exception as e:
        print(f"An error occurred during the job: {e}")

# Schedule the job
schedule.every(INTERVAL_HOURS).hours.do(job)

# Run the job immediately
job()

# Keep the bot running
while True:
    schedule.run_pending()
    time.sleep(1)
