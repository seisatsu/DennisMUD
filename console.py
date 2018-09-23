import importlib.util
import os

COMMAND_DIR = "commands/"


class Console:
    def __init__(self, database, msgcallback):
        self.user = None
        self.msgcallback = msgcallback
        self._database = database
        self._commands = {}
        
        self._load_modules()
    
    def _load_modules(self):
        """
        Enumerate and load available command modules.
        Command modules are stored in COMMAND_DIR, and their filename defines their command name.
        """
        command_modules = os.listdir(COMMAND_DIR)
        for command in command_modules:
            if command.endswith(".py"):
                # Python files in this directory are command modules. Construct modules.
                command_path = os.path.join(os.getcwd(), COMMAND_DIR, command)
                spec = importlib.util.spec_from_file_location(command[:-3], command_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self._commands[command[:-3]] = mod
        print("Registered commands: "+str(list(self._commands.keys())))
    
    def command(self, line):
        """
        Parse and execute a command line, discerning which arguments are part of the command name
        and which arguments should be passed to the command.
        """
        # Split the command line into a list of arguments.
        print("$ "+line)
        line = line.split(' ')
        
        # Find out which part of the line is the command, and which part are its arguments.
        for splitpos in range(len(line)):
            if splitpos == 0:
                if '_'.join(line) in self._commands.keys():
                    # Run the command with no arguments.
                    return self._commands['_'.join(line)].COMMAND(self, self._database, [])
                continue
            if '_'.join(line[:-splitpos]) in self._commands.keys():
                # Run the command and pass arguments.
                return self._commands['_'.join(line[:-splitpos])].COMMAND(self, self._database, line[-splitpos:])
        return None

    def help(self, line):
        """
        Retrieve the help for a command.
        """
        if line.replace(' ', '_') in self._commands.keys():
            usage = "Usage: "+self._commands[line.replace(' ', '_')].USAGE
            desc = "Description: "+self._commands[line.replace(' ', '_')].DESCRIPTION
            self.msg(usage)
            print(usage)
            self.msg(desc)
            print(desc)
        return None

    def msg(self, message):
        print(message)
        self.msgcallback(message)
        return True
