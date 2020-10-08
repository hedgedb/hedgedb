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

        if command_name in self.commands:
            self.commands[command_name].run(self.commands)
        else:
            print("ERROR: Unknown command '{}'".format(command_name))


class Column:
    def __init__(self, name):
        self.name = name


class Connector:
    def __init__(self, user, password, host, port, database):
        self.parameters = {
            'user': user,
            'password': password,
            'host': host,
            'port': port,
            'database': database
        }
        self.connection = None
        self.error = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.parameters)
        except mysql.connector.Error as err:
            self.error = err
        else:
            self.connection.close()


class Table:
    def __init__(self, name):
        self.name = name
        self.columns = []


class Command:
    def __init__(self):
        self.name = "name"
        self.description = "description"

    def help(self):
        print("")

    def run(self, commands):
        pass


class CommandAnalyze(Command):
    def __init__(self):
        super().__init__()
        self.name = "analyze"
        self.description = "Analyze database schema"

    def help(self):
        print("analyze user:password@host:port/database")

    def run(self, command):
        print("Analyze")


class CommandConnect(Command):
    def __init__(self):
        super().__init__()
        self.name = "connect"
        self.description = "Testing database connection"

    def help(self):
        print("connect user:password@host:port/database")

    def run(self, commands):
        dsn = sys.argv[2]
        user = dsn[0:dsn.find(":")]
        password = dsn[dsn.find(":")+1:dsn.find("@")]
        host = dsn[dsn.find("@")+1:dsn.find(":", dsn.find(":") + 1)]
        port = dsn[dsn.find(":", dsn.find(":") + 1) + 1:dsn.find("/")]
        database = dsn[dsn.find("/")+1:]
        connector = Connector(user, password, host, port, database)
        connector.connect()
        if connector.error is None:
            print("PASS")
        else:
            print("FAIL {} {}".format(connector.error.errno, connector.error.msg))


class CommandHelp(Command):
    def __init__(self):
        super().__init__()
        self.name = "help"
        self.description = "Display help message"

    def help(self):
        print("help          - print main help with list of supported commands")
        print("help commands - display detailed help for specified command")

    def run(self, commands):
        print("Usage:")
        print("  {} command\n".format(sys.argv[0]))
        print("Commands:")
        for name, command in commands.items():
            print("  {:<10} {}".format(name, command.description))


class CommandVersion(Command):
    def __init__(self):
        super().__init__()
        self.name = "version"
        self.description = "Display HedgeDB version"

    def help(self):
        print("version - just display version and exit")

    def run(self, commands):
        print("HedgeDB Version {}\n".format(HedgeDB.version))


hedge_db = HedgeDB()
