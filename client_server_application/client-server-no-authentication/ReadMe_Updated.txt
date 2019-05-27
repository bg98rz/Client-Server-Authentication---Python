---------- Running on Windows/Linux via command line: ----------

This system is compatible with Python version 3.5 and above.

********** Initialising and starting the system **********
Step one: start the server program first
- open a command line
- navigate to the folder where the system is stored
- run "python server.py"

Step two: start the client program
- open a different command line
- navigate to the same folder where the system is stored
- run "python client.py"


********** using the system **********
- Once the server and the client programs are running, you are prompted to enter 
  a username and password combination. 


  Sardar please use this account for login:		

		username: admin 
		password: 123



- If login authentication if passed, user is prompted to complete email authentication. 

  Sardar, to receive authenticaiton email please use this account:

		email:  ppw2.receiver@gmail.com
		pass :	cybersec123


- If email authenticaiton is passed, user can search for songs 
  associate with specific artists via the client program.


- The client prompts you to enter the name of an artist. Enter a name from the 
songs.txt file, e.g., ABBA. The client then returns the songs for Abba

********** Shuting down the system **********
- To close client connection with the server, but leaving server running 
(e.g., allow another client to connect) enter 'quit' from the client's command line window.
- To close the connection and abort the system enter 'close' form the client's command line window

Notes:
- Log files do not get overwritten! Delete them to get fresh log files.
- If server is forcibly closed then log file will not be written.