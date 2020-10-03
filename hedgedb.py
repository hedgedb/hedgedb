import sys


class HedgeDB:

    version = 1.0

    def __init__(self):

        self.names = []
        self.commands = dict()

        for command_subclass in Command.__subclasses__():
            command_class = command_subclass()
            self.names.append(command_class.name)
            self.commands[command_class.name] = command_class

        if len(sys.argv) == 2:
            command_name = sys.argv[1]
        else:
            command_name = "help"

        if command_name == "help":
            self.commands["version"].run(self.commands)

        self.commands[command_name].run(self.commands)


class Command:
    def __init__(self):
        self.name = "name"
        self.description = "description"

    def run(self, commands):
        pass


class CommandHelp(Command):
    def __init__(self):
        super().__init__()
        self.name = "help"
        self.description = "Display help message"

    def run(self, commands):
        print("Usage:")
        print("  {} command\n".format(sys.argv[0]))
        print("Commands:")
        for name, command in commands.items():
            print("  {:<16} {}".format(name, command.description))


class CommandVersion(Command):
    def __init__(self):
        super().__init__()
        self.name = "version"
        self.description = "Display HedgeDB version"

    def run(self, commands):
        print("HedgeDB Version {}\n".format(HedgeDB.version))


hedge_db = HedgeDB()
