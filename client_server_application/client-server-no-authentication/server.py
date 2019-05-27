import socket
import re
import datetime

import sqlite3
import bcrypt
import getpass
import smtplib
import random
import config

def write_startup():
    # Write information to the log file 'server.log'
    new_file = open("server.log", 'a+')
    new_file.write("Server started {} \n".format(str(datetime.datetime.now())))
    new_file.close()

def write_connection():
    # Write information to the log file
    new_file = open("server.log", 'a+')
    new_file.write("Client connected at {} ".format(str(datetime.datetime.now())))
    new_file.write("\nConnection was successful! ")
    new_file.close()

def write_disconnection(start):
    # Write information to the log file
    new_file = open("server.log", 'a+')
    connection = datetime.datetime.now() - start
    new_file.write("\nClient was connected for {} \n".format(str(connection)))
    new_file.write("\n")
    new_file.close()

def write_data(data):
    # Write information to the log file
    new_file = open("server.log", 'a+')
    new_file.write("\nClient requested songs under the artist name {} ".format(data))
    new_file.close()

class ReadingFile:
    def __init__(self):
        # Create regex that will be used for reading the file 'songs.txt
        self.start_line = re.compile('\S')
        self.end_line = re.compile('\d')

    def read_file(self, f_name):
        all_songs_dictionary = {}
        new_file = open(f_name, 'r')
        i = 0
        # Adds 100 songs to the dictionary
        while i < 100:
            hold = new_file.readline()
            # Calls the check function
            test = self.check(hold)

            # Adds the song and artist/artists to the dictionary
            if test == 'full':
                song = hold[4:34].strip()
                author = hold[35:-6].strip()
                for x in author.split('/'):
                    for y in x.split(' featuring '):
                        all_songs_dictionary.setdefault(y, []).append(song)
                i += 1
            elif test == 'name':
                song = hold[4:-1].strip()
                author = new_file.readline()[:-6].strip()
                all_songs_dictionary.setdefault(author, []).append(song)
                i += 1
        new_file.close()
        return all_songs_dictionary

    def check(self, full_line):
        # Uses the regex created previously to check that a line is valid
        if self.start_line.match(full_line[:1]):
            if self.end_line.match(full_line[-4:]):
                # This is when a full line has all the information
                return 'full'
            # This is when 2 lines contain all the information
            return 'name'
        else:
            # This is when the line is not required
            return 'none'


class Server:
    
    data = ''
    
    def __init__(self, songs):
        
        #initialise user database
        self.create_database()
        self.uslt = bcrypt.gensalt(12)
        #self.insert_user_to_database("admin", "123", "ppw2.receiver@gmail.com")
        print(self.fetch_all_from_database())
        print("")
        
        # Initialise the socket and address
        self.server_socket = socket.socket(socket.AF_INET)
        server_address = ('localhost', 6666) ## change if necessary, if changed here you should also change in the client.py program.
        print('Starting up on %s port %s' % server_address)
        try:
            # Attempt to start the server
            self.server_socket.bind(server_address)
            write_startup()
            # Listen for a connection
            self.server_socket.listen(0)
        except socket.error:
            # Catch any errors, such as the port being in use
            print("The server failed to initialise as the socket is already in use!")
            exit()
        self.song_dictionary = songs
        
    def create_database(self):
        #connect to database
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
        #create sql table with relevant fields
        cursor.execute('''
               CREATE TABLE IF NOT EXISTS users(
               userID INTEGER PRIMARY KEY,
               username VARCHAR(255) NOT NULL,
               password VARCHAR(255) NOT NULL,
               uslt VARCHAR(255) NOT NULL,
               email VARCHAR(32) NOT NULL
               );             
        ''')
    
    #add new user to sql user table      
    def insert_user_to_database(self, username, pw, email):
        #connect to database
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
            #generate unique salt for password hashing
            self.uslt = bcrypt.gensalt(12)
            #generate hashed version of password with pre generated salt
            hashed = bcrypt.hashpw(pw.encode('utf-8'), self.uslt)
            
            #store salt and hashed password in table
            insert_user = ("INSERT INTO users(username, password, uslt, email) VALUES(?, ?, ?, ?)")
            cursor.execute(insert_user, [(username), (hashed), (self.uslt), (email)])

            #clear up hashed object
            hashed = None
            
    def fetch_all_from_database(self):
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
            fetch_all_user = ("SELECT * FROM users")
            cursor.execute(fetch_all_user)
            return(str(cursor.fetchall()))
            
    #get hashed password from user table
    def fetch_hash_from_database(self, username):
        #connect to database
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
            #return output of sql query
            return_user = ("SELECT password FROM users WHERE username = ?")            
            cursor.execute(return_user, [(username)])
            hashed = cursor.fetchall()
            return(hashed)
            
    #get unique salt from user table
    def fetch_salt_from_database(self, username):
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
            return_user = ("SELECT uslt FROM users WHERE username = ?")            
            cursor.execute(return_user, [(username)])
            salt = cursor.fetchall()
            return(salt)
            
    #get user email 
    def fetch_user_email_from_database(self, username):
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
            return_user = ("SELECT email FROM users WHERE username = ?")            
            cursor.execute(return_user, [(username)])
            email = cursor.fetchall()
            return(email)
            
    def search_username_from_database(self, username):
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
            return_user = ("SELECT email FROM users WHERE username = ?")            
            cursor.execute(return_user, [(username)])
            user = cursor.fetchall()
            return(user)
        
    def fetch_all_usernames(self):
        with sqlite3.connect("ppw.db") as self.db:
            cursor = self.db.cursor()
            
            return_all = ("SELECT username FROM users ")
            cursor.execute(return_all)    
            users = cursor.fetchall()
            return(users)
        
    #authentication email function
    def send_verification_email(self, receiver):
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            #encrypt connection
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            
            #login to email
            smtp.login(config.EMAIL_ADDRESS, config.EMAIL_PW)
                        
            keygen = str(random.randint(100, 5000))
            
            subject = 'Authentication Code'
            body = 'Code: ' + keygen

            #format email
            msg = f'Subject: {subject}\n\n{body}'
            
            #send email to receiver
            smtp.sendmail(config.EMAIL_ADDRESS, receiver, msg)
            
            return keygen
            
    def running(self):
	
        # Wait for a connection
        # The while loops means that the server will keep listening after a client disconnects, unless they send 'close'		
        while 1:
            print('Waiting for a connection')
            connection, client_address = self.server_socket.accept()
            connection.send("Successful connection!".encode())
            try:
                
                # Set the time that the client connected
                start_time = datetime.datetime.now()
                
                while 1:
                    # Output that a client has connected
                    print('connection from', client_address)
                    write_connection()
                    # Set the time that the client connected
                    start_time = datetime.datetime.now()

                    # after successful connection, query client for username
                    connection.send('Username << '.encode())
                    username = connection.recv(1024).decode()
                    
                    lst = str(self.fetch_all_usernames())
                    tmp = lst[3:-4]
                    
                    print('')
                    
                    if str(username) != str(tmp):                        
                        connection.send('User does not exist\n\nClosing the connection.'.encode())
                        write_disconnection(start_time)
                        connection.close()
                        self.data = ''
                        break
                    else:
                        connection.send('Password << '.encode())
                        password = connection.recv(1024).decode()
                        print('client data recived')



                    #get hashed password from database, where == username
                    x = str(self.fetch_hash_from_database(username))
                    
                    fx = x[4:-4].encode()
                    #convert sql return output to bytes object
                    fp= bytes(fx)
                    
                    #if user input hash ==  stored hash, send pass message to client                    
                    if bcrypt.checkpw(password.encode('utf-8'), fp):
                        connection.send("pass".encode())
                        break
                    else:
                        #if password incorrect, send fail message to client
                        connection.send("fail".encode())  
                        continue
                    
                j = connection.recv(1024).decode()
                
                print(j)
                
                while 1:
                    #get email associated with current user account
                    tmp = str(self.fetch_user_email_from_database(username))
                    #remove padding from string
                    user_email = tmp[3:-4]                    
                    
                    #send verification email to associated email account
                    x = self.send_verification_email(user_email)
                    
                    #send authentication request to client.
                    connection.send('''Please enter authentication code.\n\nAn email has been sent to your account.\n\n
                                    Do not forget to check spam folder for authentication email.\n\n
                                    Please enter authentication code: '''.encode())

                    #get authentication code from client user input
                    cl_inp = connection.recv(1024).decode()
                               
                    #if user input equal to authentication code, authentication is passed
                    if cl_inp == x:
                        #if authentication successful, update client
                        connection.send("p".encode())
                        x = None
                        break
                    else:
                        #if authentication unsuccessful, update client
                        connection.send("f".encode())
                        
                r = connection.recv(1024).decode()
                
                # Loop until the client disconnects from the server
                while 1:
                    #request song from client
                    connection.send('Please search for a song: \n\n'.encode())
                    #recieve song request from client
                    cl_msg = connection.recv(1024).decode()
                    print(cl_msg)
                
                    if (cl_msg != 'quit') and (cl_msg != 'close'):
                        print('received "%s" ' % cl_msg)
                        connection.send('Your request was successfully received!'.encode())
                        write_data(cl_msg)
                        # Check the dictionary for the requested artist name
                        # If it exists, get all their songs and return them to the user
                        if cl_msg in self.song_dictionary:
                            songs = ''
                            for i in range(len(self.song_dictionary.get(cl_msg))):
                                songs += self.song_dictionary.get(cl_msg)[i] + ', '
                            songs = songs[:-2]
                            print('sending data back to the client')
                            connection.send(songs.encode())
                            print("Sent", songs)
                        # If it doesn't exist return 'error' which tells the client that the artist does not exist
                        else:
                            print('sending data back to the client')
                            connection.send('error: artist does not exist \n'.encode())
                    else:
                        # Exit the while loop
                        break
                    # Write how long the client was connected for
                    write_disconnection(start_time)

            except socket.error:
                # Catch any errors and safely close the connection with the client
                print("There was an error with the connection, and it was forcibly closed.")
                write_disconnection(start_time)
                connection.close()
                self.data = ''
                
            finally:
                if self.data == 'close':
                    print('Closing the connection and the server')
                    # Close the connection
                    connection.close()
                    # Exit the main While loop, so the server does not listen for a new client
                    break
                else:
                    print('Closing the connection')
                    # Close the connection
                    connection.close()
                    # The server continues to listen for a new client due to the While loop
                    

read = ReadingFile()
dictionary = read.read_file("songs.txt")
running_server = Server(dictionary)
running_server.running()


