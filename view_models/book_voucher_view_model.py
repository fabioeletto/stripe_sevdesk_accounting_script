from view_models.view_model import ViewModel


class BookVoucherViewModel(ViewModel):
    """Book voucher view model which represents json parameter for sevDesk request"""
    def __init__(self, invoice, account_id, sevdesk_transaction_id):
        super().__init__()
        self.amount = invoice.total / 100
        self.date = invoice.status_transitions.paid_at
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
