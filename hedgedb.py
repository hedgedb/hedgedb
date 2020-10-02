class HedgeDB:
    def __init__(self):
        self.task = TaskVersion()
        self.task.run()


class TaskVersion:
    def __init__(self):
        self.version = 1.0

    def run(self):
        print("HedgeDB V{}".format(self.version))


hedgeDB = HedgeDB()
