class Markers:
    markers = ["X", "Y", "C"]

    def __init__(self):
        self.markers = [(None, x) for x in Markers.markers]
