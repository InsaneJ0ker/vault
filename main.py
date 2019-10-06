import os
import Generator
import mysql.connector
import getpass
import json



action_prompt = """ACTIONS:
C - Create a password
R - Retrieve a password
E - Exit the Program
D - Delete an entry (USE WITH CAUTION!)
Q - Query data [Usage: Q username_email, Q website...]\n"""

def mkeysetup() -> str:
    mkeyprompt = "Please choose a non-empty masterkey:\n"
    mkey2prompt = "Please re-enter your masterkey:\n"
    mkey = getpass.getpass(prompt = mkeyprompt)
    while not mkey:
        print("Your masterkey was empty!")
        mkey = getpass.getpass(prompt = mkeyprompt)

    mkey2 = getpass.getpass(prompt = mkey2prompt)
    while mkey2 != mkey:
        print("Your masterkeys did not match!")
        mkey2 = getpass.getpass(prompt = mkey2prompt)
    print("Setup complete, enter you masterkey 1 more time to begin!")
    return mkey


def ascii():
    print("WELCOME TO ")
    print("__      __         _ _    ")
    print("\ \    / /        | | |   ")
    print(" \ \  / /_ _ _   _| | |_  ")
    print("  \ \/ / _` | | | | | __| ")
    print("   \  / (_| | |_| | | |_  ")
    print("    \/ \__,_|\__,_|_|\__| Python and MySQL Powered Password Manager v1.1")

def creatpswd(mycursor):
    username = input('Please enter your username/email:\n')
    usage = input('Please enter the website/usage:\n')
    mycursor.execute("SELECT * FROM passwords WHERE username_email = %s AND website = %s", (username, usage))
    count = mycursor.rowcount
    if count == 0:
        length = int(input("Length of password:\n"))
        password = Generator.gen(length)
        mycursor.execute("INSERT INTO passwords (website, username_email, password) VALUES (%s, %s, %s)", (usage, username, password))
    else:
        print("username+usage already in database")

def retreivepswd(mycursor):
    usage = input('What is the usage/website?\n')
    username = input('What is the username/email?\n')
    mycursor.execute("SELECT * FROM passwords WHERE username_email = %s AND website = %s", (username, usage))
    count = mycursor.rowcount
    if count == 1:
        mycursor.execute("SELECT password FROM passwords WHERE website = %s AND \
                             username_email = %s", (usage, username))
        password = mycursor.fetchone()
        password = password[0]
        print('Your password: ' + password)
    else:
        print('There is no such website/username combination in the database\n')

def deletepswd(mycursor):
    usage = input('What is the usage/website password would you like to delete?\n')
    username = input('What is the username/email?\n')
    mycursor.execute("SELECT * FROM passwords WHERE username_email = %s AND website = %s", (username, usage))
    count = mycursor.rowcount
    if count == 1:
        answer = input('Are you sure you want to delete this? Y/N\n')
        if answer.lower()!='y' and answer.lower()!='n':
            answer = input('Please enter Y or N\n')
        if answer.lower()=='y':
            mycursor.execute("DELETE FROM passwords WHERE website=%s AND username_email=%s", (usage, username))
    else:
        print('There is no such website/username combination in the database\n')

def main():

    master = False

    ascii()

    with open('config.json') as json_file:
        data = json.load(json_file)
    print()

    db = mysql.connector.connect(
          host=data["host"],
          user=data["user"],
          passwd=data["passwd"]
        )


    mycursor = db.cursor(buffered=True);
    mycursor.execute("SHOW DATABASES")

    for x in mycursor:
        if 'main' == x[0]:
            mycursor.execute("USE main")
            master = True;
            break;
    else:
        mycursor.execute("CREATE DATABASE main")
        mycursor.execute("USE main")
        mycursor.execute("CREATE TABLE passwords (website VARCHAR(255), \
        username_email VARCHAR(255), password VARCHAR(255), PRIMARY KEY(website, username_email))")

        mkey = mkeysetup()

        mycursor.execute("INSERT INTO passwords VALUES(%s, %s, %s)", ("SYSTEM", "MASTER", mkey))
        db.commit()
        master = True;


    key = getpass.getpass(prompt = "Please enter your masterkey:\n")

    mycursor.execute("SELECT password FROM passwords WHERE website = %s AND \
                               username_email = %s", ("SYSTEM", "MASTER"))
    myresult = mycursor.fetchone()

    while key != myresult[0]:
        key = getpass.getpass(prompt = "Your masterkey was wrong! Please re-enter your master key:\n")

    action = ''

    if master:
        while action == '':
            action = input(action_prompt)

            if action.lower() == 'e':
                master = False;
                break;

            if action.lower() == 'c':
                creatpswd(mycursor)
                action = ''

            if action.lower() == 'r':
                retreivepswd(mycursor)
                action = ''

            if action.lower() == 'd':
                deletepswd(mycursor)
                action = ''
        db.commit()

    db.commit()
    mycursor.close()

if __name__ == "__main__":
    main()
