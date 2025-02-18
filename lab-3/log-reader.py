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
        exerciseB(logFileA, logFileB, outfileName)


def exerciseA(logFileA, logFileB, logFileC):
    print("Stat-Clone sequences from Log A:\n")
    printStatNumSequences(logFileA)
    print("Stat-Clone sequences from Log B:\n")
    printStatNumSequences(logFileB)
    print("Stat-Clone sequences from Log C:\n")
    printStatNumSequences(logFileC)


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


def exerciseB(logFileA, logFileB, outFileName):
    print("What the sigma?")


# Loads a file and returns the lines in a collection
def loadFile(fileName):
    file = open(fileName)
    lines = file.readlines()
    file.close()
    return lines


if __name__ == "__main__":
    main()
