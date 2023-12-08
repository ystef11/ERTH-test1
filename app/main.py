#!/usr/bin/python3
# coding=utf8
import requests
import mysql.connector
import os
import time
import json

print(os.environ['MYSQL_HOST'])


while True:
    try:
        con=mysql.connector.connect(
                host=os.environ['MYSQL_HOST'],
                user=os.environ['MYSQL_USER'],
                password=os.environ['MYSQL_PASSWORD'],
        )
        cur=con.cursor()
        con.autocommit = False
        break
    except:
       time.sleep(2)

cur.execute('insert into sbp.queue_node values ()')
cur.execute('select last_insert_id()')
for row in cur.fetchall():
    print('row ',row)
    node_id=row[0]
print('node %s'%node_id)
con.commit()

while True:
    cur.execute("update sbp.payments set queue=%s where status <> 'ACWP' and queue is null order by ts desc LIMIT %s"%(node_id,os.environ['MYSQL_BATCH']))
    con.commit()
    cur.execute("select qrcId FROM sbp.payments where status <> 'ACWP' and queue=%s"%(node_id))
    result = cur.fetchall()
    if len(result)>0:
        data={"qrcIds": []}
        for row in result:
            data["qrcIds"].append(row[0])
        print(data)
        r = requests.put('http://%s:1080/payment/v2/qrc-status'%os.environ['SBP_HOST'], json=data)
        for i in r.json()['data']:
            if i['status']!='ERROR':
                print("update sbp.payments set status='%s', trxId='%s', kzo='%s',queue=null where qrcId='%s'"%(i['status'], i['trxId'], i['kzo'], i['qrcId']))
                cur.execute("update sbp.payments set status='%s', trxId='%s', kzo='%s',queue=null where qrcId='%s'"%(i['status'], i['trxId'], i['kzo'], i['qrcId']))
            else:
                cur.execute("update sbp.payments set queue=null where qrcId='%s'"%i['qrcId'])
        con.commit()
    time.sleep(2)
