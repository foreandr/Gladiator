import math
import shutil
import sys
import os
import hashlib

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


def log_message(message, type):
    from datetime import date, datetime
    now = datetime.now()
    date_time = now.strftime("%d/%m/%Y %H:%M:%S")

    if type == 'client':
        with open('LOGFILES/CLIENTlog.txt', 'w') as f:
            f.write(f"{date_time}: {message}")
    elif type == 'server':
        with open('LOGFILES/SERVERlog.txt', 'w') as f:
            f.write(f"{date_time}: {message}")


def print_green(text):
    print(COLORS.bcolors.OKGREEN + str(text) + COLORS.bcolors.ENDC)


def print_blue(text):
    print(COLORS.bcolors.OKBLUE + str(text) + COLORS.bcolors.ENDC)


def get_client_hash():
    '''
    NEEDS TO BE CHANGED TO SKIP NAME PORTION OF FILE, THAT WILL ALWAYS BE DIFFERENT
    :return:
    '''
    f = open("client.py", "r")
    client_in_text_form = f.read()  # GET TEXT
    client_encoded_binary = client_in_text_form.encode('utf-8')  # ENCODE TEXT
    hash_object = hashlib.md5(client_encoded_binary)  # HASH ENCODED TEXT
    hash_string = hash_object.digest()

    print_green(F'FINAL CLIENT HASH: {hash_string}')
    return hash_string


def get_client_txt():
    f = open("client.py", "r")
    client_in_text_form = f.read()  # GET TEXT
    return client_in_text_form


def get_server_hash():
    f = open("server.py", "r")
    server_in_text_form = (f.read())
    server_encoded_binary = server_in_text_form.encode('utf-8')  # ENCODE TEXT
    hash_object = hashlib.md5(server_encoded_binary)  # HASH ENCODED TEXT
    hash_string = hash_object.digest()

    print_green(F'FINAL SERVER HASH: {hash_string}')
    return hash_string

    # return client_in_text_form, server_in_text_form


def get_server_txt():
    f = open("client.py", "r")
    server_in_text_form = f.read()  # GET TEXT
    return server_in_text_form


client = get_client_txt()
server = get_server_txt()
name = 'Andre'


def put_files_in_folder(name, client, server):
    # print_green(client)
    # print_blue(server)
    ROOT_DIR = os.getcwd()  # SHOULD BE A UNIVERSAL
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



#put_files_in_folder(name, client, server)
