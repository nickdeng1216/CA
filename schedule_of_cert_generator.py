import os
import subprocess
import shutil
import mysql.connector as mariadb
import csv
import time

directory_root = os.getcwd() + os.sep + "cert" + os.sep
directory_request = directory_root + "request" + os.sep
directory_request_completed = directory_request + "completed" + os.sep
directory_request_processing = directory_request + "processing" + os.sep
directory_public_key = directory_root + "publickey" + os.sep
directory_issued = directory_root + "issued" + os.sep


def request_processing():
    requests = os.listdir(directory_request)
    for req in requests:
        file_info = os.path.splitext(req)

        if file_info[1] != "":
            shutil.move(directory_request + req, directory_request_processing + req)


def cer_generating():
    requests = os.listdir(directory_request_processing)
    for req in requests:
        if os.path.isdir(directory_request_processing + req):
            # generate cer
            src = directory_request_processing + req + os.sep + req + ".csr"
            gen = directory_issued + req + ".cer"
            subprocess.check_output(["openssl", "genrsa", "-out", gen, "-rand", src, "2048"])
            # move public key to ..
            src_pk = directory_request_processing + req + os.sep + req + ".pem"
            dst_pk = directory_public_key + req + ".pem"
            shutil.move(src_pk, dst_pk)
            # save to database
            file_mapping = directory_request_processing + req + os.sep + "mapping"
            csv_file = open(file_mapping, "r")
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                email = row[0]
                domain = row[1]
            csv_file.close()
            mydb = mariadb.connect(
                host="localhost",
                user="intercloudca",
                passwd="p@ssw0rd",
                database="CA"
            )
            cursor = mydb.cursor()
            cursor.execute("UPDATE CERT SET GENERATETIME = NOW() WHERE EMAIL=%s AND DOMAIN =%s",
                           (email, domain))
            mydb.commit()
            shutil.move(directory_request_processing + req, directory_request_completed + req)
            os.rename(directory_request_completed + req,
                      directory_request_completed + req + time.strftime(
                          '%Y%m%d%H%M%S', time.localtime(
                              int(round(time.time() * 1000)) / 1000)))


if __name__ == '__main__':
    request_processing()
    cer_generating()
