class APIResponse:

    def __init__(self, data):

        self.raw = data

    @property
    def success(self):

        if "status" in self.raw:
            return self.raw["status"] == "1"

        if "errorcode" in self.raw:
            return self.raw["errorcode"] == "200"

        return False

    @property
    def data(self):

        return self.raw.get("data")
