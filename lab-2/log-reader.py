# Imports
import argparse
import re
from tabulate import tabulate

def main():
    # Configure Argsuments & Help
    parser = argparse.ArgumentParser(description="A utility to parse and analyze Linux system logs.")
    parser.add_argument("logFileA", help="The log file to parse.")
    parser.add_argument("logFileB", help="The log file to parse.")
    parser.add_argument("-o", "--outfile", help="Name of an output file to generate.")
    args = parser.parse_args()

    # Load the file
    logFileA = loadFile(args.logFileA)
    logFileB = loadFile(args.logFileB)

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
            
# Loads a file and returns the lines in a collection
def loadFile(fileName):
    file = open(fileName)
    lines = file.readlines()
    file.close()
    return lines

if __name__ == '__main__':
    main()