from datetime import datetime
from helpers.file_helper import FileHelper

from services.stripe_service import StripeService

from helpers.logger import Logger
from helpers.prompt import Prompt
from helpers.constants import (
    PRINTED_LOGS_FILE_PATH,
    ADDITIONAL_INFO_FOLDER_PATH,
    TMP_DOWNLOADED_INVOICE_FOLDER_PATH
)

if __name__ == "__main__":
    stripe_service = StripeService()

    FileHelper.create_directory(ADDITIONAL_INFO_FOLDER_PATH)

    Logger(PRINTED_LOGS_FILE_PATH)

    prompt = Prompt(stripe_service)

    account_id = prompt.get_answer_account_id()
    payout_id = prompt.get_answer_payout_id()

    print(f"SevDesk account id: {account_id}")
    print(f"Stripe payout id: {payout_id}")

    current_date_timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S Uhr")
    print(f"{current_date_timestamp} - Start processing ...")

    accounting_result_view_model = stripe_service.start_accounting(
        payout_id,
        account_id
    )

    prompt.create_end_overview(accounting_result_view_model)

    FileHelper.remove_recursiv_directory(TMP_DOWNLOADED_INVOICE_FOLDER_PATH)
