from view_models.view_model import ViewModel


class ResultViewModel(ViewModel):
    """Result view model for api requests"""
    def __init__(self):
        self.data = {}
        self._is_success = False
        self.error_message = None
        self.success_message = None

    @property
    def is_success(self):
        """Property if api request was successful"""
        if self.error_message is None:
            return True
        else:
            return False
