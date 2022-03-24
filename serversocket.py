# serversocket.py
import sqlite3
import json
import sys, os
import socket
from sqlite3 import *
import logging
import hashfunction

message =""
sql_create_table = """CREATE TABLE IF NOT EXISTS Nonces(nonce text PRIMARY KEY)"""
sql_add_nonce = """INSERT INTO Nonces(nonce) VALUES(?)"""
sql_search_nonce = """SELECT nonce FROM Nonces WHERE nonce=?"""
currentDb = "database"
connection = ""
# HOST = "127.0.0.1"  # Localhost
# HOST = "25.35.53.183" # Gabriele - Hamachi IPv4
PORT = 3030  # Standard PORT
Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="logfile.log",
                    filemode="a",
                    format=Log_Format,
                    level=logging.INFO)
logger = logging.getLogger()



def connectToDb():
    global connection
    connection = None
    if os.path.isfile(currentDb):
        logger.info("Found a database in root dir. Trying to estabilish a connection..")
        print("[SERVER]: Database found!")
        print("[SERVER]: Establishing connection...")
        try:
            connection = sqlite3.connect(currentDb, check_same_thread=False)
            print("[SERVER]: Connection to database established successfully!")
            logger.info("Established connection to main database")
            return True
        except Error as e:
            print("[SERVER]: Error! The following occurred: " + str(e))
            logger.error("Can't connect to database. Error: " + str(e))
            return False
    else:
        logger.warning("No database found in program root dir. An empty database will be created.")
        logger.warning("This may pose a security threat for incoming messages!")
        print("[SERVER]: Warning! Database not found!")
        print("[SERVER]: All previous nonce-s cannot be recovered!")
        print("[SERVER]: This may pose a security threat!")
        print("[SERVER]: A new database will be created with 0 entries.")
        print("[SERVER]: Establishing connection...")
        try:
            connection = sqlite3.connect(currentDb, check_same_thread=False)
            connection.execute(sql_create_table)
            connection.commit()
            print("[SERVER]: Connection to database established successfully!")
            logger.info("Established connection to main database")
            return True
        except Error as e:
            print("[SERVER]: Error! The following occurred: " + str(e))
            logger.error("Can't connect to database. Error: " + str(e))
            return False

def nonceCheck(nonce):
    global connection
    curs = connection.cursor()
    curs.execute(sql_search_nonce, (nonce,))
    rows = curs.fetchall()
    if not bool(rows):
        try:
            curs.execute(sql_add_nonce, (nonce,))
            connection.commit()
            logger.info("Registered new nonce into database.")
        except Error as e:
            print("[SERVER]: Error! The following occurred: " + str(e))
            logger.error("Can't register nonce to database. Error: " + str(e))
        return True
    else:
        return False


def main():
    global message
    logger.info("PROGRAM STARTED")
    print("[SERVER]: Starting program...")
    connectToDb()
    print("[SERVER]: STARTING SERVER - Server IP: "+str(HOST)+" - Server Port: "+str(PORT))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"[SERVER]: Established connection with address: {addr}")
            logger.info("Estabilished a connection with client on address: "+str(addr))
            data = conn.recv(1024)
            message = json.loads(data)
            logger.info("Received data, processing message")
            print("[SERVER]: Message received. Processing message...")
            logger.info("Requested the transfer of: "+message['amount']+"€ from SenderAccount: "+message['sender']+"+to" 
                  "ReceiverAccount: "+message['receiver'])
            print(f"[SERVER]: Requested the transfer of: {message['amount']}€ from SenderAccount: {message['sender']} to "
                  f"ReceiverAccount: {message['receiver']}")
            print("[SERVER]: Checking message authenticity...")
            logger.info("Checking the autheticity of the message")
            plaintextConcat = message['sender']+message['receiver']+message['amount']+message['nonce']
            if hashfunction.hash_msg(plaintextConcat) == message['hmac']:
                if nonceCheck(message['nonce']):
                    print("[SERVER]: Message authenticity successfully verified. Authorizing operation... ")
                    logger.info("Message authenticity verified. The operation will be authorized")
                    conn.sendall(b"The requested operation has been authorized and will be executed shortly")
                    s.close()
                else:
                    print("[SERVER]: WARNING! Failed nonce check. Operation aborted")
                    logger.error("Failed nonce check. Operation will be aborted")
                    conn.sendall(b"Operation failed integrity and authenticity checks. The process will be aborted and discarded")
                    s.close()
            else:
                print("[SERVER]: WARNING! Failed hash check. Operation aborted")
                logger.error("Failed hash check. Operation will be aborted")
                conn.sendall(b"Operation failed integrity and authenticity checks. The process will be aborted and discarded")
                s.close()

if __name__ == "__main__":
    main()
