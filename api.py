from flask import Flask
from flask import request
import os
import mysql.connector as mariadb
import shutil

app = Flask(__name__)

directory_root = os.getcwd() + os.sep + "cert" + os.sep
directory_request = directory_root + "request" + os.sep
directory_public_key = directory_root + "publickey" + os.sep
directory_issued = directory_root + "issued" + os.sep
directory_issued_completed = directory_issued + "completed" + os.sep


@app.route('/cert', methods=['POST'])
def request_cert():
    # print(request.is_json)
    content = request.get_json()

    domain = content['domain']
    email = content['email']
    src = directory_issued + domain + ".cer"
    dst = directory_issued_completed + domain + ".cer"
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

    request_for = content['requestfor']
    request_from = content['requestfrom']
    email = content['email']
    src = directory_public_key + request_for + ".pem"

    return_value = bytes('No public key found.', 'utf-8')
    public_key = get_file(src)
    if public_key is not None:
        return_value = public_key
        mydb = mariadb.connect(
            host="localhost",
            user="root",
            passwd=".",
            database="ca"
        )
        cursor = mydb.cursor()
        cursor.execute("INSERT INTO FRIEND (REQUESTFOR, REQUESTFROM, EMAIL) VALUES(%s, %s,%s) ",
                       (request_for, request_from, email))
        mydb.commit()

    return return_value


@app.route('/upload', methods=['POST'])
def upload():
    content = request.get_json()
    domain = content['domain']
    csr = content['csr']
    mapping = content['mapping']
    public_key = content['publickey']
    save_certificate_request(csr, mapping, public_key, domain)
    # save_file(directory_public_key + domain + ".pem", public_key)

    return "ok"


def save_file(path, content):
    if os.path.isfile(path):
        return False
    with open(path, 'w') as file:
        file.write(content)
    return True


def save_certificate_request(cer, mapping, public_key, domain):
    path = directory_request + domain + os.sep
    if os.path.exists(path):
        return False
    os.mkdir(path)
    save_file(path + domain + ".csr", cer)
    save_file(path + "mapping", mapping)
    save_file(path + domain + ".pem", public_key)
    return True


if __name__ == '__main__':
    from werkzeug.contrib.fixers import ProxyFix

    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.run()
