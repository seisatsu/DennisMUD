import blitzdb
from datatype import Room, User, Item

class DatabaseManager:
    def __init__(self, database):
        self.database = blitzdb.FileBackend(database)
        
        if len(self.database.filter(Room,{})) == 0:
            self._init_room()
        
        if len(self.database.filter(User,{})) == 0:
            self._init_user()
    
    def insert(self, document):
        # Insert a new document.
        self.database.save(document)
        self.database.commit()
    
    def update(self, document):
        # Update an existing document.
        document.save()
        self.database.commit()
    
    def delete(self, document):
        # Delete an existing document.
        self.database.delete(document)
        self.database.commit()
    
    def filter(self, doctype, query):
        return self.database.filter(doctype, query)

    def _init_room(self):
        newroom = Room({
            "owner": "[world]",
            "id": 0,
            "name": "Initial Room",
            "users": ["[world]"],
            "exits": [],
            "items": [],
        })
        self.insert(newroom)
        return True
    
    def _init_user(self):
        newuser = User({
            "name": "[world]",
            "nick": "Root User",
            "desc": "The administrator.",
            "passhash": "0",
            "online": False,
            "room": 0,
            "inventory": [],
            "wizard": True
        })
        self.insert(newuser)
        return True

