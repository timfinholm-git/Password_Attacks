#!/usr/bin/python3
# Written and tested for Python 3.10.9

"""
Used for TryHackMe's Password Attacks Room.
Builds a sqlite database from which to choose passwords
"""

# handy for sqlite interactions
import concurrent.futures
import sqlite3


def db_build(db_location):
    location = db_location
    table_name = 'creds'
    conn = sqlite3.connect(location)
    c = conn.cursor()
    sql = 'CREATE TABLE IF NOT EXISTS {} (USERNAME TEXT, PASSWORD TEXT, TRIED INTEGER)'.format(table_name)
    c.execute(sql)
    conn.commit()
    # a list of users
    users = ['burgess']
    passwords = list()
    # dedupe_rps.txt is a file with the output of this command:
    # john - -wordlist = clinic.lst - -rules = Single - Extra - -stdout > rules_pws.txt
    # then cat rules_pws.txt | sort -u > dedupe_rps.txt
    # the clinic.lst file was built in a previous exercise in the room using cewl
    # put the lines from the file in to a list
    with open('dedupe_rps.txt', mode='r') as f:
        p = f.readlines()
        for each in p:
            pw = each.strip()
            passwords.append(pw)
    print(len(users))
    print(len(passwords))
    # take the usernames and passwords and put them in a db
    for each_user in users:
        for each_pw in passwords:
            c.execute("INSERT INTO creds (username, password, tried) VALUES (?,?,0)", (each_user, each_pw))
            conn.commit()


def main():
    db_location = 'http_creds.db'
    db_build(db_location)


if __name__ == '__main__':
    main()
