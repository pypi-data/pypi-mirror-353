from ...interface import IPacker


class ReadInsDateRangeDataPacker(IPacker):
    def __init__(self, obj) -> None:
        super().__init__(obj)

    def obj_to_tuple(self):
        return [str(self._obj.InstrumentID),
                str(self._obj.Period),
                str(self._obj.StartDate),
                str(self._obj.EndDate)]

    def tuple_to_obj(self, t):
        if len(t) >= 4:
            self._obj.InstrumentID = t[0]
            self._obj.Period = t[1]
            self._obj.StartDate = t[2]
            self._obj.EndDate = t[3]

            return True
        return False
