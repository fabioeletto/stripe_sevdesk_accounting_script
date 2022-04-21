from datetime import datetime
from PyInquirer import prompt

from services.sevdesk_service import SevDeskService

from helpers.file_helper import FileHelper
from helpers.constants import (
    PROCESSED_PAYOUTS_FILE_PATH
)


class Prompt:
    """Prompt for selecting stripe payout and sevDesk account"""
    def __init__(self, stripe_service):
        sevdesk_service = SevDeskService()

        # Get sevdesk data
        print("Getting required sevDesk accounts info...")
        result = sevdesk_service.get_accounts_info()
        if result.is_success:
            self.accounts = result.data["accounts"]
        else:
            print(result.error_message)
            return

        # Get stripe data
        print("Getting required stripe payouts info...")
        self.payouts = stripe_service.get_formatted_payouts()

        self.init_prompt()

    def init_prompt(self):
        """Init prompt"""
        questions = self.get_questions()
        self.answers = prompt(questions)

        self.account_selection_answer = self.accounts[
            self.answers.get("account_selection")
        ]

        self.payout_selection_answer = self.payouts[
            self.answers.get("payout_selection")
        ]

    def get_questions(self):
        """Get prompt questions"""
        return [
            {
                "type": "list",
                "name": "payout_selection",
                "message": "Choose a stripe payout",
                "choices": self.payouts.keys()
            },
            {
                "type": "list",
                "name": "account_selection",
                "message": "Choose a sevDesk payment account",
                "choices": self.accounts.keys(),
            },
        ]

    def get_answer_payout_id(self):
        """Get stripe payout answer id"""
        return self.payout_selection_answer

    def get_answer_account_id(self):
        """Get sevDesk account answer id"""
        return self.account_selection_answer

    def create_end_overview(self, accounting_result_view_model):
        """Create end overview of accounting process"""
        error_messages = accounting_result_view_model.error_messages
        date_format = "%d.%m.%Y %H:%M:%S Uhr"
        current_date_timestamp = datetime.now().strftime(date_format)
        print(f"{current_date_timestamp} - Finished!")
        print("---------------------------STATUS----------------------------")
        print(
            f"booked invoices => successful: {accounting_result_view_model.created_voucher} || failed: {len(error_messages)}"
        )
        print(f'not automatically booked refunds: {accounting_result_view_model.refunds["count"]}')

        category_names = accounting_result_view_model.other_resource_categories.keys()
        for category_name in category_names:
            print(f'{category_name}: {accounting_result_view_model.other_resource_categories[category_name]["count"]}')
        print("--------------------------------------------------------------")

        FileHelper.create_refunds_log(
            accounting_result_view_model.refunds["data"],
            accounting_result_view_model.payout_name
        )
        FileHelper.create_other_resource_categories_log(
            accounting_result_view_model.other_resource_categories,
            accounting_result_view_model.payout_name
        )

        if len(error_messages) > 0:
            FileHelper.create_error_log(
                error_messages,
                accounting_result_view_model.payout_name
            )
        else:
            FileHelper.write_to_file(
                PROCESSED_PAYOUTS_FILE_PATH,
                f"{accounting_result_view_model.payout_id} \n"
            )

        print(f"You can find more information about the accounting process in additional_info/{accounting_result_view_model.payout_name} folder")
