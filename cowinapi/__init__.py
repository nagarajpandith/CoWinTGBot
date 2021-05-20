from datetime import datetime
import urllib.parse
from enum import Enum
from typing import List, Optional

import httpx


class ErrorCode(Enum):
    InvalidPincodeError = "APPOIN0018"
    TooManyRequests = "403: Too many requests"


class CoWinAPIException(Exception):
    error_code: str
    error: str

    def __init__(self, errorCode: str, error: str):  ## noqa
        self.error_code = errorCode
        self.error = error

    def __str__(self) -> str:
        return f"{self.error_code}: {self.error}"

    def __repr__(self) -> str:
        return self.__str__()


class CoWinTooManyRequests(CoWinAPIException):
    pass


class Session:
    date: str
    capacity: int
    min_age_limit: int
    vaccine: str
    slots: List[str]

    def __init__(
        self,
        date: str,
        available_capacity: int,
        min_age_limit: int,
        vaccine: str,
        slots: List[str],
        **kwargs,
    ):
        self.date = date
        self.capacity = available_capacity
        self.min_age_limit = min_age_limit
        self.vaccine = vaccine
        self.slots = slots

    def __str__(self) -> str:
        return f"{self.date} ({self.capacity}): {', '.join(self.slots)}"

    def __repr__(self) -> str:
        return self.__str__()

    def is_available(self) -> bool:
        return self.capacity > 0

    @staticmethod
    def from_json(data) -> "Session":
        return Session(**data)


class VaccinationCenter:
    name: str
    block_name: str
    fee_type: str
    sessions: List[Session]

    def __init__(self, name: str, block_name: str, fee_type: str, **kwargs):
        self.name = name
        self.block_name = block_name
        self.fee_type = fee_type
        self.sessions: List[Session] = []

    def __str__(self) -> str:
        return f"{self.name.title()} ({self.block_name.title()})"

    def __repr__(self) -> str:
        return self.__str__()

    def has_available_sessions(self) -> bool:
        return len(self.get_available_sessions()) > 0

    def get_available_sessions(self) -> List[Session]:
        return [s for s in self.sessions if s.is_available()]

    def get_available_sessions_by_age_limit(self, age_limit: int) -> List[Session]:
        return [s for s in self.sessions if s.min_age_limit == age_limit]

    @staticmethod
    def from_json(data) -> "VaccinationCenter":
        vc = VaccinationCenter(**data)
        if sessions := data.get("sessions"):
            vc.sessions = [Session.from_json(s) for s in sessions]
        return vc


class CoWinAPI:
    def __init__(self):
        # some sane defaults
        self.accept_language = "en_US"
        self.base_domain = "https://cdn-api.co-vin.in/"

    """
    pincode: valid pincode in str
    date: valid date in str with DD-MM-YYYY format
    """

    def calender_by_pin(
        self: "CoWinAPI", pincode: str, date: str
    ) -> Optional[List[VaccinationCenter]]:
        url = urllib.parse.urljoin(
            self.base_domain, "/api/v2/appointment/sessions/public/calendarByPin"
        )
        params = {"pincode": pincode, "date": date}
        r = httpx.get(url, params=params, headers=self.get_default_headers())
        if r.status_code == httpx.codes.BAD_REQUEST:
            raise CoWinAPIException(**r.json())
        if r.status_code == httpx.codes.FORBIDDEN:
            raise CoWinTooManyRequests(
                errorCode=ErrorCode.TooManyRequests.value,
                error=ErrorCode.TooManyRequests.value,
            )
        if not r.status_code == httpx.codes.OK:
            return
        if centers := r.json()["centers"]:
            return [VaccinationCenter.from_json(c) for c in centers]
        return

    def get_default_headers(self) -> dict:
        return {
            "Accept": "application/json, text/plain",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip",
            "Origin": "https://www.cowin.gov.in",
            "Referer": "https://www.cowin.gov.in/",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/92.0.4476.0 Safari/537.36",
        }

    @staticmethod
    def today() -> str:
        return datetime.today().strftime("%d-%m-%Y")
