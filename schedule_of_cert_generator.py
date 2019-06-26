import os
import subprocess
import shutil
import mysql.connector as mariadb
import zipfile
import csv
import time

directory_root = os.getcwd() + os.sep + "cert" + os.sep
directory_request = directory_root + "request" + os.sep
directory_request_completed = directory_request + "completed" + os.sep
directory_request_processing = directory_request + "processing" + os.sep
directory_public_key = directory_root + "publickey" + os.sep
directory_issued = directory_root + "issued" + os.sep


# def unzip(filename):
#     src = directory_request + filename + ".zip"
#     dst = directory_request_completed + filename + "." + time.strftime('%Y%m%d%H%M%S', time.localtime(
#         int(round(time.time() * 1000)) / 1000)) + ".zip"
#     zip_file = zipfile.ZipFile(directory_request + filename + ".zip")
#     for name in zip_file.namelist():
#         zip_file.extract(name, directory_request_processing + filename)
#     zip_file.close()
#     shutil.move(src, dst)


def request_processing():
    requests = os.listdir(directory_request)
    for req in requests:
        file_info = os.path.splitext(req)
        if file_info[1] != "":
            shutil.copytree(directory_request + file_info[0],
                        directory_request_completed + file_info[0] + time.strftime('%Y%m%d%H%M%S', time.localtime(
                            int(round(time.time() * 1000)) / 1000)))
            shutil.move(directory_request + file_info[0], directory_request_processing + file_info[0])


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
                user="root",
                passwd=".",
                database="ca"
            )
            cursor = mydb.cursor()
            cursor.execute("UPDATE CERT SET GENERATETIME = NOW() WHERE EMAIL=%s AND DOMAIN =%s",
                           (email, domain))
            mydb.commit()
            if cursor.rowcount > 0:
                shutil.rmtree(directory_request_processing + req)


# def store_public_key:


if __name__ == '__main__':
    # request_processing()
    cer_generating()
    # store_public_key()
