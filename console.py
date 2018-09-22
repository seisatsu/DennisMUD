import hashlib
import importlib.util
import os
from datatype import Room, User, Item

COMMAND_DIR = "commands/"

class Console:
    def __init__(self, database):
        self.user = None
        self._database = database
        self._commands = {}
        
        # Enumerate and load available command modules.
        command_modules = os.listdir(COMMAND_DIR)
        for command in command_modules:
            if command.endswith(".py"):
                # Python files in this directory are command modules. Construct modules.
                command_path = os.path.join(os.getcwd(), COMMAND_DIR, command)
                spec = importlib.util.spec_from_file_location(command[:-3], command_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                self._commands[command[:-3]] = mod
        
        print(self._commands)
    
    def command(self, line):
        line = line.split(' ')
        print(line)
        for splitpos in range(len(line)):
            if splitpos == 0:
                if '_'.join(line) in self._commands.keys():
                    return self._commands['_'.join(line)].COMMAND(self._database)
                continue
            if '_'.join(line[:-splitpos]) in self._commands.keys():
                print(line[-splitpos:])
                return self._commands['_'.join(line[:-splitpos])].COMMAND(self._database, line[-splitpos:])
        return None
    
    def register(self, username, password):
        # Register a new user.
        check = self._database.filter(
            User, {
                "name": username
            }
        )
        if len(check) != 0: # User already exists.
            return False
        
        # Create new user.
        newuser = User({
            "name": username,
            "nick": username,
            "desc": "",
            "passhash": hashlib.sha256(password.encode()).hexdigest(),
            "online": False,
            "room": 0,
            "inventory": [],
            "wizard": False
        })
        
        # Save.
        self._database.insert(newuser)
        return True
    
    def login(self, username, password):
        thisuser = self._database.filter(
            User, {
                "name": username,
                "passhash": hashlib.sha256(password.encode()).hexdigest()
            }
        )
        if len(thisuser) == 0:
            return False # Bad login.
        self.user = thisuser[0]
        self.user.online = True
        self._database.update(self.user)
        return True
    
    def logout(self):
        self.user.online = False
        self.user = None
        self._database.update(self.user)
        return True
   
    def make_room(self, name):
        # Make sure we are logged in.
        if not self.user:
            return False
        
        # Check if a room by this name already exists. Case insensitive.
        rooms = self._database.filter(Room, {})
        if len(rooms):
            for r in rooms:
                if r["name"].lower() == name.lower():
                    return False # A room by this name already exists.
        
        # Find the highest numbered currently existing room ID.
        if len(rooms):
            lastroom = rooms.sort("id")[-1]["id"]
        else:
            lastroom = -1
        
        # Create our new room with an ID one higher.
        newroom = Room({
            "owner": self.user.name,
            "id": lastroom + 1,
            "name": name,
            "users": [],
            "exits": [],
            "items": []
        })
        
        # Save.
        self._database.insert(newroom)
        return True
    
    def make_item(self, name):
        # Make sure we are logged in.
        if not self.user:
            return False
        
        # Check if an item by this name already exists. Case insensitive.
        items = self._database.filter(Item, {})
        if len(items):
            for i in items:
                if i["name"].lower() == name.lower():
                    return False # An item by this name already exists.
        
        # Find the highest numbered currently existing item ID.
        if len(items):
            lastitem = items.sort("id")[-1]["id"]
        else:
            lastitem = -1
        
        # Create our new item with an ID one higher.
        newitem = Item({
            "id": lastitem + 1,
            "name": name,
            "desc": ""
        })
        
        # Add the item to the creator's inventory.
        self.user.inventory.append(newitem.id)
        self._database.update(self.user)
        
        # Save.
        self._database.insert(newitem)
        return True

    def make_exit(self, dest, name):
        # Make sure we are logged in.
        if not self.user:
            return False
        
        # Check if an exit by this name already exists. Case insensitive.
        thisroom = self._database.filter(Room, {"id": self.user.room})
        exits = thisroom[0]["exits"]
        if len(exits):
            for e in exits:
                if e["name"].lower() == name.lower():
                    return False # An exit by this name already exists.
        
        # Check if the destination room exists.
        destroom = self._database.filter(Room, {"id": dest})
        if not len(destroom):
            return False # The destination room does not exist.
        
        # Create our new exit.
        newexit = {"dest": dest, "name": name, "desc": ""}
        thisroom[0].exits.append(newexit)
        
        # Save.
        self._database.update(thisroom)
        return True
        
    def break_room(self, roomid):
        # Make sure we are logged in.
        if not self.user:
            return False
        
        # Check if the room exists.
        r = self._database.filter(Room, {"id": roomid})
        if len(r):
            # Delete the room.
            self._delete(r)
            return True
        else:
            # No room with that ID exists.
            return False
    
    def break_item(self, itemid):
        """Deletes an item from our inventory."""
        
        # Make sure we are logged in.
        if not self.user:
            return False
        
        # Check if the item exists.
        i = self._database.filter(Item, {"id": itemid})
        if len(i):
            # Make sure we are holding the item.
            if itemid in self._user.inventory:
                # Delete the item and remove it from our inventory.
                self._delete(i)
                self.user.inventory.remove(itemid)
                self._database.update(self.user)
                return True
            
        else:
            # No item with that ID exists, or we are not holding it.
            return False
            
    def greater_break_item(self, itemid):
        """Deletes an item even if we are not holding it or don't own it."""
        
        # Make sure we are logged in, and a wizard.
        if not self.user or not self.user.wizard:
            return False
        
        # Check if the item exists.
        i = self._database.filter(Item, {"id": itemid})
        if len(i):
            # Delete the item.
            self._delete(i)
            
            # If the item is in a room's item list, remove it.
            rooms = self._database.filter(Room, {})
            if len(rooms):
                for r in rooms:
                    if itemid in r["items"]:
                        r["items"].remove(itemid)
                        self._database.update(r)
            
            # If the item is in someone's inventory, remove it.
            users = self._database.filter(User, {})
            if len(users):
                for u in users:
                    if itemid in u["inventory"]:
                        u["inventory"].remove(itemid)
                        self._database.update(u)
            
            return True
            
        else:
            # No item with that ID exists.
            return False

    def make_exit(self, dest, name):
        # Make sure we are logged in.
        if not self.user:
            return False
        
        # Check if an exit by this name already exists. Case insensitive.
        thisroom = self._database.filter(Room, {"id": self.user.room})
        exits = thisroom[0]["exits"]
        if len(exits):
            for e in exits:
                if e["name"].lower() == name.lower():
                    return False # An exit by this name already exists.
        
        # Check if the destination room exists.
        destroom = self._database.filter(Room, {"id": dest})
        if not len(destroom):
            return False # The destination room does not exist.
        
        # Create our new exit.
        newexit = {"dest": dest, "name": name, "desc": ""}
        thisroom[0].exits.append(newexit)
        
        # Save.
        self._database.update(thisroom)
        return True
        
