import pickle
import socket
import threading
from tkinter import *
import LOGARITHM
import CONSTANTS
import Utilities
import logging


class Node:
    '''
    Notes to remember:
    can only send bytes and not strings.
    '''
    '''Variables'''

    # Lists For Clients and Their Nicknames
    nickname = "Andrefff"  # input("Tell us your name:")  # CHANGE FOR SECOND NODE
    balance = 100

    clients = []
    nicknames = []
    Servers = []
    listOfBets = []
    host = CONSTANTS.LOCAL_HOST_IPV4
    port = CONSTANTS.PORT

    # MONERO DETAILS
    # Wallet = Wallet(JSONRPCWallet(port=28088))

    '''SERVER RELATED STUFF'''

    # Starting Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def starting_server(self):
        self.server.bind((CONSTANTS.LOCAL_HOST_IPV4, CONSTANTS.PORT))
        self.server.listen()

    # Sending Messages To All Connected Clients
    def broadcast_to_clients(self, message):
        for client in self.clients:
            client.send(message)

    # Handling Messages From Clients
    def handle_client_msg(self, client):
        """
        :param client:
        Everytime a client connects to our server we run this function for it and it starts an endless loop.
        What it then does is receiving the message from the client (if he sends any) and broadcasting it to all connected clients
        If for some reason there is an error with the connection to this client, we remove it and its nickname, close the connection and broadcast that this client has left the chat.
        :return:
        """
        while True:
            try:
                # Broadcasting Messages
                message = client.recv(1024)
                self.broadcast_to_clients(message)
            except Exception as e:
                print(f'CALLING EXCEPTION: {e}')  # super helpful!
                # Removing And Closing Clients
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast_to_clients(f'{nickname} left!'.encode('utf-8'))
                self.nicknames.remove(nickname)
                break

    # Receiving / Listening Function
    def listen(self):
        print("Waiting for connections...")
        '''
        starts an endless while-loop which constantly accepts new connections from clients.
        sends the string ‘NICK’ to it, which will tell the client that its nickname is requested
        After that it waits for a response (which hopefully contains the nickname) and appends the client with the respective nickname to the lists
        start a new thread that runs the previously implemented handling function for this PARTICULAR client.
        :return:
        '''
        while True:
            # Accept Connection
            client, address = self.server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('NICK'.encode('utf-8'))
            nickname = client.recv(1024).decode('utf-8')
            self.nicknames.append(nickname)
            self.clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname))
            self.broadcast_to_clients("{} joined!".format(nickname).encode('utf-8'))
            client.send('Connected to server!'.encode('utf-8'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=self.handle_client_msg, args=(client,))
            thread.start()

    '''------------------------------------------------------------------------------------------------'''
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connecting To Server
    def connect_to_server(self):
        '''
        Instead of binding the data and listening, we are connecting to an existing server.
        :return:
        '''
        self.client.connect((CONSTANTS.LOCAL_HOST_IPV4, CONSTANTS.PORT))
        Utilities.log_message('Connected To Server', 'client')

    # Listening to Server and Sending Nickname
    def receive_from_server(self):
        """
        It constantly tries to receive messages and to print them onto the screen.
        If the message is ‘NICK’ however, it doesn’t print it but it sends its nickname to the server.
        :return:
        """
        first_instance = True
        count = 1
        while True:
            try:
                message = pickle.loads(self.client.recv(100000))
                # If 'NICK' Send Nickname
                if message["TYPE"] == "NICK":
                    nickname_dict = {
                        "TYPE": "CLIENT_NAME",
                        "VALUE": self.nickname
                    }
                    self.client.send(pickle.dumps(nickname_dict))
                elif message['TYPE'] == 'BROADCAST':
                    print(message['MESSAGE'])
                elif message['TYPE'] == 'SERVER_BETS':
                    print("\nTHESE ARE THE SERVERS CURRENT BETS...:")
                    for i in message['VALUE']:
                        print(i)
                elif message['TYPE'] == 'BALANCE CHECK':
                    print('\nPROPOSAL BETWEEN TWO PEOPLE')
                    print(message)
                    print(self.balance)
                    if self.balance >= message['Opponent Bet Value']:
                        print(self.nickname + ' has enough')
                        has_enough = True
                    else:
                        print(self.nickname + ' does not have enough')
                        has_enough = False
                    dict_to_send = {
                        'TYPE': 'BALANCE CHECK CONFIRMATION',
                        'NICKNAME': self.nickname,
                        'HAS ENOUGH': has_enough,
                        'BET SIZE': message['Opponent Bet Value'],
                        'BET KEY': message['BET KEY']
                    }
                    self.client.send(pickle.dumps(dict_to_send))
                elif message['TYPE'] == 'BET EXECUTION':
                    print('\nEXECUTING BALANCE CHANGES...')
                    print(message)
                    print(f"Current balance: {self.balance}")

                    sending = message['AMOUNT']
                    execution_confirmation_dict = {
                        'TYPE': 'FUND EXTRACTION',
                        'NICKNAME': self.nickname,
                        'AMOUNT': message['AMOUNT'],
                        'BET KEY': message['BET KEY']

                    }
                    self.balance = self.balance - message['AMOUNT']

                    print(f"Updated balance: {self.balance}")
                    print(f"Sending out:{sending}")

                    self.client.send(pickle.dumps(execution_confirmation_dict))
                elif message['TYPE'] == 'AMOUNT':
                    print('WINNINGS')
                    print(message)
                    print(message['AMOUNT'])
                    print(type(message['AMOUNT']))
                    self.balance += float(message['WINNINGS'])  # monero addr
                elif message['TYPE'] == 'DIFFERENT CLI/SERVER':
                    print('different clients, send a request for their code')
                    print('THEIR CLIENT', message['THEIR CLIENT HASH'])
                    print('YOUR CLIENT', message['YOUR CLIENT HASH'], '\n')
                    print('THEIR CLIENT', message['THEIR CLIENT HASH'])
                    print('YOUR CLIENT', message['YOUR CLIENT HASH'])
                elif message['TYPE'] == 'CODE REQUEST':
                    print('CODE REQUEST')
                    client_txt = Utilities.get_client_txt()
                    server_txt = Utilities.get_server_txt()

                    send_to_dict = {
                        'TYPE': 'SENDING CODE',
                        'TO': F'{message["ASKER CLIENT"]}',  # confusing
                        'FROM': F'{message["PROVIDER CLIENT"]}',
                        'CLIENT TEXT': client_txt,
                        'SERVER TEXT': server_txt,
                        'ASKER NICKNAME': message['ASKER CLIENT NAME'],
                        'PROVIDER NICKNAME': message['PROVIDER CLIENT NAME']
                    }
                    self.client.send(pickle.dumps(send_to_dict))
                elif message['TYPE'] == 'SENT FILES':
                    Utilities.put_files_in_folder(message['PROVIDER NICKNAME'], message['CLIENT'], message['SERVER'])
                else:
                    print(message)
            except Exception as e:
                print(f'CALLING EXCEPTION: {e}')  # super helpful!
                Utilities.log_message(f'CALLING EXCEPTION: {e}', 'client')
                # Close Connection When Error
                print("An error occurred!")
                self.client.close()
                break

    # Sending Messages To Server
    def write_to_server(self):
        while True:
            msg_dict = {"Type": "MESSAGE",
                        "VALUE": f"{self.nickname}: {input('')}"
                        }
            self.client.send(pickle.dumps(msg_dict))
            break

    # Starting Threads For Listening And Writing
    def run_threads(self):
        receive_thread = threading.Thread(target=self.receive_from_server)
        receive_thread.start()
        write_thread = threading.Thread(target=self.write_to_server)
        write_thread.start()

    '''BET INFORMATION------------------------------------------------------------------------------------------------'''
    proposed_bet = betFunctions.propose_single_bet()

    def propose_bet_to_server(self, betDetails=proposed_bet):
        while True:
            message = f"{self.nickname} proposed \n{betDetails}\n"
            self.client.send(message.encode('utf-8'))
            break

    '''BET INFORMATION------------------------------------------------------------------------------------------------'''
    bet_num = 0  # THIS IS FOR THE HOST BETS, THE NUMBER OF BETS THE HOST HAS PROPOSED
    bets = []

    '''GUI Related Stuff'''

    def run_client_gui(self):
        root = Tk()  # Create root
        root.title(f"Gladiator CLIENT Test {self.nickname}")
        root.geometry("500x500")
        bet_details = []

        def askBets():
            ask_message = {
                "TYPE": "REQUEST",
                "NICKNAME": self.nickname,
            }
            self.client.send(pickle.dumps(ask_message))

        def click_propose_bets():
            # betValue = float(betAmountInput.get())
            # betRatio = float(betAmountRatio.get())
            betValue = 10
            betRatio = 1.1
            gladiator_percent = 5
            betEnterPerson1 = 'Covington'
            betEnterPerson2 = 'Masvidal'
            betType = 'Victory'

            client_hash = Utilities.get_client_hash()
            server_hash = Utilities.get_server_hash()

            tempDict = {
                "TYPE": "BET",
                "NICKNAME": self.nickname,
                "KEY": self.bet_num,
                "Bet Value": betValue,
                "Bet Type": betType,
                "Bet Ratio": betRatio,
                "Bet Participant1": betEnterPerson1,
                "Bet Participant2": betEnterPerson2,
                "Bet Focus": betEnterPerson2,
                "Potential Winnings": betRatio * betValue,
                "Opponent Bet Value": betRatio * betValue,
                "Opponent Potential Winnings": betValue,
                "Gladiator Percent": gladiator_percent,
                "Host Percent": {
                    "PROPOSER VICTORY": round(Utilities.get_log_percent(betValue), 2),
                    "OPPONENT VICTORY": round(Utilities.get_log_percent(betRatio * betValue), 2)
                },
                'CLIENT HASH': client_hash,
                'SERVER HASH': server_hash
            }
            while True:
                message = tempDict
                self.client.send(pickle.dumps(message))
                print('SENT BET...')
                Utilities.log_message(f'SENT BET...', F'{self.client}')
                # print(message)
                break
            self.bet_num += 1

        betEnterLabel = Label(root, text='CREATE A BET AND SEND TO SERVERS')
        betEnterLabel.grid(row=1, column=1, columnspan=1)

        myButton = Button(root, text="Ask For Bets", command=askBets)
        myButton.grid(row=14, column=1, columnspan=3)

        betEnterLabel = Label(root, text='Enter Bet Amount    :')
        betEnterLabel.grid(row=2, column=0, columnspan=1)
        betAmountInput = Entry(root)  # WHERE INPUT COMES FROM
        betAmountInput.grid(row=2, column=1, columnspan=1)

        # DROP DOWN

        BetTypeLabel = Label(root, text='Bet Type    :')
        BetTypeLabel.grid(row=3, column=0, columnspan=1)
        variable = StringVar(root)
        variable.set("Victory")  # default value
        dropdown = OptionMenu(root, variable, "Victory", "Defeat")
        dropdown.grid(row=3, column=1, columnspan=1)

        R1 = Radiobutton(root, text="Person 1", value=1)
        R1.grid(row=4, column=5)

        R2 = Radiobutton(root, text="Person 2", value=2)
        R2.grid(row=5, column=5)

        betEnterPerson1 = Label(root, text='Bet Person1        :')
        betEnterPerson1.grid(row=4, column=0, columnspan=1)
        betEnterPerson1input = Entry(root)  # WHERE INPUT COMES FROM
        betEnterPerson1input.grid(row=4, column=1, columnspan=1)

        betEnterPerson2 = Label(root, text='Bet Person2        :')
        betEnterPerson2.grid(row=5, column=0, columnspan=1)
        betEnterPerson2input = Entry(root)  # WHERE INPUT COMES FROM
        betEnterPerson2input.grid(row=5, column=1, columnspan=1)

        betEnterRatio = Label(root, text='Enter Bet Ratio         :')
        betEnterRatio.grid(row=6, column=0, columnspan=1)
        betAmountRatio = Entry(root)  # WHERE INPUT COMES FROM
        betAmountRatio.grid(row=6, column=1, columnspan=1)

        gladiator_percent = Label(root, text="What Percent to Gladiator    :")
        gladiator_percent.grid(row=7, column=0, columnspan=1)
        gladiator_percent_input = Entry(root)  # WHERE INPUT COMES FROM
        gladiator_percent_input.grid(row=7, column=1, columnspan=1)

        # -- SECTION

        blankSpace = Label(root, text='\nCHOOSING / REQUESTING OPPONENT BETS')
        blankSpace.grid(row=9, column=1, columnspan=1)

        myButton = Button(root, text="Submit Bet", command=click_propose_bets)
        myButton.grid(row=8, column=1, columnspan=3)

        def ask_for_code():
            # opponent_nickname_for_exchange = opponent_nickname_label_Input_for_exchange.get()
            # opponent_bet_key_for_exchange = opponent_bet_key_input_for_exchange.get()

            opponent_nickname_for_exchange = 'Andre'
            opponent_bet_key_for_exchange = 1
            print('REQUESTING CODE FROM PERSON')

            request_dict = {
                'TYPE': 'CODE REQUEST',
                'BET HOST NICKNAME': opponent_nickname_for_exchange,
                'BET KEY': opponent_bet_key_for_exchange,
                'NICKNAME': self.nickname,
            }
            while True:
                self.client.send(pickle.dumps(request_dict))
                break

        # ACCEPTING THE A BET
        def choose_bet():
            # opponent_nickname = opponent_nickname_label_Input.get()
            # opponent_bet_key = opponent_bet_key_input.get()

            opponent_nickname = 'Andre'
            opponent_bet_key = 1
            send_bet_confirmation(opponent_nickname, opponent_bet_key)

        def send_bet_confirmation(nickname, key):
            print('SENDING BET CONFIRMATION')

            client_hash = Utilities.get_client_hash()
            server_hash = Utilities.get_server_hash()

            confirmationDict = {
                'TYPE': 'CONFIRMATION',
                'NICKNAME': self.nickname,
                'OPP NICKNAME': nickname,
                'BET KEY': key,
                'CLIENT HASH': client_hash,
                'SERVER HASH': server_hash
            }
            while True:
                self.client.send(pickle.dumps(confirmationDict))
                # print(message)
                break

        opponent_nickname_label = Label(root, text="Opponent Nickname:")
        opponent_nickname_label.grid(row=11, column=0, columnspan=1)
        opponent_nickname_label_Input = Entry(root)  # WHERE INPUT COMES FROM
        opponent_nickname_label_Input.grid(row=11, column=1, columnspan=1)

        opponent_bet_key = Label(root, text="Opponent BET_KEY    :")
        opponent_bet_key.grid(row=12, column=0, columnspan=1)
        opponent_bet_key_input = Entry(root)  # WHERE INPUT COMES FROM
        opponent_bet_key_input.grid(row=12, column=1, columnspan=1)

        myButton = Button(root, text="Choose bet", command=choose_bet)
        myButton.grid(row=13, column=1, columnspan=3)

        myButton = Button(root, text="Ask For Bets", command=askBets)
        myButton.grid(row=14, column=1, columnspan=3)

        # -- SECTION
        blankSpace = Label(root, text='\nGET CLIENT AND SERVER FROMS SOMEBODY ')
        blankSpace.grid(row=15, column=1, columnspan=1)

        opponent_nickname_label_for_exchange = Label(root, text="Opponent Nickname:")
        opponent_nickname_label_for_exchange.grid(row=16, column=0, columnspan=1)
        opponent_nickname_label_Input_for_exchange = Entry(root)  # WHERE INPUT COMES FROM
        opponent_nickname_label_Input_for_exchange.grid(row=16, column=1, columnspan=1)

        opponent_bet_key_for_exchange = Label(root, text="Opponent BET_KEY    :")
        opponent_bet_key_for_exchange.grid(row=17, column=0, columnspan=1)
        opponent_bet_key_input_for_exchange = Entry(root)  # WHERE INPUT COMES FROM
        opponent_bet_key_input_for_exchange.grid(row=17, column=1, columnspan=1)

        myButton = Button(root, text="Ask for the code", command=ask_for_code)
        myButton.grid(row=18, column=1, columnspan=3)

        root.mainloop()


'''Client STUFF'''
node = Node()
node.connect_to_server()
node.run_threads()
# node.propose_bet_to_server()
node.run_client_gui()
