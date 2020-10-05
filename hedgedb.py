import sys
import mysql.connector


class HedgeDB:

    version = 1.0

    def __init__(self):

        self.names = []
        self.commands = dict()

        for command_subclass in Command.__subclasses__():
            command_class = command_subclass()
            self.names.append(command_class.name)
            self.commands[command_class.name] = command_class

        if len(sys.argv) >= 2:
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


class CommandConnect(Command):
    def __init__(self):
        super().__init__()
        self.name = "connect"
        self.description = "Testing database connection"

    def run(self, commands):
        dsn = sys.argv[2]
        user = dsn[0:dsn.find(":")]
        password = dsn[dsn.find(":")+1:dsn.find("@")]
        if dsn.find("/") == -1:
            host = dsn[dsn.find("@")+1:]
        else:
            host = dsn[dsn.find("@")+1:dsn.find("/")]
        print(host)
        try:
            conn = mysql.connector.connect(user=user, password=password, host=host)
            print("PASS")
        except mysql.connector.Error as err:
            print("FAIL {} {}".format(err.errno, err.msg))
        else:
            conn.close()


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
