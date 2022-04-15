import os
from urllib.parse import urlencode
import requests

from dotenv import load_dotenv
from requests.structures import CaseInsensitiveDict

from helpers.constants import SEVDESK_BASE_API_URL


class SevDeskApiCaller:
    """SevDesk api caller"""
    def __init__(self):
        load_dotenv("../.env")
        self.api_key = os.getenv("SEVDESK_API_KEY")
        self.base_api_url = SEVDESK_BASE_API_URL

    def set_headers(self):
        """Set required http header for api calls"""
        headers = CaseInsensitiveDict()
        headers["Authorization"] = self.api_key
        headers["Content-Type"] = "application/json"

        return headers

    def get(self, api_endpoint, params=None):
        """GET for sevDesk api"""
        if params is None:
            params = {}
        headers = self.set_headers()

        encoded_params = urlencode(params)

        url = f"{self.base_api_url}{api_endpoint}?{encoded_params}"

        return requests.get(url, headers=headers)

    def post(self, api_endpoint, data, files=None):
        """POST for sevDesk api"""
        headers = self.set_headers()
        url = f"{self.base_api_url}{api_endpoint}"

        if files is not None:
            file_header = CaseInsensitiveDict()
            file_header["Authorization"] = self.api_key
            return requests.post(url, files=files, headers=file_header)

        return requests.post(url, data=data, headers=headers)

    def put(self, api_endpoint, data):
        """PUT for sevDesk api"""
        headers = self.set_headers()
        url = f"{self.base_api_url}{api_endpoint}"

        return requests.put(url, data=data, headers=headers)
