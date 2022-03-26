import math
import shutil
import sys
import os
import hashlib
import requests
from bs4 import BeautifulSoup


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_nickname():
    nickname = 'Andreff'
    # nickname = input()
    return nickname




def get_fight_result(better2_choice2, better1_choice):
    '''Kind of complicated and unintelligibel way to get
    The result of a particular bet
    '''
    URL = "http://ufcstats.com/statistics/events/completed"
    page = requests.get(URL)
    event_page = None
    soup = BeautifulSoup(page.content, "html.parser")

    for link in soup.find_all('a'):
        wanted_names = [better1_choice, better2_choice2]
        casted_string_link = str(link)
        if wanted_names[0] in casted_string_link or wanted_names[
            1] in casted_string_link:
            print(bcolors.HEADER, link, bcolors.ENDC)
            event_link = str(link.get('href'))
            event_page = requests.get(event_link)
            break
        else:
            continue

    event_soup = BeautifulSoup(event_page.content, "html.parser")
    fight_link_list = []
    for link in event_soup.find_all('a'):
        casted_link = str(link)
        if 'fight-details' in casted_link:
            fight_link_list.append(link.get('href'))

    count = 0
    list_of_results = []
    for i in fight_link_list:
        actual_fight_page = requests.get(i)
        fight_page_soup = BeautifulSoup(actual_fight_page.content, "html.parser")
        results = fight_page_soup.find_all('div', {'class': 'b-fight-details__person'})
        for i in results:
            list_of_results.append([i])
        count += 1
        if count == 1:
            break

    final_dict = {}
    for i in list_of_results:
        almost_name = i[0].find_all('a')
        casted_almost_name = str(almost_name)
        splitted_list1 = casted_almost_name.split('">')
        splitted_list2 = splitted_list1[1].split('</a>')
        name = splitted_list2[0].strip()

        almost_conclusion = i[0].find_all('i')
        casted_almost_conclusion = str(almost_conclusion)
        conc_splitted_list1 = casted_almost_conclusion.split('">')
        conc_splitted_list2 = conc_splitted_list1[1].split('</i>')
        conclusion = conc_splitted_list2[0].strip()

        if conclusion == 'W':
            conclusion = 'WINNER'
        elif conclusion == 'L':
            conclusion = 'LOSER'

        final_dict[conclusion] = name

    return final_dict
# print(get_fight_result('Makhachev', 'Green')) # EXTRA TEST

def log_message(message, type):
    from datetime import datetime
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")

    if type == 'client':
        with open('LOGFILES/CLIENTlog.txt', 'w') as f:
            f.write(f"{date_time}: {message}")
    elif type == 'server':
        with open('LOGFILES/SERVERlog.txt', 'w') as f:
            f.write(f"{date_time}: {message}")


def print_green(text):
    print(bcolors.OKGREEN + str(text) + bcolors.ENDC)


def print_blue(text):
    print(bcolors.OKBLUE + str(text) + bcolors.ENDC)


def get_client_hash():
    f = open("client.py", "r")
    client_in_text_form = f.read()
    client_encoded_binary = client_in_text_form.encode('utf-8')
    hash_object = hashlib.md5(client_encoded_binary)
    hash_string = hash_object.digest()

    print_green(F'FINAL CLIENT HASH: {hash_string}')
    return hash_string


def get_client_txt():
    f = open("client.py", "r")
    client_in_text_form = f.read()
    return client_in_text_form


def get_server_hash():
    f = open("server.py", "r")
    server_in_text_form = (f.read())
    server_encoded_binary = server_in_text_form.encode('utf-8')
    hash_object = hashlib.md5(server_encoded_binary)
    hash_string = hash_object.digest()

    print_green(F'FINAL SERVER HASH: {hash_string}')
    return hash_string


def get_server_txt():
    f = open("client.py", "r")
    server_in_text_form = f.read()
    return server_in_text_form


def put_files_in_folder(name, client, server):
    ROOT_DIR = os.getcwd()
    path = 'OPPOFILES'
    unique_path_name = name
    saveLocation = os.path.join(ROOT_DIR, path, unique_path_name)

    if os.path.exists(saveLocation):
        shutil.rmtree(saveLocation)
    os.makedirs(saveLocation)

    os.chdir(saveLocation)
    with open('client.py', 'w') as f:
        f.write(f'{client}')

    with open('server.py', 'w') as f:
        f.write(f'{server}')


def get_log_percent(money):
    return math.log10(money)

def divide_winnings(message):
    print('OG MESSAGE: ', message)
    initial_bet_winnings = message['AMOUNT']
    initial_bet = message['BET DETAILS']
    gladiator_percent = initial_bet['Gladiator Percent']
    my_cut_dict = 'Host Percent' # HEHEHEH XD
    my_cut = my_cut_dict

    # print('INITIAL BET', initial_bet)
    print('GLADIATOR CUT ', gladiator_percent)




demo_dict = {'TYPE': 'WINNINGS', 'AMOUNT': 11.0, 'BET DETAILS': {'TYPE': 'BET', 'NICKNAME': 'Andre', 'KEY': 1, 'Bet Value': 10, 'Bet Type': 'Victory', 'Bet Ratio': 1.1, 'Bet Participant1': 'Walker', 'Bet Participant2': 'Hill', 'Bet Focus': 'Hill'
, 'Potential Winnings': 11.0, 'Opponent Bet Value': 11.0, 'Opponent Potential Winnings': 10, 'Gladiator Percent': 5, 'Host Percent': {'PROPOSER VICTORY': 1.0, 'OPPONENT VICTORY': 1.04}, 'CLIENT HASH': b'\xd4Id\x15;\xdf\xa4`\x16\xaa\x9a\x964\xf1,X', 'SERVER HASH': b'($xh+\x1a\xf1<0nn\xf6Q\xe7\xc8%'}}

divide_winnings(demo_dict)