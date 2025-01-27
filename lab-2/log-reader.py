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
    readEventsA = findTerm(' read(', logFileA)
    readEventsB = findTerm(' read(', logFileB)

    # Find instances of read events from the keyboard - /dev/tty
    readKeyboardsA = findTerm('/dev/tty', readEventsA)
    readKeyboardsB = findTerm('/dev/tty', readEventsB)

    # Find instances of read events from a file
    # 0/3/5, etc. seems to indicate the source of the read, '/' will mean it's a filepath
    readFilesA = findTerm('read(3</', readEventsA)
    readFilesB = findTerm('read(3</', readEventsB)

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
    readEventsA = findTerm(' read(', logFileA)
    readEventsB = findTerm(' read(', logFileB)

    # Find instances of read events from the keyboard - /dev/tty
    readKeyboardsA = findTerm('/dev/tty', readEventsA)
    readKeyboardsB = findTerm('/dev/tty', readEventsB)

    # Find instances of read events from a file
    # 0/3/5, etc. seems to indicate the source of the read, '/' will mean it's a filepath
    readFilesA = findTerm('read(3</', readEventsA)
    readFilesB = findTerm('read(3</', readEventsB)

    # Find read from pipe events
    readPipesA = findTerm('pipe', readEventsA)
    readPipesB = findTerm('pipe', readEventsB)

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
    programStartsA = findTerm('execve', logFileA)
    programStartsB = findTerm('execve', logFileB)

    # Find write events
    programWritesA = findTerm('write', logFileA)
    programWritesB = findTerm('write', logFileB)

    # Find get file/directory status events
    statusChecksA = findTerms(logFileA, "access", "stat")
    statusChecksB = findTerms(logFileB, "access", "stat")

    # Find unlink events
    unlinksA = findTerm('unlink', logFileA)
    unlinksB = findTerm('unlink', logFileB)

    # Find program ends events
    programEndsA = findTerm('exit_group', logFileA)
    programEndsB = findTerm('exit_group', logFileB)

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

# Returns each line of a file containing a given term
def findTerm(term, logFile):

    result = []

    for line in logFile:
        if term in line:
            result.append(line)

    return result

# Returns each line of a file containing a given terms
def findTerms(logFile, *terms):

    result = []

    for line in logFile:
        for term in terms:
            if term in line:
                result.append(line)

    # Dedup
    return set(result)

# Loads a file and returns the lines in a collection
def loadFile(fileName):
    file = open(fileName)
    lines = file.readlines()
    file.close()
    return lines

if __name__ == '__main__':
    main()