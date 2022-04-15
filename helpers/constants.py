import os
import pathlib

SEVDESK_BASE_API_URL = "https://my.sevdesk.de/api/v1/"

TMP_DOWNLOADED_INVOICE_FOLDER_PATH = os.path.join(
    pathlib.Path().resolve(),
    "tmp_invoices"
)

ADDITIONAL_INFO_FOLDER_PATH = os.path.join(
    pathlib.Path().resolve(),
    "additional_info"
)

PRINTED_LOGS_FILE_PATH = os.path.join(
    ADDITIONAL_INFO_FOLDER_PATH,
    "printed_logs.txt"
)

PROCESSED_PAYOUTS_FILE_PATH = os.path.join(
    ADDITIONAL_INFO_FOLDER_PATH,
    "already_processed_payout_ids.txt"
)

ADDITIONAL_INFO_PAYOUT_FOLDER_NAME_PLACEHOLDER = "#payout_name#"
ADDITIONAL_INFO_PAYOUT_FOLDER_PATH = os.path.join(
    ADDITIONAL_INFO_FOLDER_PATH,
    ADDITIONAL_INFO_PAYOUT_FOLDER_NAME_PLACEHOLDER
)

CUSTOM_PAYOUT_INPUT_NAME = "custom_payout_id"
CUSTOM_ACCOUNT_INPUT_NAME = "custom_account_id"

VOUCHER_ID_PLACEHOLDER = "#voucher_id#"
CHECK_IF_VOUCHER_ALREADY_ADDED = "Voucher"
CHECK_ACCOUNT_ENDPOINT = "CheckAccount"
ADD_TAG_TO_VOUCHER_ENDPOINT = "Tag/Factory/create"
BOOK_VOUCHER_ENDPOINT = f"Voucher/{VOUCHER_ID_PLACEHOLDER}/bookAmount"
CREATE_VOUCHER_API_ENDPOINT = "Voucher/Factory/saveVoucher"
UPLOAD_VOUCHER_API_ENDPOINT = "Voucher/Factory/uploadTempFile"
CHECK_ACCOUNT_TRANSACTION_ENDPOINT = "CheckAccountTransaction"
