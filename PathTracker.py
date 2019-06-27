import json, sys, os
from pathlib import Path

def startUp():
    print("\nStarting PathTracker...")
    global gameName
    gameName = input("Choose a campaign to load or create: ").lower()
    ensureFilesExist()

    loadData()
    print("PathTracker started successfully!\n")

    inputLoop()

    saveData()
    print("Exited successfully!")

def inputLoop():
    endLoop = False

    while not endLoop:
        command = input("PathTracker> ")
        processResult = processCommand(command)
        endLoop = (processResult == "end")

def processCommand(cmd):
    cmdInfo = parseCommandInfo(cmd)
    if cmdInfo != {}:
        command = cmdInfo["command"]

        if command == "quit" or command == "exit" or command == "q":
            return "end"
        elif command == "save":
            saveData()
        elif command == "addLoot":
            addLoot(cmdInfo["args"], cmdInfo["flags"])
        elif command == "addXP":
            addXP(cmdInfo["args"], cmdInfo["flags"])
        elif command == "addMoney":
            addMoney(cmdInfo["args"], cmdInfo["flags"])
        elif command == "listLoot":
            listLoot(cmdInfo["args"], cmdInfo["flags"])
        elif command == "listXP":
            listXP(cmdInfo["args"], cmdInfo["flags"])
        elif command == "cashOut":
            cashOut(cmdInfo["args"], cmdInfo["flags"])
        elif command == "awardXP":
            awardXP(cmdInfo["args"], cmdInfo["flags"])
        elif command == "setLootValue":
            setLootValue(cmdInfo["args"], cmdInfo["flags"])
        else:
            print("Unknown command: " + command)
        print()

def parseCommandInfo(cmd):
    if len(cmd.strip()) == 0:
        return {}
    
    quoteCount = cmd.count('"')
    if quoteCount % 2 == 1:
        print("Mismatched quotation marks. Cannot process input.")
        return {}
    
    quoteSplit = cmd.split('"')
    if len(quoteSplit[0]) == 0:
        print("Command cannot begin with a quoted value.")
        return {}
    
    parts = []
    quoted = False
    for chunk in quoteSplit:
        if quoted:
            parts.append(chunk)
        else:
            chunk = chunk.strip()
            if len(chunk) > 0:
                parts += chunk.split(' ')
        quoted = (not quoted)
    
    cmdObj = {"command": parts[0]}
    args = []
    idx = 1
    while idx < len(parts) and parts[idx][0] != '-':
        args.append(parts[idx])
        idx += 1
    cmdObj["args"] = args

    flags = []
    while idx < len(parts):
        flagObj = {"flag": parts[idx][1::]}
        flagArgs = []
        idx += 1
        while idx < len(parts) and parts[idx][0] != '-':
            flagArgs.append(parts[idx])
            idx += 1
        flagObj["args"] = flagArgs
        flags.append(flagObj)
    cmdObj["flags"] = flags
    return cmdObj

def ensureFilesExist():
    lootPath = "data/" + gameName + "/loot.json"
    xpPath = "data/" + gameName + "/xp.json"
    if os.path.isdir("data/" + gameName):
        if not os.path.exists(lootPath):
            print("Generating new loot file...")
            with open(lootPath, 'w') as lootFile:
                json.dump({'items': [], 'money': 0}, lootFile)
        if not os.path.exists(xpPath):
            print("Generating new XP file...")
            with open(xpPath, 'w') as xpFile:
                json.dump([], xpFile)
    else:
        print("Generating new data files...")
        os.makedirs("data/" + gameName, exist_ok=True)
        with open(lootPath, 'w') as lootFile:
            json.dump({'items': [], 'money': 0}, lootFile)
        with open(xpPath, 'w') as xpFile:
            json.dump([], xpFile)

def loadData():
    global lootData
    global xpData
    global lootTotal
    global xpTotal
    print("Loading loot data...")
    with open("data/" + gameName + "/loot.json") as lootFile:
        lootData = json.loads(lootFile.read())
    lootTotal = lootData["money"]
    for item in lootData["items"]:
        if "value" in item:
            lootTotal += item["value"] / 2
    print("Loot loaded. Total sell value is currently " + str(lootTotal) + " gp.")
    
    print("Loading XP data...")
    with open("data/" + gameName + "/xp.json") as xpFile:
        xpData = json.loads(xpFile.read())
    xpTotal = 0
    for reward in xpData:
        xpTotal += reward['value']
    print("XP loaded. Total XP is currently " + str(xpTotal) + ".")

def saveData():
    print("Saving data...")
    with open("data/" + gameName + "/loot.json", "w") as lootFile:
        json.dump(lootData, lootFile)
    with open("data/" + gameName + "/xp.json", "w") as xpFile:
        json.dump(xpData, xpFile)
    print("All data saved.")

def addLoot(args, flags):
    completeAdd = True
    if len(args) != 1:
        print("Unexpected number of arguments. Please specify exactly one item and any relevant flags.")
        completeAdd = False
    item = {"name": args[0]}
    quantity = 1
    value = 0
    for flagItem in flags:
        flag = flagItem["flag"]
        flagArgs = flagItem["args"]
        if flag == "v":
            if len(flagArgs) != 1:
                print("The -v flag expects exactly one argument for item value.")
                completeAdd = False
            elif not flagArgs[0].replace('.','',1).isdigit():
                print("The -v flag expects a positive number.")
                completeAdd = False
            else:
                value = float(flagArgs[0])
                item["value"] = value
        elif flag == "q":
            if len(flagArgs) != 1:
                print("The -q flag expects exactly one argument for item quantity.")
                completeAdd = False
            elif not flagArgs[0].isdigit():
                print("The -q flag expects a positive integer.")
                completeAdd = False
            else:
                quantity = int(flagArgs[0])
        else:
            print("Unknown flag: -" + flag + ".")
            completeAdd = False
    
    if completeAdd:
        global lootTotal
        lootTotal += (value / 2) * float(quantity)
        for _ in range(quantity):
            lootData["items"].append(item.copy())
        print("Added " + str(quantity) + "x " + item["name"] + " to loot. Total sell value is now " + str(lootTotal) + ".")
    else:
        print("Could not add item due to one or more errors. Please try again.")

def addXP(args, flags):
    completeAdd = True
    value = 0
    if len(args) != 1:
        print("Unexpected number of arguments. Please specify exactly one XP value and any relevant flags.")
        completeAdd = False
    elif not args[0].isdigit():
        print("XP value must be a positive integer")
        completeAdd = False
    else:
        value = int(args[0])
    item = {"value": value}
    quantity = 1
    for flagItem in flags:
        flag = flagItem["flag"]
        flagArgs = flagItem["args"]
        if flag == "d":
            if len(flagArgs) != 1:
                print("The -d flag expects exactly one argument for XP source description.")
                completeAdd = False
            else:
                item["description"] = flagArgs[0]
        elif flag == "q":
            if len(flagArgs) != 1:
                print("The -q flag expects exactly one argument for item quantity.")
                completeAdd = False
            elif not flagArgs[0].isdigit():
                print("The -q flag expects a positive integer.")
                completeAdd = False
            else:
                quantity = int(flagArgs[0])
        else:
            print("Unknown flag: -" + flag + ".")
            completeAdd = False
    
    if completeAdd:
        global xpTotal
        xpTotal += value * quantity
        for _ in range(quantity):
            xpData.append(item.copy())
        print("Added " + str(value * quantity) + " XP. Total XP is now " + str(xpTotal) + ".")
    else:
        print("Could not add XP due to one or more errors. Please try again.")

def addMoney(args, flags):
    completeAdd = True
    value = 0
    if len(args) != 1:
        print("Unexpected number of arguments. Please specify exactly one monetary value and any relevant flags.")
        completeAdd = False
    elif not args[0].replace('.','',1).isdigit():
        print("Monetary value must be a positive number.")
        completeAdd = False
    else:
        value = float(args[0])
    for flagItem in flags:
        flag = flagItem["flag"]
        flagArgs = flagItem["args"]
        if flag == "q":
            if len(flagArgs) != 1:
                print("The -q flag expects exactly one argument for item quantity.")
                completeAdd = False
            elif not flagArgs[0].isdigit():
                print("The -q flag expects a positive integer.")
                completeAdd = False
            else:
                value *= float(flagArgs[0])
        else:
            print("Unknown flag: -" + flag + ".")
            completeAdd = False

    if completeAdd:
        global lootTotal
        lootTotal += value
        lootData["money"] += value
        print("Added " + str(value) + " gp to loot. Total sell value is now " + str(lootTotal) + ".")
    else:
        print("Could not add money due to one or more errors. Please try again.")

def sortLootByValue(item):
        if "value" in item:
            return item["value"]
        else:
            return 0

def listLoot(args, flags):
    if len(args) > 0:
        print("listLoot takes no arguments, only optional flags.")
    for item in sorted(lootData["items"], key=sortLootByValue, reverse=True):
        if "value" in item:
            print(item["name"] + ": " + str(item["value"]) + " gp")
        else:
            print(item["name"])
    print()
    print("Money: " + str(lootData["money"]) + " gp")
    print("Total value: " + str(lootTotal) + " gp")

def listXP(args, flags):
    if len(args) > 0:
        print("listXP takes no arguments, only optional flags.")
    for item in xpData:
        if "description" in item:
            print(str(item["value"]) + " XP (" + item["description"] + ")")
        else:
            print(str(item["value"]) + " XP (no description included)")
    print()
    print("Total: " + str(xpTotal) + " XP")

def cashOut(args, flags):
    complete = True
    if len(args) > 0:
        print("cashOut takes no arguments, only optional flags.")
        complete = False
    numPCs = 1
    for flagItem in flags:
        flag = flagItem["flag"]
        flagArgs = flagItem["args"]
        if flag == "n":
            if len(flagArgs) != 1:
                print("The -n flag expects exactly one argument for number of PCs.")
                complete = False
            elif not flagArgs[0].isdigit():
                print("The -n flag expects a positive integer.")
                complete = False
            else:
                numPCs = int(flagArgs[0])
        else:
            print("Unknown flag: -" + flag + ".")
            complete = False
    
    if complete:
        global lootTotal
        sellList = [item for item in lootData["items"] if "value" in item]
        for item in sorted(sellList, key=sortLootByValue, reverse=True):
            print(item["name"] + ": " + str(item["value"]) + " gp")
        print()
        print("Money: " + str(lootData["money"]) + " gp")
        print("Total value: " + str(lootTotal) + " gp")
        print()

        print("Each PC receives " + str(lootTotal / numPCs) + " gp.")

        lootData["money"] = 0
        lootTotal = 0
        lootData["items"] = [item for item in lootData["items"] if not "value" in item]
        if len(lootData["items"]) > 0:
            print("Some items had no value and could not be sold.")
    else:
        print("Could not cash out due to one or more errors. Please try again.")

def awardXP(args, flags):
    complete = True
    if len(args) > 0:
        print("awardXP takes no arguments, only optional flags.")
        complete = False
    numPCs = 1
    for flagItem in flags:
        flag = flagItem["flag"]
        flagArgs = flagItem["args"]
        if flag == "n":
            if len(flagArgs) != 1:
                print("The -n flag expects exactly one argument for number of PCs.")
                complete = False
            elif not flagArgs[0].isdigit():
                print("The -n flag expects a positive integer.")
                complete = False
            else:
                numPCs = int(flagArgs[0])
        else:
            print("Unknown flag: -" + flag + ".")
            complete = False
    
    if complete:
        global xpTotal
        global xpData
        for item in xpData:
            if "description" in item:
                print(str(item["value"]) + " XP (" + item["description"] + ")")
            else:
                print(str(item["value"]) + " XP (no description included)")
        print()
        print("Total: " + str(xpTotal) + " XP")
        print()
        print("Each PC receives " + str(xpTotal / numPCs) + " gp.")

        xpTotal = 0
        xpData = []
    else:
        print("Could not award XP due to one or more errors. Please try again.")

def setLootValue(args, flags):
    complete = True
    if len(args) != 2:
        print("setLootValue takes exactly two arguments: item name and value.")
        complete = False
    name = args[0]
    if not args[1].replace('.','',1).isdigit():
        print("The second argument must be a positive numeric value.")
    value = float(args[1])
    if len(flags) > 0:
        print("setLootValue doesn't take any flags.")
        complete = False
    if complete:
        count = 0
        global lootTotal
        for item in lootData["items"]:
            if item["name"] == name:
                if "value" in item:
                    lootTotal -= item["value"] / 2
                item["value"] = value
                lootTotal += (value / 2)
                count += 1
        print("Successfully set value for " + str(count) + " item(s). Total sell value updated to " + str(lootTotal) + " gp.")
    else:
        print("Could not set value(s) due to one or more errors. Please try again.")
startUp()
