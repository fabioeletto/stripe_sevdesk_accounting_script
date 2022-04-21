import stripe
from datetime import datetime

from view_models.tag_view_model import TagViewModel
from view_models.result_view_model import ResultViewModel
from view_models.voucher_view_model import VoucherViewModel
from view_models.book_voucher_view_model import BookVoucherViewModel
from view_models.voucher_position_view_model import VoucherPositionViewModel

from helpers.sevdesk_api_caller import SevDeskApiCaller
from helpers.constants import (
    BOOK_VOUCHER_ENDPOINT,
    CHECK_ACCOUNT_ENDPOINT,
    VOUCHER_ID_PLACEHOLDER,
    ADD_TAG_TO_VOUCHER_ENDPOINT,
    UPLOAD_VOUCHER_API_ENDPOINT,
    CREATE_VOUCHER_API_ENDPOINT,
    CHECK_IF_VOUCHER_ALREADY_ADDED,
    CHECK_ACCOUNT_TRANSACTION_ENDPOINT,
    TMP_DOWNLOADED_INVOICE_FOLDER_PATH
)
from helpers.accounting_types import AccountingTypes


class SevDeskService(SevDeskApiCaller):
    """SevDesk service"""
    def __init__(self):
        super().__init__()

    def get_accounts_info(self):
        """Get all sevDesk account infos"""
        result_view_model = ResultViewModel()
        accounts = {}

        raw_request = self.get(CHECK_ACCOUNT_ENDPOINT)
        if raw_request.ok:
            result = raw_request.json()
            for account in result.get("objects"):
                accounts[account.get("name")] = account.get("id")
        else:
            result_view_model.error_message = "Getting sevDesk account info failed. Please try again or enter a custom account id"
            return result_view_model

        accounts["Custom_id"] = "custom"
        result_view_model.data["accounts"] = accounts
        return result_view_model

    def is_voucher_already_added(
        self,
        invoice_id,
        voucher_number
    ):
        result_view_model = ResultViewModel()
        data = {
            'descriptionLike': voucher_number,
        }

        raw_request = self.get(
            CHECK_IF_VOUCHER_ALREADY_ADDED,
            data
        )
        if raw_request.ok:
            result = raw_request.json()
            if len(result.get("objects")) > 0:
                result_view_model.error_message = f"{invoice_id} - Error: Voucher already exists ({voucher_number})"
        else:
            result_view_model.error_message = f"{invoice_id} - The voucher retrieval API responded with an error, duplicates cannot be detected"

        return result_view_model

    def upload_invoice_file(self, invoice_id):
        """Upload invoice pdf to sevDesk"""
        result_view_model = ResultViewModel()

        files = {
            "file": open(
                f"{TMP_DOWNLOADED_INVOICE_FOLDER_PATH}/{invoice_id}.pdf",
                "rb",
            )
        }

        raw_result = self.post(UPLOAD_VOUCHER_API_ENDPOINT, {}, files)
        if raw_result.ok:
            result = raw_result.json()
            result_view_model.success_message = f"{invoice_id} - Uploaded invoice file to sevdesk"
            result_view_model.data["file_name"] = result.get("objects").get("filename")
        else:
            result_view_model.error_message = f"{invoice_id} - Uploading invoice file to sevdesk failed"

        return result_view_model

    def create_voucher(self, accounting_view_model, file_name):
        """Create a new voucher in sevDesk"""
        result_view_model = ResultViewModel()

        voucher = VoucherViewModel(
            accounting_view_model.voucher_date,
            accounting_view_model.supplier_name,
            accounting_view_model.voucher_type,
            accounting_view_model.delivery_date,
            accounting_view_model.delivery_date_until,
            accounting_view_model.voucher_number,
            file_name
        )

        for line in accounting_view_model.voucher_position_lines_data:
            description = (
                line.description.encode("utf-8").decode("utf-8")
                if accounting_view_model.voucher_type == "D"
                else f"Credit note for {accounting_view_model.voucher_number}"
            )

            voucher.add_voucher_position(VoucherPositionViewModel(
                AccountingTypes.REVENUE.value,
                accounting_view_model.voucher_tax_rate.get("percentage"),
                line.amount,
                description)
            )

        result_view_model.data["country_code"] = accounting_view_model.voucher_tax_rate.get("country")

        if accounting_view_model.voucher_type == "D":
            discount = accounting_view_model.invoice.get("discount")
            if discount is not None:
                voucher.add_voucher_position(VoucherPositionViewModel(
                    AccountingTypes.REVENUE_REDUCTION.value,
                    accounting_view_model.voucher_tax_rate.get("percentage"),
                    -discount.coupon.amount_off,
                    discount.coupon.name)
                )

        raw_result = self.post(CREATE_VOUCHER_API_ENDPOINT, voucher.to_json())
        if raw_result.ok:
            result = raw_result.json()
            result_view_model.success_message = f"{accounting_view_model.voucher_id} - Created voucher"
            result_view_model.data["voucher_id"] = result.get("objects").get("voucher").get("id")
        else:
            result_view_model.error_message = f"{accounting_view_model.voucher_id} - Creating voucher failed"

        return result_view_model

    def add_tag_to_voucher(self, invoice_id, voucher_id, tag_name):
        result_view_model = ResultViewModel()

        tag_view_model = TagViewModel(voucher_id, tag_name)

        raw_result = self.post(
            ADD_TAG_TO_VOUCHER_ENDPOINT,
            tag_view_model.to_json()
        )
        if raw_result.ok:
            result_view_model.success_message = f"{invoice_id} - Added tag to voucher"
        else:
            result_view_model.error_message = f"{invoice_id} - Adding tag failed"

        return result_view_model

    def get_account_transaction_id(
        self,
        invoice_id,
        stripe_payout_amount,
        account_id
    ):
        """Get sevDesk account transaction id where the vouchers should be linked to"""
        result_view_model = ResultViewModel()

        data = {
            'checkAccount[id]': account_id,
            'checkAccount[objectName]': 'CheckAccount',
        }

        raw_request = self.get(
            CHECK_ACCOUNT_TRANSACTION_ENDPOINT,
            data
        )
        if raw_request.ok:
            result = raw_request.json()
            for check_account_transaction in result.get("objects"):
                if float(check_account_transaction.get("amount")) == float(
                    (stripe_payout_amount / 100)
                ):
                    result_view_model.data["account_transaction_id"] = check_account_transaction.get("id")
        else:
            result_view_model.error_message = f"{invoice_id} - Check account transaction failed"

        return result_view_model

    def book_voucher(
        self,
        account_view_model,
        voucher_id,
        account_id,
        sevdesk_transaction_id
    ):
        """Book a voucher in sevDesk"""
        result_view_model = ResultViewModel()

        endpoint = BOOK_VOUCHER_ENDPOINT.replace(
            VOUCHER_ID_PLACEHOLDER,
            voucher_id
        )

        book_voucher_view_model = BookVoucherViewModel(
            account_view_model.voucher_total_amount,
            account_view_model.voucher_paid_at,
            account_id,
            sevdesk_transaction_id
        )

        raw_result = self.put(endpoint, book_voucher_view_model.to_json())
        if not raw_result.ok:
            result_view_model.error_message = f"{account_view_model.voucher_id} - Booking voucher failed"

        return result_view_model
