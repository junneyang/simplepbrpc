#!/usr/bin/env python
# coding=utf-8

import errno
import os
import sys
import fileinput
import string
import logging
import traceback
import hashlib
import time
import re
from datetime import date, timedelta
import datetime
from subprocess import call
import redis
from datasource import DataSource   


class Items(DataSource):
    def __init__(self, redisClientManager, config, act):
        DataSource.__init__(self, config, act)
        self.redisClientManager = redisClientManager
        self.downloadedDir = ""
        self.key = ""
        if os.path.exists(self.dir + "/downloaded.txt"):
            with open(self.dir + "/downloaded.txt", 'r') as content_file:
                    self.downloadedDir = content_file.read()
        
    def saveDownloadedDir(self, dir):
        self.downloadedDir = dir
        with open(self.dir + "/downloaded.txt", "w") as text_file:
            text_file.write(dir)

    def isOkFloatString(self, value):
        for c in value:
            if c == '.':
                continue
            if ord(c) <48 or ord(c) > 57:
                return False
        return True        
        
    def download(self):
        try:
            cmd = "rm -rf " + self.dir + "/*"
            call(cmd, shell=True)
            cmd = "hadoop fs -get " + self.download_url + " " + self.dir
            logging.info("[" + self.name + "]" + "Downloading file:" + self.download_url)
            retcode = call(cmd, shell=True)
            if retcode != 0:
                logging.error("Child was terminated by signal:" + str(retcode) + " for cmd:" + cmd)
                return False
            else:
                self.saveDownloadedDir(self.datedir)
                return True
        except:
            tb = traceback.format_exc()
            logging.error("Some error occured:\n" + tb)
            return False
    def __parseImport(self, filename, name):
        file = open(filename, 'r')
        count = 0
        ff = name.split('_')
        prefix= self.config["prefix"] + ":"
        while 1:
            lines = file.readlines(10000)
            if not lines:
                break
            for line in lines:
                line = line.strip()
                if count % 100000 == 0 and count != 0:
                    logging.info("[" + self.name + "]" + str(count) + " lines parsed and imported to redis for file:" + filename)
                count = count + 1
                #ss = re.split(r'\t+', line.rstrip('\t'))
                line = line.rstrip("\n")
                ss = line.split("\t")
                if len(ss) != 11:
                    print "fxxk you man!"
                    exit(1)
                #poi_id = ss[0]
                #�쳣�ַ���
                poi_id = ss[0]
                if not all(ord(c) < 128 for c in poi_id):
                    logging.error("[" + self.name + "]Discard invalid line:" + line + "\n")
                    continue
                if len(poi_id) > 50:
                    logging.error("filename:" + filename + ", line:" + str(count) +", cuid too long!")
                    continue
                key = prefix + poi_id
                value = ""
                i = 1
                tag = 0
                while i < len(ss):
#                     if not self.isOkFloatString(ss[i]):
#                         tag = 1
#                         break
                    if i == 1:
                        value = ss[i]
                    else:
                        value = value + ":" + ss[i]
                    i = i+1
#                 if tag == 1:
#                     logging.error("filename:" + filename + ", line:" + str(count) +", not all nums are right")
#                     continue    
                clients = self.redisClientManager.getClientsByShardKey("items", poi_id)
                self.cnt+=1
                if self.key != key:
                    for client in clients:
                        client.pipeline.delete(key)
                    self.key = key
                for client in clients:
                    client.pipeline.sadd(key, value)
                    client.IncrPipeCount()
                    if client.pipecount >= 100:
                        client.commit()
        file.close()
        return True
    def parseImport(self):
        fs = os.listdir(self.dir)
        for file in fs:
            if file == "status.txt" or file == "downloaded.txt":
                continue
            while True:
                try:
                    logging.info("[" + self.name + "]Start parsing import data from file:" + file)
                    self.__parseImport(self.dir + "/" + file, file)
                    self.redisClientManager.commitClients("items")
                    break
                except:
                    tb = traceback.format_exc()
                    logging.error("Some error occured to parsing import file:" + file + "\n" + tb)
                    time.sleep(60)
        return True
    
    def __delete(self, filename):
        fi = open(filename, 'r')
        count = 0
        prefix= self.config["prefix"] + ":"
        while 1:
            lines = fi.readlines(10000)
            if not lines:
                break
            for line in lines:
                line = line.strip()
                if count % 100000 == 0 and count != 0:
                    logging.info("[" + self.name + "]" + str(count) + " lines parsed and deleted from redis for file:" + filename)
                count = count + 1
                ss = re.split(r'\t+', line.rstrip('\t'))

                #poi_id = ss[0]
                poi_id = ss[0]
                if not all(ord(c) < 128 for c in poi_id):
                    logging.error("[" + self.name + "]Discard invalid line:" + line + "\n")
                    continue
                if len(poi_id) > 50:
                    logging.error("filename:" + filename + ", line:" + str(count) +", cuid too long!")
                    continue
                key = prefix + poi_id
     
                clients = self.redisClientManager.getClientsByShardKey("items", poi_id)
                
                for client in clients:
                    client.pipeline.delete(key)
                    client.IncrPipeCount()
                    if client.pipecount >= 100:
                        client.commit()
                
        fi.close()
        return True
        
    def delete(self):
        fs = os.listdir(self.dir)
        for fi in fs:
            if fi == "status.txt" or fi == "downloaded.txt":
                continue
            while True:
                try:
                    logging.info("[" + self.name + "]Start parsing delete data from file:" + fi)
                    self.__delete(self.dir + "/" + fi)
                    self.redisClientManager.commitClients("items")
                    break
                except:
                    tb = traceback.format_exc()
                    logging.error("Some error occured to parsing delete file:" + fi + "\n" + tb)
                    time.sleep(60)
        return True
    
    def checkAvailable(self):
        try:
            if self.action == "import":
                yesterday = date.today() - timedelta(1)
                self.datedir = yesterday.strftime('%Y%m%d')
                #self.datedir = "."
                if self.datedir == self.downloadedDir:
                    return 0
            elif self.action == "delete":
                self.datedir = self.del_date 
                if self.datedir == self.downloadedDir:
                    return 2
            
            self.download_url = self.config["url"].replace("${date}", self.datedir)
            
            donefile = self.config["checkfile"].replace("${date}", self.datedir)
            cmd = "hadoop fs -test -e " + donefile
            retcode = call(cmd, shell=True)
            if retcode == 0:
                return 1
            return 0
        except:
            tb = traceback.format_exc()
            logging.error("Some error occured:\n" + tb)
            return 0 
        return 0
        
