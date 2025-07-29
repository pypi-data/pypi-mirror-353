class Group:
    def __init__(self, name=None, noncapturing=False):
        self.name = ''
        self.data = ''
        if noncapturing:
            self.data = r'?:'
        elif name:
            self.name = name
            self.data = f'?<{name}>'
