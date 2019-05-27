import socket
import datetime
import getpass
import time

def write_response(start, finish, artist, length):
    # This writes information to the log file 'client.log
    new_file = open("client.log", 'a+')
    new_file.write("Server took {} to complete the request for '{}' ".format(str(finish - start), artist))
    new_file.write("\nThe response length was {} bytes ".format(str(length)))
    new_file.write("\nThe response was received on {} \n".format(str(datetime.datetime.now())))
    new_file.write("\n\n")
    new_file.close()


class RunningConnection:
    def __init__(self):
        # Initialise the socket and address
        self.sock = socket.socket(socket.AF_INET)
        server_address = ('localhost', 6666) #change port number if necessary. If changed here you should also change it in the server.py program.
        print('connecting to %s on port %s' % server_address)
        try:
            # Set a timeout for the connection to allow it to fail if another client is already connected
            self.sock.settimeout(10)
            # Attempt to connect to the server
            self.sock.connect(server_address)
            print("Waiting to connect to the server...")
            print(self.sock.recv(22).decode())
        except socket.timeout:
            # Catch a timeout error
            print("There was a timeout error, as another user is already connected to the server!")
            print("No other connections will be able to be made to the server whilst it is running.")
            exit()
        except socket.error:
            # Catch any other errors that may arise, such as the server not running
            print("There was an error connecting to the server as it is not available/running.")
            exit()

    def running(self):
        try:
            
            # Set the time that the client connected
            start_time = datetime.datetime.now()

			# Loop until the user logs in succesfully
            while 1:

                #login loop
                while 1:
                    msg = self.sock.recv(1024).decode()
                    u_input = input(msg)
                    username = u_input
                    self.sock.send(u_input.encode())

                
                    msg = self.sock.recv(1024).decode()
                    u_input = getpass.getpass(msg)
                    password = u_input
                    self.sock.send(u_input.encode())

                    msg = self.sock.recv(1024).decode()

                    if msg == 'pass':
                        print("Login successful \n")
                        self.sock.send('success'.encode())
                        break
                    else:
                        print("Login failed")
                        print("Disconnecting!")
                        self.sock.close()
                        
                while 1:
                    sv_msg = self.sock.recv(1024).decode()
                                   
                    inp = input(sv_msg)
    
                    self.sock.send(inp.encode())
                    
                    sl_msg = self.sock.recv(1024).decode()
                    
                    print(sl_msg)
                    
                    if str(sl_msg) == 'p':
                        print("Authentication successful")
                        self.sock.send('received server data'.encode())
                        break
                    else:
                        print("Authentication failed. Closing the connection.")
                        msg = input()
                        
                    
                sv_msg = self.sock.recv(1024).decode()
                
                cl_msg = ''
                
                #loop until user inputs request
                while cl_msg == '':
                    
                    cl_msg = input(sv_msg)
                    
                    if cl_msg == '':
                        print("ERROR: Message is empty!")
                    
                self.sock.send(cl_msg.encode())
                    
                    # If the user input 'quit' or 'close', exit the while loop and close the connection
                if cl_msg == 'quit' or cl_msg == 'close':
                    print("Disconnecting!")
                    self.sock.close()
                    break
                
                # Output what the user is sending to the terminal
                print('You are sending "%s" message to the server: ' % cl_msg)
                time.sleep(1)
                # Receive a response from the server
                data = self.sock.recv(39)
                time.sleep(2)
                print(data.decode())
                data = self.sock.recv(1024)
                time.sleep(3)

                # 'error' is returned if no songs are found, otherwise the songs are displayed on the terminal
                if data.decode() == 'error':
                    print("There are no songs under the author", cl_msg)
                else:
                    print("The songs made by ", cl_msg, "are: \n\n")
                    print(data.decode())
                    print('')

                # Set the finish time, and call the function to write to the log file
                finish_time = datetime.datetime.now()
                write_response(start_time, finish_time, cl_msg, len(data))
                print("\nType in 'quit' to disconnect, or 'close' to quit and shut down the server!\n")
                cl_msg = ''
                
        except socket.timeout:
            # Catch a timeout error
            print("There was a timeout error!")
            self.sock.sendall('quit'.encode())
            self.sock.close()
            exit()
        except socket.error:
            # Catch any other errors that may arise, such as the server not running
            print("There was an error with the connection!")
            exit()
        finally:
            # Close the connection
            self.sock.close()


connect_client = RunningConnection()
connect_client.running()
