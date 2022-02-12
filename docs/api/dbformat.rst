Database Format
===============

Tables
------

* items
* rooms -> exits
* users

Items
-----


JSON Structure::

    {
        "id":        <int>,         # Item ID (Unique)
        "name":      <str>,         # Item Name (Unique)
        "desc":      <str>,         # Item Description
        "action":    <str>,         # Item Action Text
        "owners":    <list:str>,    # List of Owner Usernames
        "glued":     <bool>,        # Whether the Item is Glued
        "duplified": <bool>,        # Whether the Item is Duplified
        "telekey":   <None|int>     # Telekey Destination Room if Set
    }

Rooms
-----

JSON Structure::

    {
        "id":           <int>,         # Room ID (Unique)
        "name":         <str>,         # Room Name (Unique)
        "desc":         <str>,         # Room Description
        "owners":       <list:str>,    # List of Owner Usernames
        "users":        <list:str>,    # List of Occupant Usernames
        "exits":        <list:dict>,   # List of Exit Documents
        "entrances":    <list:int>,    # List of IDs of Rooms Containing Entrances
        "items":        <list:int,     # List of Present Item IDs
        "sealed": {
            "inbound":  <bool>,        # Whether the Room is Inbound Sealed
            "outbound": <bool>         # Whether the Room is Outbound Sealed
        }
    }

Users
-----

JSON Structure::

    {
        "name":         <str>,      # User Name (Unique)
        "nick":         <str>,      # User Nickname (Unique)
        "desc":         <str>,      # User Description
        "passhash":     <str>,      # SHA256 Hash of Password
        "room":         <int>,      # Current Room
        "inventory":    <list:int>, # List of Inventory Item IDs
        "pronouns":     <str>,      # Pronouns; One of: "female", "male", "neutral", or subjective case of custom.
        "pronouno":     <str>,      # Objective case of a custom pronoun.
        "pronounp":     <str>,      # Posessive case of a custom pronoun.
        "wizard":       <str>,      # Whether the User is a Wizard/Admin
        "autolook": {
            "enabled":  <bool>      # Whether Autolook is Enabled
        },
        "chat": {
            "enabled":  <bool>,     # Whether General Chat is Enabled
            "ignored":  <list:str>  # List of Ignored User Names
        }
    }

Exits
-----

An exit's ID is its index in the room's exits list. The ID will change if an exit at a lower index is broken, and is not unique between rooms.

JSON Structure::

    {
        "dest":         <int>,      # ID of Destination Room (Unique but Mutable)
        "name":         <str>,      # Exit Name (Unique)
        "desc":         <str>,      # Exit Description
        "owners":       <list:str>, # List of Owner Usernames
        "key":          <None|int>, # Key Item ID if Set
        "key_hidden":   <bool>,     # Whether the Key is Hidden
        "locked":       <bool>,     # Whether the Exit is Locked
        "action": {
            "go":       <str>,      # Action Text for Using the Exit
            "locked":   <str>,      # Action Text for Failing to Use the Exit while Locked
        },
    }
