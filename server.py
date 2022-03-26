'''
Coder: Dre Foreman
Purpose:
Date:
'''

import pickle
import socket
import threading
import CONSTANTS
import Utilities
from Utilities import *


class Node:
    '''
    Notes to remember:
    can only send bytes and not strings.
    '''
    '''Variables'''

    # Lists For Clients and Their Nicknames
    # name = "Andre" #CHANGE FOR SECOND NODE
    clients = []
    nicknames = []
    Servers = []
    host = CONSTANTS.LOCAL_HOST_IPV4
    port = CONSTANTS.PORT
    bets = []
    nickname_client_dict = {}

    # MONERO DETAILS
    # Wallet = Wallet(JSONRPCWallet(port=28088))
    fakeMoneroPerson = {
        'ADDRESS': 'ABC123',
        'NAME': 'Jorge'
    }

    '''------------------------------------------------------------------------------------------------'''
    '''SERVER RELATED STUFF'''
    # Starting Server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def starting_server(self):
        # sometimes CONSTANTS.LOCAL_HOST_IPV4 RANDOMLY stops working
        self.server.bind((CONSTANTS.LOCAL_HOST_IPV4, CONSTANTS.PORT))
        self.server.listen()

    def broadcast_to_clients(self, message):
        sent_dict = {'TYPE': 'BROADCAST',
                     'MESSAGE': message}
        for client in self.clients:
            client.send(pickle.dumps(sent_dict))

    def broadcast_singular_json(self, message):
        print_green(message)
        for client in self.clients:
            print_green(client)
            client.send(pickle.dumps(message))
            print_green('executed this')

    def full_bet_execution(self, execution_dict):
        print_green('\nFULL BET EXECUTION WITH KEY')
        print_green(execution_dict)
        for key, value in execution_dict.items():
            if key != 'BET KEY':
                message = {
                    'TYPE': 'BET EXECUTION',
                    'AMOUNT': value[0],
                    'BET KEY': execution_dict['BET KEY']
                }
                # print(key, value)
                value[1].send(pickle.dumps(message))
            else:
                print(key, value, 'is bet key')  # not sending out to people

    def remove_bet(self, better, key):
        for i in self.bets:
            # print(i)
            if i['KEY'] == key:  # SOMEWHERE IN THE CODE THIS MUST CHANGE TO BET KEY
                if i['NICKNAME'] == better:  # check for names of betters
                    self.bets.remove(i)

    # Handling Messages From Clients
    dict_of_bet_details = {'BETTERS': 0}

    def handle_client_msg(self, client):
        '''
        :param client:
        Everytime a client connects to our server we run this function for it and it starts an endless loop.
        What it then does is receiving the message from the client (if he sends any) and broadcasting it to all connected clients
        If for some reason there is an error with the connection to this client, we remove it and its nickname, close the connection and broadcast that this client has left the chat.
        :return:
        '''

        def execute_bet(stored_bet, challenger_message):
            print_green("Executing Bet...")

            # print(stored_bet)
            # print(challenger_message)

            def check_both_parties_balances(stored_bet_=stored_bet, challenger_message_=challenger_message):
                print_green("\nChecking Balances")
                dict_to_send = {
                    'TYPE': 'BALANCE CHECK'
                }
                challenger_message_.update(dict_to_send)
                # print('testing dict')
                # print(stored_bet_)
                # print(challenger_message_)
                # print('got to here1')
                mini_dict = {'Opponent Bet Value': stored_bet_['Opponent Bet Value']}
                challenger_message_.update(mini_dict)
                # print(challenger_message_)
                # print('got to here2')
                client.send(pickle.dumps(challenger_message_))
                # balances_check = pickle.loads(client.recv(100000))
                # print('BALANCES CHECK')
                # print(balances_check)

            check_both_parties_balances()

        # IDK HOW NECESSARY THESE GLOBALS ARE, THIS IS KIND OF DESIGNED POORLY
        global found_match, RESULT, current_bet

        while True:
            try:
                # Broadcasting Messages
                message = pickle.loads(client.recv(100000))
                # print(str(message))
                # print(message['TYPE'])
                # print(type(message))
                if message["TYPE"] == 'BET':
                    print_green("\nRECIEVED BET...")
                    self.bets.append(message)
                elif message['TYPE'] == "REQUEST":
                    # self.broadcast_singular()
                    print_green(f"\nSENDING CURRENT BETS TO {message['NICKNAME']}")
                    send_back_bets = {
                        'TYPE': 'SERVER_BETS',
                        'VALUE': self.bets
                    }
                    client.send(pickle.dumps(send_back_bets))
                elif message['TYPE'] == 'CONFIRMATION':
                    bet_found = False
                    print_green("\nCONFIRMING BET BETWEEN OPPONENTS...")
                    for i in self.bets:
                        # other criteria to check ehre
                        if i['KEY'] == message['BET KEY'] and i['NICKNAME'] == message['OPP NICKNAME']:
                            print_green('This is the bet being used')
                            print(i)
                            bet_found = True
                            found_match = i

                            if found_match['CLIENT HASH'] != message['CLIENT HASH'] or found_match['SERVER HASH'] != \
                                    message['SERVER HASH']:
                                bet_found = False

                                # HE CHOSE THE BET BUT IS RUNNING DIFFERENT CODE THAN THE GUY HE WANTED TO BET
                                print(f'MISMATCHED SOFTWARE')
                                print(f'Clients {found_match["CLIENT HASH"]} | {found_match["SERVER HASH"]}')
                                print(f"Servers {found_match['SERVER HASH']} | {message['SERVER HASH']}")

                                send_client_server_dict = {
                                    'TYPE': 'DIFFERENT CLI/SERVER',
                                    'TITLE': f'{i["NICKNAME"]}',
                                    'THEIR CLIENT HASH': found_match["CLIENT HASH"],
                                    'THEIR SERVER HASH': found_match['SERVER HASH'],
                                    'YOUR CLIENT HASH': message["CLIENT HASH"],
                                    'YOUR SERVER HASH': message['SERVER HASH']
                                }
                                client.send(pickle.dumps(send_client_server_dict))
                            break
                        else:
                            print('Not a match')
                    if bet_found:
                        print_green('Found Match:')
                        print(found_match)
                        # print(message)
                        execute_bet(found_match, message)
                elif message['TYPE'] == 'BALANCE CHECK CONFIRMATION':
                    print_green("\nCHECKING BALANCE BETWEEN PARTIES...")
                    print(message)
                    if message['HAS ENOUGH'] == True:
                        print_green(f"{message['NICKNAME']} has high enough balance to bet {message['BET SIZE']}")
                        print(f"Executing bet between {message['NICKNAME']} and {found_match['NICKNAME']}")

                        # INDEXED BY CLIENT NICKNAME ENTERED
                        # print(str(message['NICKNAME']) + str(self.nickname_client_dict[message['NICKNAME']]))
                        # print(str(found_match['NICKNAME']) + str(self.nickname_client_dict[found_match['NICKNAME']]))
                        print_green('KEY TESTING MESSAGE:')
                        print(message)
                        temp_dict_for_execution = {
                            message['NICKNAME']: [message['BET SIZE'], self.nickname_client_dict[message['NICKNAME']]],
                            found_match['NICKNAME']: [found_match['Bet Value'],
                                                      self.nickname_client_dict[found_match['NICKNAME']]],
                            'BET KEY': message['BET KEY']
                        }
                        self.full_bet_execution(temp_dict_for_execution)

                    else:
                        print_green(
                            f"{message['NICKNAME']} does not have high enough balance to bet {message['BET SIZE']}")
                elif message['TYPE'] == 'FUND EXTRACTION':
                    print_green("\nCONFIRMED FUND EXTRACTION BETWEEN PARTIES...")
                    # print(message)

                    # del message['FUND EXTRACTION'] # remove annoying part of dict DOESNT WORK?
                    self.dict_of_bet_details[f'{message["NICKNAME"]}'] = message
                    self.dict_of_bet_details["BETTERS"] += 1
                    print(self.dict_of_bet_details)

                    if self.dict_of_bet_details["BETTERS"] == 2:
                        print_green('\nAPI EXECUTION, PROBABLY ASYNC..')
                        better1 = list(self.dict_of_bet_details.keys())[1]  # getting the index of keys to this dict
                        better2 = list(self.dict_of_bet_details.keys())[2]
                        print(f'BETTER1 IS {better1}')
                        print(f'BETTER2 IS {better2}')
                        # print(better1, better2)
                        # print(self.dict_of_bet_details[f'{better1}'], self.dict_of_bet_details[f'{better2}'])

                        result_dict = Utilities.get_fight_result()
                        print('RESULT FROM SCRAPING SITE', result_dict)
                        print('DICT OF BET DETAILS', self.dict_of_bet_details)

                        # GRABBING THE CORRECT BET
                        for i in self.bets:  # SOMETHING WRONG HERE, 'KEY': 2 # there is some confusion here
                            if i['NICKNAME'] in self.dict_of_bet_details:
                                current_choice = self.dict_of_bet_details[i['NICKNAME']]  # ignored error here
                                if i['KEY'] == current_choice['BET KEY']:  # where 1 IS A VARIABLE
                                    current_bet = i
                                    break
                                    # print('FOUND BET :', current_bet)

                        print_green(f'CURRENT BET\n{current_bet}')
                        # check who won the bet and assign them the winner
                        if current_bet["NICKNAME"] == better1:
                            print('NO CHANGE ', current_bet["NICKNAME"], 'is', better1)
                            OPPO = better2
                        else:
                            print('CHANGE, ', current_bet["NICKNAME"], 'is ', better2)
                            OPPO = better1
                        print(current_bet['Bet Focus'], result_dict['WINNER'])
                        if current_bet['Bet Focus'] in result_dict['WINNER'] and current_bet['Bet Type'] == 'Victory':
                            print(f'{current_bet["NICKNAME"]} WON betting {result_dict["WINNER"]} would WIN')
                            RESULT = {
                                'TYPE': 'API RESULT',
                                'WINNER': f'{current_bet["NICKNAME"]}',
                                'LOSER': OPPO
                            }
                        elif current_bet['Bet Focus'] in result_dict['LOSER'] and current_bet['Bet Type'] == 'Victory':
                            print(f'{current_bet["NICKNAME"]} LOST betting {result_dict["LOSER"]} would WIN')
                            RESULT = {
                                'TYPE': 'API RESULT',
                                'WINNER': OPPO,
                                'LOSER': f'{current_bet["NICKNAME"]}',
                            }
                        elif current_bet['Bet Focus'] in result_dict['WINNER'] and current_bet['Bet Type'] != 'Victory':
                            print(f'{current_bet["NICKNAME"]} LOST betting {result_dict["WINNER"]} would LOSE')
                            RESULT = {
                                'TYPE': 'API RESULT',
                                'WINNER': OPPO,
                                'LOSER': f'{current_bet["NICKNAME"]}',
                            }
                        elif current_bet['Bet Focus'] in result_dict['LOSER'] and current_bet['Bet Type'] != 'Victory':
                            print(f'{current_bet["NICKNAME"]} WON betting {result_dict["LOSER"]} would LOSE')
                            RESULT = {
                                'TYPE': 'API RESULT',
                                'WINNER': f'{current_bet["NICKNAME"]}',
                                'LOSER': OPPO,
                            }

                        print_green(RESULT)

                        print_green(f'\n{RESULT["WINNER"]} is the WINNER')  # ande
                        print_green(f'Bet details: {RESULT}')
                        bet_key = message['BET KEY']

                        winner = RESULT["WINNER"]
                        loser = RESULT["LOSER"]

                        if winner == current_bet['NICKNAME']:
                            winnings = current_bet['Potential Winnings']
                        else:
                            winnings = current_bet['Bet Value']

                        # print(winnings)

                        winner_client = self.nickname_client_dict[winner]
                        loser_client = self.nickname_client_dict[loser]
                        final_dict = {
                            'TYPE': 'BET COMPLETION CONFIRMATION',
                            'WINNER': winner,
                            'LOSER': loser,
                            'BET KEY': bet_key,
                            'WINNINGS': winnings,
                            'WINNER CLIENT': winner_client,
                            'LOSER CLIENT': loser_client
                        }
                        print_green(f'\nIMPORTANT DICT {final_dict}\n')

                        '''HERE WOULD BE THE MONERO TRANSACTION
                           SOMEHOW THERE NEEDS TO BE ACCOUNTABILITY FOR DISCONNECTING
                        '''

                        send_winnings_dict = {
                            'TYPE': 'WINNINGS',
                            'AMOUNT': final_dict['WINNINGS']
                        }

                        final_dict['WINNER CLIENT'].send(pickle.dumps(send_winnings_dict))
                        for i in self.bets:
                            # print(i)
                            if i['KEY'] == bet_key:  # SOMEWHERE IN THE CODE THIS MUST CHANGE TO BET KEY
                                print(i)
                                if i['NICKNAME'] == winner or i['NICKNAME'] == loser:
                                    print('BET REMOVAL BETWEEN', winner, loser, bet_key)
                                    self.bets.remove(i)
                        self.dict_of_bet_details = 0
                        print('FINISHED BET EXECUTION\n')
                elif message['TYPE'] == 'CODE REQUEST':
                    print('\nCODE REQUEST')
                    # print(self.nickname_client_dict[message['NICKNAME']]) # print the nickanme of the requested bet
                    relevant_client = self.nickname_client_dict[message['NICKNAME']]
                    # print('RELEVANT CLIENT', relevant_client, type(relevant_client))
                    # print('CLIENT', client,type(client))
                    # print('CLIENT DICT' ,self.nickname_client_dict ,type(self.nickname_client_dict))
                    request_dict = {
                        'TYPE': 'CODE REQUEST',
                        'PROVIDER CLIENT': str(relevant_client),
                        'PROVIDER CLIENT NAME': f'{message["BET HOST NICKNAME"]}',
                        'ASKER CLIENT': str(client),
                        'ASKER CLIENT NAME': message['NICKNAME']
                    }
                    relevant_client.send(pickle.dumps(request_dict))
                elif message['TYPE'] == 'SENDING CODE':
                    print('\nSENDING OUT CODE')
                    dict_with_file_info = {
                        "TYPE": 'SENT FILES',
                        "CLIENT": message['CLIENT TEXT'],
                        "SERVER": message['SERVER TEXT'],
                        "PROVIDER NICKNAME": message['PROVIDER NICKNAME']
                    }
                    self.nickname_client_dict[message['ASKER NICKNAME']].send(pickle.dumps(dict_with_file_info))
                else:
                    print("SERVER DOESNT HAVE THIS TYPE OF MESSAGE")
                    print(message)
            except Exception as e:
                print(f'\nCALLING EXCEPTION: {e}')  # super helpful!
                # Removing And Closing Clients
                index = self.clients.index(client)
                self.clients.remove(client)
                client.close()
                nickname = self.nicknames[index]
                self.broadcast_to_clients(f'{nickname} left!'.encode('utf-8'))
                print(f'{nickname} left!'.encode('utf-8'))
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
            nameDict = {'TYPE': "NICK"
                        }
            client.send(pickle.dumps(nameDict))
            nickname = pickle.loads(client.recv(1024))
            # print(nickname) # ENTIRE NICKNAME DICT
            self.nickname_client_dict.update({nickname['VALUE']: client})
            self.nicknames.append(nickname['VALUE'])
            self.clients.append(client)

            # Print And Broadcast Nickname
            print("Nickname is {}".format(nickname['VALUE']))
            self.broadcast_to_clients("{} joined!".format(nickname['VALUE']).encode('utf-8'))
            self.broadcast_to_clients('Connected to server!'.encode('utf-8'))

            # Start Handling Thread For Client
            thread = threading.Thread(target=self.handle_client_msg, args=(client,))
            thread.start()

    '''------------------------------------------------------------------------------------------------'''

    '''CLIENT RELATED STUFF'''
    nickname = "Andre"  # CHANGE FOR SECOND NODE
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connecting To Server
    def connect_to_server(self):
        '''
        Instead of binding the data and listening, we are connecting to an existing server.
        :return:
        '''
        self.client.connect((CONSTANTS.LOCAL_HOST_IPV4, CONSTANTS.PORT))

    # Listening to Server and Sending Nickname
    def receive_from_server(self):
        '''
        It constantly tries to receive messages and to print them onto the screen.
        If the message is ‘NICK’ however, it doesn’t print it but it sends its nickname to the server.
        :return:
        '''
        while True:
            try:
                # Receive Message From Server
                # If 'NICK' Send Nickname
                message = self.client.recv(1024).decode('utf-8')
                if message == 'NICK':
                    self.client.send(self.nickname.encode('utf-8'))
                else:
                    print(message)
            except:
                # Close Connection When Error
                print("An error occured!")
                self.client.close()
                break

    # Sending Messages To Server
    def write_to_server(self):
        while True:
            message = f"{self.nickname}: {input('')}"  # weird way to get input, but kind of cool
            self.client.send(message.encode('utf-8'))

    # Starting Threads For Listening And Writing
    def run_threads(self):
        receive_thread = threading.Thread(target=self.receive_from_server)
        receive_thread.start()
        write_thread = threading.Thread(target=self.write_to_server)
        write_thread.start()


'''SERVER STUFF'''
node = Node()
node.starting_server()
node.listen()
