from view_models.view_model import ViewModel


class VoucherPositionViewModel(ViewModel):
    """Voucher position view model which represents json parameter for sevDesk request"""
    def __init__(
        self,
        accounting_type_id,
        tax_percentage,
        amount,
        description
    ):
        super().__init__()
        self.accountingType = {
            "id": accounting_type_id,
            "objectName": "AccountingType"
        }
        self.taxRate = tax_percentage
        self.sum = None
        self.net = False
        self.isAsset = False
        self.sumNet = None
        self.sumGross = amount / 100
        self.comment = description
        self.mapAll = True
        self.objectName = "VoucherPos"
