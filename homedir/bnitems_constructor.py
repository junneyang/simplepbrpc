#!/usr/bin/env python
#-*- coding: utf-8 -*-

import os
import sys
import re
import hashlib
import redis
import json
import struct
import traceback
import logging
import time

sys.path.append('..')
import UppsTestFrame.importer.RedisClients as RedisClients

class ItemsConstructor(object):
    def __init__(self, config, file):
        self.config = config
        self.file = file
        self.conn_dic = RedisClients.UppsRedisClientManager(self.config)
        self.key = ""

    def run(self):
        try:
            file = open(self.file, 'r')
            while True:
                lines = file.readlines(10000)
                if not lines:
                    break
                for line in lines:
                    line = line.strip()
                    #ss = re.split(r'\t+', line.rstrip('\t'))
                    if line.startswith("#"):
                        continue
                    ss = line.split()
                    prefix = ss[0]
                    poi_id = ss[1].lower()
                    if not all(ord(c) < 128 for c in poi_id):
                        print("[" + self.name + "]Discard invalid line:" + line + "\n")
                        continue

                    key = prefix + ":" + poi_id
                    value = ""
                    i = 2
                    while i < len(ss):
                        if i == 2:
                            value = ss[i]
                        else:
                            value = value + ":" + ss[i]
                        i = i+1

                    clients = self.conn_dic.getClientsByShardKey("items", poi_id)

                    if self.key != key:
                        for client in clients:
                            client.delete(key)
                        self.key = key
                    for client in clients:
                        client.sadd(key, value)
            file.close()
        except:
            tb = traceback.format_exc()
            print(tb)


if __name__ == '__main__':
    print("start")
    start = time.time()
    try:
        conf = json.load(open("./config.json", "r"))
        constructor = ItemsConstructor(conf, "./TestData/bnitems.data")
        constructor.run()
    except :
        tb = traceback.format_exc()
        print("Some error occured:\n" + tb)
        #sys.exit()

    end = time.time()
    print("Items check Cost " + str(int(end-start)) +"s.")
    print("end")

