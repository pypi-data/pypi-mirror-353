from typing import List
from ...interface import IData
from ...packer.trade.read_ins_date_range_data_packer import ReadInsDateRangeDataPacker


class ReadInsDateRangeData(IData):
    def __init__(self, instrument_id: str = '', period: str = ''):
        super().__init__(ReadInsDateRangeDataPacker(self))
        self._InstrumentID: str = instrument_id
        self._Period: str = period
        self._StartDate: str = ''
        self._EndDate: str = ''

    @property
    def InstrumentID(self):
        return self._InstrumentID

    @InstrumentID.setter
    def InstrumentID(self, value: str):
        self._InstrumentID = value

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, value: str):
        self._Period = value

    @property
    def StartDate(self):
        return self._StartDate

    @StartDate.setter
    def StartDate(self, value: str):
        self._StartDate = value

    @property
    def EndDate(self):
        return self._EndDate

    @EndDate.setter
    def EndDate(self, value: str):
        self._EndDate = value
