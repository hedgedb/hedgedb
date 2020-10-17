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


class Arguments:
    def __init__(self):
        pass

    @staticmethod
    def parse(argument):
        dsn = argument
        return {
            'user': dsn[0:dsn.find(":")],
            'password': dsn[dsn.find(":") + 1:dsn.find("@")],
            'host': dsn[dsn.find("@") + 1:dsn.find(":", dsn.find(":") + 1)],
            'port': dsn[dsn.find(":", dsn.find(":") + 1) + 1:dsn.find("/")],
            'database': dsn[dsn.find("/") + 1:]
        }


class Column:
    def __init__(self, name):
        self.name = name


class Connector:
    def __init__(self, parameters):
        self.parameters = parameters
        self.connection = None
        self.error = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.parameters)
        except mysql.connector.Error as err:
            self.error = err

    def disconnect(self):
        self.connection.close()


class Table:
    def __init__(self, name, engine):
        self.name = name
        self.engine = engine
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
        parameters = Arguments.parse(sys.argv[2])
        connector = Connector(parameters)
        connector.connect()
        cursor = connector.connection.cursor()
        tables_stmt = Q.select(["TABLE_NAME", "ENGINE"], "information_schema.TABLES", "TABLE_SCHEMA = %s")
        columns_stmt = Q.select(
            [
                "ORDINAL_POSITION",
                "COLUMN_NAME",
                "IS_NULLABLE",
                "DATA_TYPE",
                "CHARACTER_MAXIMUM_LENGTH",
                "CHARACTER_OCTET_LENGTH",
                "NUMERIC_PRECISION",
                "NUMERIC_SCALE",
                "DATETIME_PRECISION",
                "CHARACTER_SET_NAME",
                "COLLATION_NAME",
                "COLUMN_TYPE",
                "COLUMN_KEY",
                "EXTRA",
                "PRIVILEGES",
                "COLUMN_COMMENT",
                "GENERATION_EXPRESSION",
                "SRS_ID"
            ], "information_schema.COLUMNS", "TABLE_SCHEMA = %s AND TABLE_NAME = %s", "ORDINAL_POSITION"
        )
        database = parameters['database']
        print("Database: {}".format(database))
        cursor.execute(tables_stmt, [database])

        tables = []
        for (TABLE_NAME, ENGINE) in cursor:
            table = Table(TABLE_NAME, ENGINE)
            tables.append(table)
            print("{} {}".format(table.name, table.engine))
        cursor.close()
        connector.disconnect()


class CommandConnect(Command):
    def __init__(self):
        super().__init__()
        self.name = "connect"
        self.description = "Testing database connection"

    def help(self):
        print("connect user:password@host:port/database")

    def run(self, commands):
        parameters = Arguments.parse(sys.argv[2])
        connector = Connector(parameters)
        connector.connect()
        if connector.error is None:
            print("PASS")
            connector.disconnect()
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


class Inspection:
    def __init__(self):
        self.engines = "SELECT ENGINE, COUNT(1) FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s GROUP BY ENGINE"
        self.charsets = "SELECT CHARACTER_SET_NAME, COUNT(1) FROM information_schema.TABLES " \
                        "WHERE TABLE_SCHEMA = %s GROUP BY CHARACTER_SET_NAME"
        self.collations = "SELECT TABLE_COLLATION, COUNT(1) FROM information_schema.TABLES " \
                          "WHERE TABLE_SCHEMA = %s GROUP BY TABLE_COLLATION"
        self.size = "SELECT TABLE_SCHEMA," \
                    "ROUND(SUM(DATA_LENGTH) / 1024 / 1024)," \
                    "ROUND(SUM(INDEX_LENGTH) / 1024 / 1024)," \
                    "ROUND(SUM(DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024) " \
                    "FROM information_schema.TABLES " \
                    "GROUP BY TABLE_SCHEMA " \
                    "WITH ROLLUP"


class Q:
    @staticmethod
    def select(expression, reference, condition, position=None):
        if position is None:
            stmt = "SELECT {} FROM {} WHERE {}".format(','.join(expression), reference, condition)
        else:
            stmt = "SELECT {} FROM {} WHERE {} ORDER BY {}".format(','.join(expression), reference, condition, position)
        return stmt


hedge_db = HedgeDB()
