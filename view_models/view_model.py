import json


class ViewModel:
    """Base view model class"""
    def to_json(self):
        """Retuns class as json object"""
        return json.dumps(self.__dict__)

    def __str__(self):
        """Retuns class name and properties as string"""
        return f"{self.__class__}: {self.__dict__}"
