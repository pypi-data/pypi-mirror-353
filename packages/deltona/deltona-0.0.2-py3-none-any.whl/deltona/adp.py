"""Salary calculator."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING, TypedDict, cast, override

import requests

from .string import strip_ansi_if_no_colors

if TYPE_CHECKING:
    from .typing import INCITS38Code

__all__ = ('SalaryResponse', 'calculate_salary')

# Find the API key by looking at requests on this page
# http://www.symmetry.com/try-it-for-free/calculators
API_KEY = 'RnFqNFA0NVlRTExEenRwWjNiRnJrTXY4WkZHZEpkcENEeFFzQ3F0Nnh5VT0='
POST_URI = ('https://calculators.symmetry.com/api/calculators/'
            'hourly?report=none')
REFERER = 'https://www.symmetry.com/'


class ContentDict(TypedDict):
    federal: float
    fica: float
    medicare: float
    netPay: float
    state: float


class ResponseDict(TypedDict):
    content: ContentDict


@dataclass
class SalaryResponse:
    """Response from the Symmetry API."""
    federal: float
    """Federal tax amount."""
    fica: float
    """FICA tax amount."""
    fuckery: float
    """Difference between gross and net pay."""
    gross: float
    """Gross pay amount."""
    medicare: float
    """Medicare tax amount."""
    net_pay: float
    """Net pay amount."""
    state: float
    """State tax amount."""
    @override
    def __str__(self) -> str:
        return strip_ansi_if_no_colors(f"""Gross     \033[1;32m{self.gross:8.2f}\033[0m
Federal   \033[1;32m{self.federal:8.2f}\033[0m
FICA      \033[1;32m{self.fica:8.2f}\033[0m
Medicare  \033[1;32m{self.medicare:8.2f}\033[0m
State     \033[1;32m{self.state:8.2f}\033[0m
------------------
Net       \033[1;32m{self.net_pay:8.2f}\033[0m

------------------
Fuckery   \033[1;31m{self.fuckery:8.2f}\033[0m""")


def calculate_salary(*,
                     hours: int = 70,
                     pay_rate: float = 70.0,
                     state: INCITS38Code = 'FL') -> SalaryResponse:
    """
    Calculate a US salary using the Symmetry API.

    Parameters
    ----------
    hours : int
        The number of hours worked. Default is 70.
    pay_rate : float
        The pay rate per hour. Default is 70.0.
    state : INCITS38Code
        The state code. Default is 'FL'.

    Returns
    -------
    SalaryResponse
        The response from the Symmetry API.
    """
    check_date = int(datetime.now(tz=UTC).timestamp() * 1000)
    gross_pay = hours * pay_rate
    req = requests.post(POST_URI,
                        headers={
                            'accept': 'application/json, text/javascript, */*; q=0.01',
                            'cache-control': 'no-cache',
                            'dnt': '1',
                            'origin': 'https://www.symmetry.com',
                            'pcc-api-key': API_KEY,
                            'referer': REFERER
                        },
                        json={
                            'checkDate': check_date,
                            'state': state.upper(),
                            'rates': [{
                                'payRate': str(pay_rate),
                                'hours': str(hours),
                            }],
                            'grossPay': str(gross_pay),
                            'grossPayType': 'PAY_PER_PERIOD',
                            'grossPayYTD': '0',
                            'payFrequency': 'MONTHLY',
                            'exemptFederal': 'false',
                            'exemptFica': 'false',
                            'exemptMedicare': 'false',
                            'federalFilingStatusType': 'SINGLE',
                            'federalAllowances': '0',
                            'additionalFederalWithholding': '0',
                            'roundFederalWithholding': 'false',
                            'print': {
                                'checkDate': check_date,
                                'checkNumber': '',
                                'checkNumberOnCheck': 'false',
                                'companyAddressLine1': '',
                                'companyAddressLine2': '',
                                'companyAddressLine3': '',
                                'companyName': '',
                                'companyNameOnCheck': 'false',
                                'employeeAddressLine1': '',
                                'employeeAddressLine2': '',
                                'employeeAddressLine3': '',
                                'employeeName': '',
                                'id': '',
                                'remarks': ''
                            },
                            'otherIncome': [],
                            'payCodes': [],
                            'stockOptions': [],
                            'stateInfo': {
                                'parms': [{
                                    'name': 'TOTALALLOWANCES',
                                    'value': '0'
                                }, {
                                    'name': 'additionalStateWithholding',
                                    'value': '0'
                                }, {
                                    'name': 'SPOUSEBLINDNESS',
                                    'value': 'false'
                                }, {
                                    'name': 'stateExemption',
                                    'value': 'false'
                                }, {
                                    'name': 'PERSONALBLINDNESS',
                                    'value': 'false'
                                }, {
                                    'name': 'HEADOFHOUSEHOLD',
                                    'value': 'false'
                                }, {
                                    'name': 'FULLTIMESTUDENT',
                                    'value': 'false'
                                }]
                            },
                            'voluntaryDeductions': [],
                            'presetDeductions': []
                        },
                        timeout=30)
    req.raise_for_status()
    data = cast('ResponseDict', req.json())['content']
    return SalaryResponse(federal=data['federal'],
                          fica=data['fica'],
                          fuckery=gross_pay - data['netPay'],
                          gross=gross_pay,
                          medicare=data['medicare'],
                          net_pay=data['netPay'],
                          state=data['state'])
