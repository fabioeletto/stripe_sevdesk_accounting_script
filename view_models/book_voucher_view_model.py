from view_models.view_model import ViewModel


class BookVoucherViewModel(ViewModel):
    """Book voucher view model which represents json parameter for sevDesk request"""
    def __init__(
        self,
        voucher_total_amount,
        voucher_paid_at,
        account_id,
        sevdesk_transaction_id
    ):
        super().__init__()
        self.amount = voucher_total_amount / 100
        self.date = voucher_paid_at
        self.type = "N"
        self.checkAccount = {
            "id": account_id,
            "objectName": "CheckAccount",
        }
        self.checkAccountTransaction = {
            "id": sevdesk_transaction_id,
            "objectName": "CheckAccountTransaction"
        }
        self.createFeed = True
