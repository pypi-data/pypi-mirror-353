class Set:
    def __init__(self):
        self.data = ''

    def add_char(self, char):
        self.data += char
        return self

    def add_range(self, start, end):
        self.data += f'{start}-{end}'
        return self

class ReverseSet(Set):
    def __init__(self):
        self.data = '^'
