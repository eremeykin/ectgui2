class Markers:
    def __init__(self):
        self._dict = {"X": (None, None), "Y": (None, None), "C": (None, None)}

    def set(self, marker, table, feature):
        self._dict[marker] = (table, feature)

    def get_marker(self, table, feature):
        markers = []
        for marker in self._dict.keys():
            c_table, c_feature = self._dict[marker]
            if c_table is table and feature == c_feature:
                markers.append(marker)
        return markers

    def all(self):
        return self._dict.keys()
