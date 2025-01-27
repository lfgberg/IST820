# Lab 2

## Exercise A

Functional Requirements:

- Output A: the total number of “read” events recorded in the first log file, and all the “read” event log entries contained in the first log file.
- Output B: the total number of “read” events recorded in the second log file, and all the “read” event log entries contained in the second log file.
- Output C: all the log entries contained in the first log file which record a “read from keyboard” (i.e., getting keyboard inputs) event (hint: “read from keyboard” events are closely related to tty).
- Output D: all the log entries contained in the second log file which record a “read from keyboard” (i.e., getting keyboard inputs) event.
- Output E: all the log entries contained in the first log file which record a “read from file” (e.g., read from file /lib/x86_64-linux-gnu/libnss_nis-2.23.so) event (hint: if you are not sure about what to do, browser all the event you get).
- Output F: all the log entries contained in the second log file which record a “read from file” (e.g., read from file /lib/x86_64-linux-gnu/libnss_nis-2.23.so) event.
- Output G: For each of the two log files, output a table which consists of the following rows and columns:
Each row describes a particular file which appears in one or more “read from file” events. Inside each row. The first column is the name of the file. The second column is the total number of times the file was read, i.e., how many read events involved the file.
- Add the third column to the table mentioned in Output G. The third column contains the timestamps of each of the read events counted in the second column. In each log file, the timestamp of the first log entry is “time 1”; the timestamp of the second log entry is “time 2”; and so forth.

## Exercise B

Functional Requirements:

- Output A: output a table which consists of the following rows and columns:
  - The first row has two fields. (a) The total number of “read from a file” events recorded in the first log file; (b) The total number of “read from a file” events recorded in the second log file.
  - The second row has two fields. (a) The total number of “read from keyboard” events recorded in the first log file; (b) The total number of “read from keyboard” events recorded in the second log file.
  - The third row has two fields. (a) The total number of “read from pipe” events recorded in the first log file; (b) The total number of “read from pipe” events recorded in the second log file.
- Output B: output a table which consists of the following rows and columns:
  - The first row has two fields. (a) The total number of “a program starts running” events recorded in the first log file; (b) The total number of “a program starts running” events recorded in the second log file.
  - The second row has two fields. (a) The total number of write events recorded in the first log file; (b) The total number of write events recorded in the second log file.
  - The third row has two fields. (a) The total number of “get file/directory status” events recorded in the first log file; (b) The total number of “get file/directory status” events recorded in the second log file.
  - The fourth row has two fields. (a) The total number of “file unlinking” events recorded in the first log file; (b) The total number of “file unlinking” events recorded in the second log file.
  - The fifth row has two fields. (a) The total number of “a program ends executing” events recorded in the first log file; (b) The total number of “a program ends executing” events recorded in the second log file.
- Output C: output a table which consists of the following rows and columns:
  - The first row has three fields. (a) The name of one executable program. (b) If the executable program appears in the first log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”. (c) If the executable program appears in the second log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”.
  - The second row has three fields. (a) The name of another executable program. (b) If the executable program appears in the first log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”. (c) If the executable program appears in the second log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”.
  - The third row has three fields. (a) The name of a third executable program if it exists. (b) If the executable program appears in the first log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”. (c) If the executable program appears in the second log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”.
  - The fourth row has three fields. (a) The name of a fourth executable program if it exists. (b) If the executable program appears in the first log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”. (c) If the executable program appears in the second log, print the timestamp of the corresponding “a program starts running” event; otherwise, print “absent”.
- Output D: From the first log file, retrieve and output the sequence of user-console interaction events.
  - The events in the sequence are ordered by the “happened before” relation.  
  - When an event let the user provide keystrokes to the console, output the following items: (a) print “the user provides the following keystrokes to the console:”; (b) print the keystrokes recorded in the log.  
  - When an event let the console show a message to the user’s eyes, output the following items: (a) print “the console shows the following message to the user’s eyes:”; (b) print the message recorded in the log, if any.
- Output E: From the second log file, retrieve and output the sequence of user-console interaction events.
  - The events in the sequence are ordered by the “happened before” relation.  
  - When an event let the user provide keystrokes to the console, output the following items: (a) print “the user provides the following keystrokes to the console:”; (b) print the keystrokes recorded in the log.  
  - When an event let the console show a message to the user’s eyes, output the following items: (a) print “the console shows the following message to the user’s eyes:”; (b) print the message recorded in the log, if any.
