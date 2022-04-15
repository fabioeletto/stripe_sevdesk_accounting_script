from view_models.view_model import ViewModel


class AccountingResultViewModel(ViewModel):
    """Accounting result view model for end overview"""
    def __init__(self, payout_id, payout_name):
        super().__init__()
        self.payout_id = payout_id
        self.payout_name = payout_name
        self.error_messages = []
        self.created_voucher = 0
        self.refunds = {
            "data": [],
            "count": 0,
        }
        self.other_resource_categories = {}
