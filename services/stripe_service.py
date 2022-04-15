from datetime import datetime
import os
import stripe
import requests
from dotenv import load_dotenv

from services.sevdesk_service import SevDeskService

from helpers.file_helper import FileHelper
from helpers.constants import (
    TMP_DOWNLOADED_INVOICE_FOLDER_PATH,
    PROCESSED_PAYOUTS_FILE_PATH
)

from view_models.result_view_model import ResultViewModel
from view_models.accounting_result_view_model import AccountingResultViewModel

# TODO Create an user input to chose a date when the payouts should displayed
# Sun May 02 2021 18:12:42 GMT+0000
STRIPE_PAYOUTS_UNIX_TIMESTAMP = 1619979162


class StripeService:
    """Stripe service"""
    def __init__(self):
        load_dotenv()
        stripe.api_key = os.getenv("STRIPE_API_KEY")
        FileHelper.create_directory(TMP_DOWNLOADED_INVOICE_FOLDER_PATH)
        self.formatted_payouts = {}
        self.sev_desk_service = SevDeskService()

    # add already processed payout ids as parameter and check
    def get_formatted_payouts(self):
        """Get formatted stripe payouts"""
        payouts = stripe.Payout.list(limit=10)

        # Get already processed payout ids
        processed_payout_ids = FileHelper.read_from_file(
            PROCESSED_PAYOUTS_FILE_PATH
        )

        for payout in payouts.auto_paging_iter():
            if (
                payout.id not in processed_payout_ids
                and payout.arrival_date > STRIPE_PAYOUTS_UNIX_TIMESTAMP
            ):
                arrival_date = datetime.fromtimestamp(int(payout.arrival_date)).strftime("%d.%m.%Y")
                self.formatted_payouts[f"{payout.amount / 100}€_From_{arrival_date}"] = payout.id

        return self.formatted_payouts

    def start_accounting(self, payout_id, account_id):
        """Main accounting method"""
        payout_name = list(self.formatted_payouts.keys())[
            list(self.formatted_payouts.values()).index(payout_id)
        ]
        accounting_result_view_model = AccountingResultViewModel(
            payout_id,
            payout_name
        )

        balance_transactions = stripe.BalanceTransaction.list(
            payout=payout_id,
            limit=50,
            expand=["data.source"],
        )

        payout = stripe.Payout.retrieve(payout_id)
        for txn in balance_transactions.auto_paging_iter():
            if txn.reporting_category != "payout":
                item = txn.source
                if hasattr(item, "invoice"):
                    invoice = stripe.Invoice.retrieve(item.invoice)

                    result = self.sev_desk_service.is_voucher_already_added(invoice)
                    if result.is_success is False:
                        accounting_result_view_model.error_messages.append(
                            result.error_message
                        )
                        print(result.error_message)
                        continue

                    result = self.download_invoice(
                        invoice.id,
                        invoice.invoice_pdf
                    )
                    if result.is_success is False:
                        accounting_result_view_model.error_messages.append(
                            result.error_message
                        )
                        print(result.error_message)
                        continue
                    print(result.success_message)

                    result = self.sev_desk_service.upload_invoice_file(
                        invoice.id
                    )
                    if result.is_success is False:
                        accounting_result_view_model.error_messages.append(
                            result.error_message
                        )
                        print(result.error_message)
                        continue
                    print(result.success_message)

                    result = self.sev_desk_service.create_voucher(
                        invoice,
                        result.data["file_name"]
                    )
                    if result.is_success is False:
                        accounting_result_view_model.error_messages.append(
                            result.error_message
                        )
                        print(result.error_message)
                        continue
                    print(result.success_message)

                    voucher_id = result.data["voucher_id"]
                    country_code = result.data["country_code"]

                    if country_code is not None:
                        result = self.sev_desk_service.add_tag_to_voucher(
                            invoice.id,
                            voucher_id,
                            country_code
                        )

                        if result.is_success is False:
                            accounting_result_view_model.error_messages.append(
                                result.error_message
                            )
                            print(result.error_message)
                            continue
                        print(result.success_message)

                    result = self.sev_desk_service.get_account_transaction_id(
                        invoice.id,
                        payout.amount,
                        account_id
                    )
                    if result.is_success is False:
                        accounting_result_view_model.error_messages.append(
                            result.error_message
                        )
                        print(result.error_message)
                        continue

                    result = self.sev_desk_service.book_voucher(
                        voucher_id,
                        invoice, account_id,
                        result.data["account_transaction_id"]
                    )
                    if result.is_success is False:
                        accounting_result_view_model.error_messages.append(
                            result.error_message
                        )
                        print(result.error_message)
                        continue

                    accounting_result_view_model.created_voucher += 1
                    print(
                        f"{invoice.id} - Successfully added invoice to sevdesk - count: {accounting_result_view_model.created_voucher} \n"
                    )

                elif txn.reporting_category == "refund":
                    charge = stripe.Charge.retrieve(item.charge)
                    accounting_result_view_model.refunds["count"] += 1
                    accounting_result_view_model.refunds["data"].append(
                        {
                            "customer_id": charge.customer,
                            "charge_id": charge.id,
                            "receipt_url": charge.receipt_url,
                        }
                    )
                else:
                    others_data = {
                        "amount": f"{txn.amount / 100}€",
                        "net": f"{txn.net / 100}€",
                        "fee": f"{txn.fee / 100}€",
                        "description": f"{txn.description}",
                    }

                    if hasattr(
                        accounting_result_view_model.other_resource_categories,
                        txn.reporting_category
                    ):
                        accounting_result_view_model.other_resource_categories[txn.reporting_category]["count"] += 1
                        accounting_result_view_model.other_resource_categories[txn.reporting_category].append(others_data)
                    else:
                        accounting_result_view_model.other_resource_categories[txn.reporting_category] = {
                            "count": 1,
                            "data": [others_data]
                        }

        return accounting_result_view_model

    def download_invoice(self, invoice_id, invoice_pdf_url):
        """Download stripe invoice pdf in local tmp folder"""
        result_view_model = ResultViewModel()

        try:
            response = requests.get(invoice_pdf_url)
            response.raise_for_status()
            file = open(
                f"{TMP_DOWNLOADED_INVOICE_FOLDER_PATH}/{invoice_id}.pdf", "wb"
            )
            file.write(response.content)
            file.close()
            result_view_model.success_message = f"{invoice_id} - Downloaded invoice pdf"
        except requests.exceptions.HTTPError as http_error:
            result_view_model.error_message = f"{invoice_id} - Downloading invoice pdf failed (HTTP Error: {http_error})"
        except requests.exceptions.RequestException as request_error:
            result_view_model.error_message = f"{invoice_id} - Downloading invoice pdf failed (Request Error: {request_error})"

        return result_view_model
