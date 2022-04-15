from view_models.view_model import ViewModel


class TagViewModel(ViewModel):
    """Tag view model which represents json parameter for sevDesk request"""
    def __init__(self, voucher_id, tag_name):
        super().__init__()
        self.name = tag_name
        self.object = {
            "id": voucher_id,
            "objectName": "Voucher"
        }
