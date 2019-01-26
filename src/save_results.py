import MySQLdb
import datetime
import subprocess

path = '../images/test/drug_01.jpg'
s3_path = 's3://drug-detector-images/drug_01.jpg'
cmd = ['s3cmd', 'put', path, s3_path]
subprocess.Popen(cmd)


mydb = MySQLdb.connect(
  host="mysql-large.ccsroiuq1uw2.us-east-1.rds.amazonaws.com",
  port = 3306,
  user = "heming",
  passwd="xenia0427rds",
  db="mydb"
)

mycursor = mydb.cursor()

url = 'test_url'
date = datetime.datetime.today().strftime('%Y-%m-%d')
flag = True

sql = "INSERT INTO images (url, path, process_date, flag) VALUES (%s, %s, %s, %s)"
val = (url, path, date, flag)
mycursor.execute(sql, val)

mydb.commit()

print(mycursor.rowcount, "record inserted.")
