# Imports
import argparse
import re


def main():
    # Configure Argsuments & Help
    parser = argparse.ArgumentParser(
        description="A utility to parse and analyze Linux system logs."
    )
    parser.add_argument("logFileA", help="The log file to parse.")
    parser.add_argument("logFileB", help="The log file to parse.")
    parser.add_argument("logFileC", help="The log file to parse.")
    parser.add_argument("exercise", help="The exercise output to generate")
    parser.add_argument("-o", "--outfile", help="Name of an output file to generate.")
    args = parser.parse_args()

    exercise = args.exercise.lower()

    # Validate our exercise input
    if (exercise != "a") & (exercise != "b"):
        raise SystemExit("Must select either exercise A or B")

    # Define the outfile name, default to 'output.txt'
    outfileName = "output.txt"
    if args.outfile:
        outfileName = args.outfile

    # Load the files
    logFileA = loadFile(args.logFileA)
    logFileB = loadFile(args.logFileB)
    logFileC = loadFile(args.logFileC)

    if exercise == "a":
        exerciseA(logFileA, logFileB, logFileC)
    else:
        exerciseB(logFileB)


def exerciseB(logFileB):
    # So we know this is gonna be working with log B because it's the only one that has an fchmodat event
    # And it's on "remote_shell.elf" lmao

    # First we need "open-write-close sequences"
    print("Open-Write-Close sequences from Log A:\n")
    printTripleSequences(["open(", "write(", "close("], logFileB)

    # fchmodat instaces
    fchmodat_events = findTermInLog(logFileB, ["fchmodat("])

    for event in fchmodat_events:
        print(f"Fchmodat Event: '{event}'\n")

    # execve instaces
    execve_events = findTermInLog(logFileB, ["execve("])

    for event in execve_events:
        print(f"Execve Event: '{event}'\n")


def exerciseA(logFileA, logFileB, logFileC):
    # Outputs A & B
    print("Stat-Clone sequences from Log A:\n")
    printStatNumSequences(logFileA)
    print("Stat-Clone sequences from Log B:\n")
    printStatNumSequences(logFileB)
    print("Stat-Clone sequences from Log C:\n")
    printStatNumSequences(logFileC)

    # Output C
    print("Open-Getdents-Close sequences from Log A:\n")
    printTripleSequences(["open(", "getdents(", "close("], logFileA)
    print("Open-Getdents-Close sequences from Log B:\n")
    printTripleSequences(["open(", "getdents(", "close("], logFileB)
    print("Open-Getdents-Close sequences from Log C:\n")
    printTripleSequences(["open(", "getdents(", "close("], logFileA)


# Takes in a list of events ["clone", "stat", "write"] etc
# Prints corresponding sequences of events
def printTripleSequences(sequence: list, logFile):
    # last seen info for stat
    pids = [None, None, None]
    timestamps = [None, None, None]
    events = [None, None, None]
    keywords = [False, False, False]

    for timestamp, line in enumerate(logFile, start=1):
        pid = line.split(" ")[0]

        if sequence[0] in line:
            pids[0] = pid
            timestamps[0] = timestamp
            events[0] = line
            keywords[0] = True
        elif sequence[1] in line:
            if keywords[0]:
                if pids[0] == pid:
                    pids[1] = pid
                    timestamps[1] = timestamp
                    events[1] = line
                    keywords[1] = True
        elif sequence[2] in line:
            if keywords[0] and keywords[1]:
                if (pids[0] == pid) and (pids[1] == pid):
                    pids[2] = pid
                    timestamps[2] = timestamp
                    events[2] = line
                    keywords[2] = True

        # Check for a valid subsequence, if valid clear out the vars
        if keywords[0] and keywords[1] and keywords[2]:
            print(
                f"Valid Sequence:\nFirst Event: '{events[0].strip()}'\nTimestamp: {timestamps[0]}\nSecond Event: '{events[1].strip()}'\nTimestamp: {timestamps[1]}\nThird Event: '{events[2].strip()}'\nTimestamp: {timestamps[2]}\n"
            )

            # Clear
            pids = [None, None, None]
            timestamps = [None, None, None]
            events = [None, None, None]
            keywords = [False, False, False]


def printStatNumSequences(logFile):
    result = []

    # last seen info for stat
    stat_pid = None
    stat_timestamp = None
    stat_event = None

    # last seen info for clone
    clone_pid = None
    clone_timestamp = None
    clone_event = None

    for timestamp, line in enumerate(logFile, start=1):
        if " stat" in line:
            stat_pid = line.split(" ")[0]
            stat_timestamp = timestamp
            stat_event = line

        elif "clone" in line:
            clone_pid = line.split(" ")[0]
            clone_timestamp = timestamp
            clone_event = line

        # Check for a valid subsequence, if valid clear out the vars
        # Must be on the same process, and stat must come before clone
        if (
            stat_pid == clone_pid
            and stat_timestamp is not None
            and clone_timestamp is not None
            and clone_timestamp > stat_timestamp
        ):
            result.append(
                {
                    "stat": stat_event,
                    "clone": clone_event,
                    "statPID": stat_pid,
                    "clonePID": clone_pid,
                    "statTime": stat_timestamp,
                    "cloneTime": clone_timestamp,
                }
            )
            print(
                f"Valid Sequence:\nStat Event: '{stat_event.strip()}'\nTimestamp: {stat_timestamp}\nClone Event: '{clone_event.strip()}'\nTimestamp: {clone_timestamp}\n"
            )

            # Clear
            stat_pid = None
            stat_timestamp = None
            stat_event = None
            clone_pid = None
            clone_timestamp = None
            clone_event = None


# Returns each line of a file containing one or more given terms in a list of lists
# [[line, timestamp], [line, timestamp]]
def findTermInLog(logFile, terms):
    result = []

    for timestamp, line in enumerate(logFile, start=1):
        if any(term in line for term in terms):
            result.append([line.strip(), timestamp])

    return result


# Loads a file and returns the lines in a collection
def loadFile(fileName):
    file = open(fileName)
    lines = file.readlines()
    file.close()
    return lines


if __name__ == "__main__":
    main()
