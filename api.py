#!flask/bin/python
from flask import Flask
from flask import request
import os
import mysql.connector as mariadb
import shutil

app = Flask(__name__)

directory_root = os.getcwd() + os.sep + "cert" + os.sep


@app.route('/cert', methods=['POST'])
def request_cert():
    # print(request.is_json)
    content = request.get_json()

    domain = content['domain']
    email = content['email']
    directory_issued = directory_root + "issued" + os.sep
    src = directory_issued + domain + ".cer"
    dst = directory_issued + "completed" + os.sep + domain + ".cer"
    return_value = bytes('No certificate generated.', 'utf-8')
    cert = get_file(src)
    if cert is not None:
        return_value = cert
        mydb = mariadb.connect(
            host="localhost",
            user="root",
            passwd=".",
            database="ca"
        )
        cursor = mydb.cursor()
        cursor.execute("UPDATE CERT SET DOWNLOADTIME = NOW() WHERE EMAIL=%s AND DOMAIN =%s",
                       (email, domain))
        mydb.commit()
        shutil.move(src, dst)

    return return_value


def get_file(src):
    if not os.path.isfile(src):
        return None
    with open(src, 'r') as content_file:
        return content_file.read()


@app.route('/friend', methods=['POST'])
def request_friend():
    content = request.get_json()

    requestfor = content['requestfor']
    requestfrom = content['requestfrom']
    email = content['email']
    src = directory_root + "publickey" + os.sep + requestfor + ".pem"

    return_value = bytes('No public key found.', 'utf-8')
    publickey = get_file(src)
    if publickey is not None:
        return_value = publickey
        mydb = mariadb.connect(
            host="localhost",
            user="root",
            passwd=".",
            database="ca"
        )
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO FRIEND (REQUESTFOR, REQUESTFROM, EMAIL) VALUES(%s, %s,%s) ",
                       (requestfor, requestfrom, email))
        mydb.commit()

    return return_value


app.run(host='0.0.0.0', port=5000)
