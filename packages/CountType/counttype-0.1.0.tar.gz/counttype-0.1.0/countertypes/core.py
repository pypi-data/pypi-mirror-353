# counttypes/core.py

class CountTypes:
    def __init__(self, value):
        self.integer = 0
        self.floating = 0
        self.string = 0
        self.boolean = 0
        self.lst = 0
        self.tpl = 0
        self.dct = 0
        self.sets = 0

        self.lstOfInt = []
        self.lstOfFloat = []
        self.lstOfString = []
        self.lstOfBool = []
        self.lstOfLst = []
        self.lstOfTuple = []
        self.lstOfSet = []
        self.lstOfDict = []

        self.value = value

        for i in self.value:
            if isinstance(i, bool):
                self.boolean += 1
                self.lstOfBool.append(i)
            elif isinstance(i, int):
                self.integer += 1
                self.lstOfInt.append(i)
            elif isinstance(i, float):
                self.floating += 1
                self.lstOfFloat.append(i)
            elif isinstance(i, str):
                self.string += 1
                self.lstOfString.append(i)
            elif isinstance(i, list):
                self.lst += 1
                self.lstOfLst.append(i)
            elif isinstance(i, tuple):
                self.tpl += 1
                self.lstOfTuple.append(i)
            elif isinstance(i, set):
                self.sets += 1
                self.lstOfSet.append(i)
            elif isinstance(i, dict):
                self.dct += 1
                self.lstOfDict.append(i)

    def NonZeroTotal(self):
        NewSet = ''
        if self.integer:
            NewSet += f'Int : {self.integer}\n'
        if self.floating:
            NewSet += f'Float : {self.floating}\n'
        if self.string:
            NewSet += f'Str : {self.string}\n'
        if self.boolean:
            NewSet += f'Bool : {self.boolean}\n'
        if self.lst:
            NewSet += f'List : {self.lst}\n'
        if self.tpl:
            NewSet += f'Tuple : {self.tpl}\n'
        if self.sets:
            NewSet += f'Set : {self.sets}\n'
        if self.dct:
            NewSet += f'Dict : {self.dct}\n'
        return NewSet.strip()
