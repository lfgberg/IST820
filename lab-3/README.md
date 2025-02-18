# Lab 3

## Exercise A

Please write a Python program to analyze the given log files and print to console the following outputs:
• Output A: The first log file contains two particular kinds of events: stat events and clone events,
respectively. Please output all the following two-event sequences contained in the first log file.
o Inside each such two-event sequence:
▪ The first event must be a stat event.
▪ The second event must be a clone event.
▪ The first event must precede the second event.
▪ The two events do not need to be neighbors.
▪ Both events must have happened to the same pid (process id).
▪ Between these two events, there isn’t any other stat or clone event which has
happened to the aforementioned pid.
▪ Please output the whole log entry for each of the two events.
▪ Please output the timestamp of each of the two events.
• Output B: The second log file or the third log file contains two particular kinds of events: stat events
and clone events, respectively. Please do the same thing described in Output A against the second log
file and the third log file.
• Output C: One of the three log files contains three particular kinds of events: open events, getdents
events, and close events. Please find the log file that contains all the three kinds of events, and output
all the following three-event sequences:
o Inside each such three-event sequence:
▪ The first event must be an open event.
▪ The second event must be a getdents event.
▪ The third event must be a close event.
▪ The first event must precede the second event, and the second event must precede
the third event.
▪ The three events do not need to be neighbors.
▪ All of the three events must have happened to the same pid (process id).
o Inside each such three-event sequence:
▪ There is no other open or close event that comes from the same pid and stands
between the open event and the close event.
▪ Please output the whole log entry for each of the three events.
▪ Please output the timestamp of each of the three events.

## Exercise B

Among the three given log files, only one log file records the corresponding malicious events.
• After you identify the log file that contains the malicious events, please output the following:
o Output A: The second stage of the attack is “Download malicious code”. This stage
corresponds to a subsequence of 3 events: open a particular file; write the content to the file;
close the file. Please output the corresponding three-event subsequences. Please output the
whole log entry for each of the three events.
o Output B: The fourth stage of the attack is “Modify permission”. The malicious event during this
stage uses the keyword “fchmodat”. This type of event changes the permission of a file.
Please output the corresponding event log entries. Please make sure that the file name is the
same as the file name in one of the three-event subsequences in Output A.
o Output C: The sixth stage of the attack is “Run the malicious code”. The malicious event during
this stage uses the keyword “execve”. Please output the corresponding event log entries.
Please make sure that the file name is the same as the file name in one of log entries in Output
B.
