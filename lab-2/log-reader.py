# Imports
import argparse
import re
from prettytable import PrettyTable

def main():
    # Configure Argsuments & Help
    parser = argparse.ArgumentParser(description="A utility to parse and analyze Linux system logs.")
    parser.add_argument("logFileA", help="The log file to parse.")
    parser.add_argument("logFileB", help="The log file to parse.")
    parser.add_argument("logFileC", help="The log file to parse.")
    parser.add_argument("exercise", help="The exercise output to generate")
    parser.add_argument("-o", "--outfile", help="Name of an output file to generate.")
    args = parser.parse_args()

    exercise  = args.exercise.lower()

    # Validate our exercise input
    if ((exercise != 'a') & (exercise != 'b')):
        raise SystemExit("Must select either exercise A or B")
    
    # Define the outfile name, default to 'output.txt'
    outfileName = 'output.txt'
    if (args.outfile):
        outfileName = args.outfile

    # Load the files
    logFileA = loadFile(args.logFileA)
    logFileB = loadFile(args.logFileB)
    logFileC = loadFile(args.logFileC)

    if (exercise == 'a'):
        exerciseA(logFileA, logFileB, outfileName)
    else:
        exerciseB(logFileA, logFileB, outfileName)

def exerciseA(logFileA, logFileB, outFileName):
    # Find all instances of read events in both files
    readEventsA = findTermInLog(logFileA, [' read('])
    readEventsB = findTermInLog(logFileB, [' read('])

    # Find instances of read events from the keyboard - /dev/tty
    readKeyboardsA = findTerm(readEventsA, ['/dev/tty'])
    readKeyboardsB = findTerm(readEventsB, ['/dev/tty'])

    # Find instances of read events from a file
    # 0/3/5, etc. seems to indicate the source of the read, '/' will mean it's a filepath
    readFilesA = findTerm(readEventsA, ['read(3</'])
    readFilesB = findTerm(readEventsB, ['read(3</'])

    repeats = findRepeatingFileInstances(readFilesA, readFilesB)
    table = generateRepeatingFileInstancesTable(repeats)

    # Save to a text file
    with open(outFileName, "w") as f:
        f.write("Output A:\n\n")
        f.write("Number of read events:" + str(len(readEventsA)) + "\n\n")
        f.write(formatEvents(readEventsA) + "\n\n")
        f.write("Output B:\n\n")
        f.write("Number of read events:" + str(len(readEventsB)) + "\n\n")
        f.write(formatEvents(readEventsB) + "\n\n")
        f.write("Output C:\n\n")
        f.write(formatEvents(readKeyboardsA) + "\n\n")
        f.write("Output D:\n\n")
        f.write(formatEvents(readKeyboardsB) + "\n\n")
        f.write("Output E:\n\n")
        f.write(formatEvents(readFilesA) + "\n\n")
        f.write("Output F:\n\n")
        f.write(formatEvents(readFilesB) + "\n\n")
        f.write("Output G:\n\n")
        f.write(table.get_string() + "\n")

def exerciseB(logFileA, logFileB, outFileName):
    # Find all instances of read events in both files
    readEventsA = findTermInLog(logFileA, [' read('])
    readEventsB = findTermInLog(logFileB, [' read('])

    # Find instances of read events from the keyboard - /dev/tty
    readKeyboardsA = findTerm(readEventsA, ['/dev/tty'])
    readKeyboardsB = findTerm(readEventsB, ['/dev/tty'])

    # Find instances of read events from a file
    # 0/3/5, etc. seems to indicate the source of the read, '/' will mean it's a filepath
    readFilesA = findTerm(readEventsA, ['read(3</'])
    readFilesB = findTerm(readEventsB, ['read(3</'])

    # Find read from pipe events
    readPipesA = findTerm(readEventsA, ['pipe'])
    readPipesB = findTerm(readEventsB, ['pipe'])

    # Start to stub out table content
    result1 = {}

    result1["Read files from log A"] = len(readFilesA)
    result1["Read files from log B"] = len(readFilesB)
    result1["Read keyboard from log A"] = len(readKeyboardsA)
    result1["Read keyboard from log B"] = len(readKeyboardsB)
    result1["Read pipe from log A"] = len(readPipesA)
    result1["Read pipe from log B"] = len(readPipesB)

    table1 = generateTable(["Event", "Occurances"], result1)

    # Find program start events
    programStartsA = findTermInLog(logFileA, ['execve'])
    programStartsB = findTermInLog(logFileB, ['execve'])

    # Find write events
    programWritesA = findTermInLog(logFileA, ['execve'])
    programWritesB = findTermInLog(logFileB, ['execve'])

    # Find get file/directory status events
    statusChecksA = findTermInLog(logFileA, ["access", "stat"])
    statusChecksB = findTermInLog(logFileB, ["access", "stat"])

    # Find unlink events
    unlinksA = findTermInLog(logFileA, ['unlink'])
    unlinksB = findTermInLog(logFileB, ['unlink'])

    # Find program ends events
    programEndsA = findTermInLog(logFileA, ['exit_group'])
    programEndsB = findTermInLog(logFileB, ['exit_group'])

    # Build out table 2
    # Start to stub out table content
    result2 = {}

    result2["Program starts from log A"] = len(programStartsA)
    result2["Program starts from log B"] = len(programStartsB)
    result2["Program writes from log A"] = len(programWritesA)
    result2["Program writes from log B"] = len(programWritesB)
    result2["Status checks from log A"] = len(statusChecksA)
    result2["Status checks from log B"] = len(statusChecksB)
    result2["File unlinks from log A"] = len(unlinksA)
    result2["File unlinks from log B"] = len(unlinksB)
    result2["Program ends from log A"] = len(programEndsA)
    result2["Program ends from log B"] = len(programEndsB)

    table2 = generateTable(["Event", "Occurances"], result2)

    result3 = findExecutableOccurances(programStartsA, programStartsB)
    table3 = generateExecutableTable(result3)

    writeEventsA = findTermInLog(logFileA, ['write('])
    writeEventsB = findTermInLog(logFileB, ['write('])

    writeTTYA = findTerm(writeEventsA, ['tty'])
    writeTTYB = findTerm(writeEventsB, ['tty'])

    writeContentA = extractContent(writeTTYA)
    writeContentB = extractContent(writeTTYB)

    readContentA = extractContent(readKeyboardsA)
    readContentB = extractContent(readKeyboardsB)

    # Save to a text file
    with open(outFileName, "w") as f:
        f.write("Output A:\n\n")
        f.write(table1.get_string() + "\n\n")
        f.write("Output B:\n\n")
        f.write(table2.get_string() + "\n\n")
        f.write("Output C:\n\n")
        f.write(table3.get_string() + "\n\n")
        f.write("Output D:\n\n")
        f.write("Content read from the keyboard:\n\n")
        f.write(formatContents(readContentA) + "\n\n")
        f.write("Content printed to the terminal:\n\n")
        f.write(formatContents(writeContentA)+ "\n\n")
        f.write("Output E:\n\n")
        f.write("Content read from the keyboard:\n\n")
        f.write(formatContents(readContentB) + "\n\n")
        f.write("Content printed to the terminal:\n\n")
        f.write(formatContents(writeContentB) + "\n")

def extractContent(events):

    result = []

    for event, timestamp in events:
        content = re.search(r'\([^\)]+\s*,\s*"([^"]+)"\s*,', event)

        if content:
            result.append(content.group(1))

    return result

# Generates a table from the results of findExecutableOccurances()
def generateExecutableTable(executables):
    table = PrettyTable()
    table.field_names = ["Executable", "Log A Occurances", "Log B Occurances"]

    for executable, timestamps in executables.items():
        timestamps_a = ", ".join(map(str, timestamps["timestampsA"]))
        timestamps_b = ", ".join(map(str, timestamps["timestampsB"]))
        table.add_row([executable, timestamps_a, timestamps_b])

    return(table)

# Takes in a collection of [[line, timestamp], [line, timestamp]] and returns a string of all the lines
def formatEvents(events):
    return "\n".join(event[0] for event in events)

# Same as formatEvents but for the content functions
def formatContents(contents):
    return "\n".join(content for content in contents)

# Takes in a set of headers and data and builds/returns a table
def generateTable(fieldNames, data):
    table = PrettyTable()
    table.field_names = fieldNames

    for key, value in data.items():
        table.add_row([key, value])

    return table

# Parses through executable start events to build a dictionary of timestamps in each log file for each executable
def findExecutableOccurances(eventsA, eventsB):
    result = {}

    for event, timestamp in eventsA:
        executable = re.search(r'execve\("([^"]+)"', event)

        if executable:
            executable = executable.group(1)
            if executable not in result:
                result[executable] = {"timestampsA": [], "timestampsB": []}
            result[executable]["timestampsA"].append(timestamp)

    for event, timestamp in eventsB:
        executable = re.search(r'execve\("([^"]+)"', event)

        if executable:
            executable = executable.group(1)
            if executable not in result:
                result[executable] = {"timestampsA": [], "timestampsB": []}
            result[executable]["timestampsB"].append(timestamp)

    # Replace empty timestamp lists with "absent"
    for executable, timestamps in result.items():
        if not timestamps["timestampsA"]:
            timestamps["timestampsA"] = ["absent"]
        if not timestamps["timestampsB"]:
            timestamps["timestampsB"] = ["absent"]

    return result

# Take X instances of read file collections, and return the number of times each file occurs if it's greater than 1
def findRepeatingFileInstances(*readEvents):
    result = {}

    # Combine the event collections into one
    events = [event for events in readEvents for event in events]

    for event, timestamp in events:
        name = re.search(r'<([^>]+)>', event).group(1)
        
        if name not in result:
            result[name] = {"count": 0, "timestamps": []}
        
        result[name]["count"] += 1
        result[name]["timestamps"].append(timestamp)

    # Filter to only include files that appear more than once
    result = {key: value for key, value in result.items() if value["count"] >= 2}

    return result

# Generataes a table for output G
def generateRepeatingFileInstancesTable(result):
    table = PrettyTable()
    table.field_names = ["File Name", "Count", "Timestamps"]

    for file_name, data in result.items():
        count = data["count"]
        timestamps = ", ".join(map(str, data["timestamps"]))  # Convert timestamps list to a comma-separated string
        table.add_row([file_name, count, timestamps])

    return table

# Returns each line of a file containing one or more given terms in a list of lists
# [[line, timestamp], [line, timestamp]]
def findTermInLog(logFile, terms):
    result = []

    for timestamp, line in enumerate(logFile, start=1):
        if any(term in line for term in terms):
            result.append([line.strip(), timestamp])

    return result

# Returns each line of output from findTermInLog containing one or more given terms
def findTerm(events, terms):
    result = []

    for line, timestamp in events:
        if any(term in line for term in terms):
            result.append([line, timestamp])

    return result

# Loads a file and returns the lines in a collection
def loadFile(fileName):
    file = open(fileName)
    lines = file.readlines()
    file.close()
    return lines

if __name__ == '__main__':
    main()