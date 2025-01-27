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
    readEventsA = findTerm(logFileA, [' read('])
    readEventsB = findTerm(logFileB, [' read('])

    # Find instances of read events from the keyboard - /dev/tty
    readKeyboardsA = findTerm(readEventsA, ['/dev/tty'])
    readKeyboardsB = findTerm(readEventsB, ['/dev/tty'])

    # Find instances of read events from a file
    # 0/3/5, etc. seems to indicate the source of the read, '/' will mean it's a filepath
    readFilesA = findTerm(readEventsA, ['read(3</'])
    readFilesB = findTerm(readEventsB, ['read(3</'])

    repeats = findRepeatingFileInstances(readFilesA, readFilesB)

    # TODO - print repeats as a table
    # TODO - print the other outputs
    # TODO - Timestamps

    table = generateTable(["File Name", "Num Occurances"], repeats)

    # Save to a text file
    with open(outFileName, "w") as f:
        f.write("Output A:\n")
        f.write("Number of read events:" + str(len(readEventsA)) + "\n")
        f.write(str(readEventsA) + "\n")
        f.write("Output B:\n")
        f.write("Number of read events:" + str(len(readEventsB)) + "\n")
        f.write(str(readEventsB) + "\n")
        f.write("Output C:\n")
        f.write(str(readKeyboardsA) + "\n")
        f.write("Output D:\n")
        f.write(str(readKeyboardsB) + "\n")
        f.write("Output E:\n")
        f.write(str(readFilesA) + "\n")
        f.write("Output F:\n")
        f.write(str(readFilesB) + "\n")
        f.write("Output G:\n")
        f.write(table.get_string() + "\n")

def exerciseB(logFileA, logFileB, outFileName):
    # Find all instances of read events in both files
    readEventsA = findTerm(logFileA, [' read('])
    readEventsB = findTerm(logFileB, [' read('])

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
    programStartsA = findTerm(logFileA, ['execve'])
    programStartsB = findTerm(logFileB, ['execve'])

    # Find write events
    programWritesA = findTerm(logFileA, ['execve'])
    programWritesB = findTerm(logFileB, ['execve'])

    # Find get file/directory status events
    statusChecksA = findTerm(logFileA, ["access", "stat"])
    statusChecksB = findTerm(logFileB, ["access", "stat"])

    # Find unlink events
    unlinksA = findTerm(logFileA, ['unlink'])
    unlinksB = findTerm(logFileB, ['unlink'])

    # Find program ends events
    programEndsA = findTerm(logFileA, ['exit_group'])
    programEndsB = findTerm(logFileB, ['exit_group'])

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

    print(table1)
    print(table2)

# Takes X log files and returns the names of all executables
def pullExNames(*logFiles):
    print("What the sigma")

# Takes in a set of headers and data and builds/returns a table
def generateTable(fieldNames, data):
    table = PrettyTable()
    table.field_names = fieldNames

    for key, value in data.items():
        table.add_row([key, value])

    return table

# Take X instances of read file collections, and return the number of times each file occurs if it's greater than 1
def findRepeatingFileInstances(*readEvents):

    result = {}

    # Combine the event collections into one
    events = [event for events in readEvents for event in events]

    for event in events:
        name = re.search(r'<([^>]+)>', event).group(1)
        result[name] = result.get(name, 0) + 1

    result = {key: value for key, value in result.items() if value >= 2}

    return result

# Returns each line of a file containing one or more given terms
def findTerm(logFile, terms):
    result = []

    for line in logFile:
        if any(term in line for term in terms):
            result.append(line)

    # Dedup
    return list(set(result))

# Loads a file and returns the lines in a collection
def loadFile(fileName):
    file = open(fileName)
    lines = file.readlines()
    file.close()
    return lines

if __name__ == '__main__':
    main()