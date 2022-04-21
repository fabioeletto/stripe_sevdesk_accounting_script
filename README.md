# Stripe sevDesk accounting script
Automated booking of stripe payout invoices in sevDesk

## Motivation
I am co-founder of a software company and we sell our product for a monthly amount. Since the process to book a Stripe invoice in sevDesk is always the same, I came up with the idea to automate the whole process to minimize errors and to save time.

__Main tasks of the script:__
- Download the invoices from Stripe
- Create a new voucher for each invoice in sevDesk with:
  - correct metadata (customer, amount, date, ...)
  - VAT from the customers country
  - discounts if applicable
- Book vouchers to the corresponding transaction in sevDesk

## Setup
__Required Python version 3.8__
1. Clone the Git repository (and install Python if you don't have it already)
2. Create a __.env__ file in the root directory and add the following properties
    ```
    STRIPE_API_KEY=<YOUR_STRIPE_API_KEY>
    SEVDESK_API_KEY=<YOUR_SEVDESK_API_KEY>
    ```
3. Install the required packages
   ```
    pip install -r requirements.txt
   ```
4. Run the script
   ```
   python3 main.py
   ```
    *To stop the script use __CTRL + C__*

## Usage
After the script has started, you will be prompted to select a Stripe payout which should be booked to sevDesk. Then you need to select the corresponding sevDesk account that receives your Stripe payouts.

The script will try to create a new voucher for each individual invoice and book it to the corresponding transaction in sevDesk.

When the script has finished, a folder will be created where you can find additional information about the process.

__"additional_info"__ folder contains
- "printed_logs.txt" - output of all printed console logs
- "already_processed_payout_ids.txt" - list of already processed payout ids
- payout folder
  - "errors.txt" - logs errors during the accounting process
  - other payout resource types (like refunds, fees, adjustments, ...) which could not be booked automatically. You have to book these manually



## Resources
- [Stripe API](https://stripe.com/docs/api?lang=python)
- [sevDesk voucher API](https://my.sevdesk.de/api/ReceiptAPI/doc.html)
- [Where do I find my Stripe API-Key?](https://stripe.com/docs/keys#obtain-api-keys)
- [Where do I find my sevDesk API-Key? [GER]](https://hilfe.sevdesk.de/de/knowledge/wo-finde-ich-meinen-api-token-in-sevdesk)
