import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Optional

import requests
import platform

class VehicleHistoryClientError(Exception):
    pass

@dataclass
class VehicleInfo:
    registration_number: str
    vin: str
    first_registration_date: str

class VehicleHistoryClient:
    def __init__(self):
        self.session = requests.Session()

        self.base_url = "https://moj.gov.pl"
        self.app_name = "HistoriaPojazdu"
        self.api_version = "1.0.17"

        self.nf_wid: Optional[str] = None
        self.cookies: Optional[dict[str, str]] = None

        self._setup_session_headers()

    def _setup_session_headers(self):
        self.session.headers.update({
            "Accept-Language": "pl-PL,pl;q=0.9",
            "User-Agent": f"cepik-vehicle-history-client/0.1.0; Python/{platform.python_version()}",
            })

    @staticmethod
    def _get_current_time_ms():
        """Get the current time in milliseconds."""
        return int(round(time.time() * 1000))

    def __make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise VehicleHistoryClientError(f"Request failed: {e}")

    def create_session(self):
        url = f"{self.base_url}/uslugi/engine/ng/index?xFormsAppName={self.app_name}"

        res = self.__make_request("GET", url)
        if res.status_code != 200:
            raise VehicleHistoryClientError("Failed to create session")

        self.cookies = res.cookies.get_dict()

        if not self.cookies:
            raise VehicleHistoryClientError("No cookies have been received from the server while creating a session.")

        return self.cookies

    def authenticate_session(self):
        if not self.cookies:
            raise VehicleHistoryClientError("A session must be created before authentication.")

        current_time = self._get_current_time_ms()
        self.nf_wid = f"{self.app_name}:{current_time}"

        url = f"{self.base_url}/uslugi/engine/ng/index?xFormsAppName={self.app_name}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = f"NF_WID={self.nf_wid}"

        res = self.__make_request("POST", url, headers=headers, cookies=self.cookies, data=data)

        if res.status_code != 200:
            raise VehicleHistoryClientError("Failed to authenticate session")

        new_cookies = res.cookies.get_dict()
        self.cookies.update(new_cookies)

        return self.cookies, self.nf_wid

    def close_session(self) -> None:
        if not self.cookies or not self.nf_wid:
            raise VehicleHistoryClientError("Session was not properly initialized.")

        url = f"{self.base_url}/nforms/api/{self.app_name}/{self.api_version}/close"

        headers = {
            "Content-Type": "application/json, text/plain, */*",
            "Nf_wid": self.nf_wid,
            }

        self.__make_request("GET", url, headers=headers, cookies=self.cookies)
        self.cookies = None
        self.nf_wid = None
        self.session.close()

    def __make_api_request(self, endpoint: str, vehicle_info: VehicleInfo):
        if not self.cookies or not self.nf_wid:
            raise VehicleHistoryClientError("Session was not properly authenticated.")

        if "XSRF-TOKEN" not in self.cookies:
            raise VehicleHistoryClientError("Missing XSRF-TOKEN. Ensure session is authenticated.")

        url = f"{self.base_url}/nforms/api/{self.app_name}/{self.api_version}/data/{endpoint}"

        headers = {
            "Content=Type": "application/json",
            "X-Xsrf-Token": self.cookies["XSRF-TOKEN"],
            "Nf_wid": self.nf_wid,
        }

        data = {
            "registrationNumber": vehicle_info.registration_number,
            "VINNumber": vehicle_info.vin,
            "firstRegistrationDate": vehicle_info.first_registration_date,
        }

        res = self.__make_request("POST", url, headers=headers, cookies=self.cookies, json=data)

        return res.json()

    def get_vehicle_data(self, vehicle_info: VehicleInfo):
        response = self.__make_api_request("vehicle-data", vehicle_info)

        if "technicalData" not in response:
            raise VehicleHistoryClientError("Invalid response format: 'technicalData' not found.")

        return response

    def get_timeline_data(self, vehicle_info: VehicleInfo):
        response = self.__make_api_request("timeline-data", vehicle_info)

        if "timelineData" not in response:
            raise VehicleHistoryClientError("Invalid response format: 'timelineData' not found.")

        return response

    @contextmanager
    def authenticated_session(self):
        try:
            self.create_session()
            self.authenticate_session()
            yield self
        finally:
            if self.cookies and self.nf_wid:
                try:
                    self.close_session()
                except Exception as e:
                    print(f"Warning: Failed to close session: {e}")