# coding:gbk
#
import socket,threading
import mcpack
import struct
import logging

logging.basicConfig(level=logging.DEBUG)
class McpackNsheadDriver(object):

    format = "HHI16sIII"
    magic_num = 0xfb709394

    def __init__(self, cfg={}):
        self.port = int(cfg.get("port",61111))
        self.ip = cfg.get("ip","127.0.0.1")
        self.name = cfg.get("name","base_driver")
        self.read_timeout = cfg.get("readtimeout",2)
        self.write_timeout = cfg.get("writetimeout",2)
        self.connect_timeout = cfg.get("connecttimeout",2)
        self.struct = struct.Struct(self.format)
        self.size = self.struct.size
        self.net = DriverNetLib(self)
        self.res = {"head":{},"body":{}}
        self.head = None
        self.body = None
        self.conntype = cfg.get("conntype",1)

    def setRequestHead(self,head):
        self.head = head

    def setRequestBody(self,body):
        self.body = body

    def decodeHead(self, data):
        #self.res["head"] = self.struct.unpack(data)
        (self.res["head"]["id"], self.res["head"]["version"], self.res["head"]["log_id"], self.res["head"]["provider"], self.res["head"]["magic_num"], self.res["head"]["reserved"], self.res["head"]["body_len"]) = self.struct.unpack(data)
        print "Response head: " + str(self.res["head"])
        #if self.head["magic_num"] != self.magic_num:
        #    raise UserWarning("magic_num check fail")

    def decodeBody(self, data):
        self.res["body"] = mcpack.loads(data)
        ssee = str(self.res["body"])
        if len(ssee) < 500:
            print "Response body: " + str(self.res["body"])
    
    def encode(self):
        send_data = mcpack.dumps_version(mcpack.mcpackv2, self.body, 1000000)
        self.head['body_len'] = len(send_data)
        send_data = struct.pack("HHI16sIII", self.head["id"], self.head["version"], self.head["log_id"], self.head["provider"], self.head["magic_num"], self.head["reserved"], self.head["body_len"]) + send_data
        return send_data


    def getBodySize(self):
        if self.res["head"] is not None:
            #import pdb
            #pdb.set_trace()
            #print type(self.res["head"])
            return int(self.res["head"]["body_len"])


    def doRequest(self):
        self.net.invite()



class DriverNetLib():

    def __init__(self, driver):
        self.driver = driver
        self.sockets = []
        self.socket_num = 0
        self.sockcond = threading.Condition()

    def __connect(self):
        try:
            sock = socket.create_connection((self.driver.ip, self.driver.port), self.driver.connect_timeout)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        except socket.error, why:
            logging.warning("driver connect error (%s), ip(%s), port(%d)", why, self.driver.ip , self.driver.port)
            return None
        return sock

    def __get_socket(self):
        self.sockcond.acquire()
        if len(self.sockets) == 0:
            sock = self.__connect()
            if sock: self.socket_num += 1
        else:
            sock = self.sockets.pop(0)
        self.sockcond.release()
        return sock

    def __put_socket(self, sock):
        self.sockcond.acquire()
        if not sock:
            self.socket_num -= 1
        elif self.driver.conntype:
            self.sockets.append(sock)
        else:
            sock.close()
            self.socket_num -= 1
        self.sockcond.notify()
        self.sockcond.release()

    def invite(self):
        #get socket
        #import pdb
        #pdb.set_trace()
        sock = self.__get_socket()
        if not sock:
            logging.warning("driver connect failed")
            return
        try:
            #send
            reqRawData = self.driver.encode()
            sent = 0
            sock.settimeout(self.driver.write_timeout)
            while sent < len(reqRawData):
                sent += sock.send(reqRawData[sent:])

            #recv
            sock.settimeout(self.driver.read_timeout)
            headSize = self.driver.size 
            recvRawHead = sock.recv(headSize)

            retryNum = 5
            while len(recvRawHead) < headSize and retryNum > 0:
                recvRawHead = recvRawHead + sock.recv(headSize - len(recvRawHead))
                retryNum -= retryNum

            if len(recvRawHead) < headSize:
                logging.warning("driver get head failed")
                sock.close()
                self.__put_socket(None)
                return

            self.driver.decodeHead(recvRawHead)
            bodySize = self.driver.getBodySize()
            if bodySize != 0:
                recvRawBody = sock.recv(bodySize)
                while len(recvRawBody) < bodySize:
                    recvRawBody = recvRawBody + sock.recv(bodySize - len(recvRawBody))
                self.driver.decodeBody(recvRawBody)

            self.__put_socket(sock)

        except socket.error,why:
            logging.warning("socket error (%s)", why)
            sock.close()
            self.__put_socket(None)

def GetDriver():
    return McpackNsheadDriver({"ip":"10.81.11.204","name":"test","port":"8300"})
if __name__=="__main__":
#    driverTest = McpackNsheadDriver({"ip":"10.81.60.25","name":"test","port":"8300"})
    driverTest = GetDriver()
    head= {'reserved': 0, 'log_id': 0, 'body_len': 0, 'version': 0, 'magic_num':4218459028, 'provider': 'app_nresult', 'id': 0}
#    body ={"userID":"xuxingjun", "cuid":"hitskyer","coor_sys":"baidu", "x":13120816.99, "y":4386448.54, "areaId":100010000,"keywords":"����","qrw_str_poi_id":"10023935094330872363"}
    print "�������� һ��poi"
    body ={"userID":"xuxingjun", 
           "cuid":"hitskyer",
           "coor_sys":"baidu", 
           "x":13120816.99, #10003822386528537279 ��xy
           "y":4386448.54,  
           "areaId":354,    #
           "keywords":"�������� һ��poi",
           "qrw_str_poi_id":"10003822386528537279"
    }
    driverTest.setRequestHead(head)
    driverTest.setRequestBody(body)
    driverTest.doRequest()
    
    print "�������� ����poi����"
    driverTest = GetDriver()
    head= {'reserved': 0, 'log_id': 0, 'body_len': 0, 'version': 0, 'magic_num':4218459028, 'provider': 'app_nresult', 'id': 0}
    body ={"userID":"xuxingjun", 
           "cuid":"hitskyer",
           "coor_sys":"baidu", 
           "x":13120816.99, #10003822386528537279 ��xy
           "y":4386448.54,  
           "areaId":354,    #
           "keywords":"�������� ����poi����",
           "qrw_str_poi_id":"10003822386528537279_7916147949828599617"
    }
    driverTest.setRequestHead(head)
    driverTest.setRequestBody(body)
    driverTest.doRequest()
    
    print "�������� ���poi����"
    driverTest = GetDriver()
    driverTest = McpackNsheadDriver({"ip":"10.81.11.204","name":"test","port":"8300"})
    head= {'reserved': 0, 'log_id': 0, 'body_len': 0, 'version': 0, 'magic_num':4218459028, 'provider': 'app_nresult', 'id': 0}
    body ={"userID":"xuxingjun", 
           "cuid":"hitskyer",
           "coor_sys":"baidu", 
           "x":13120816.99, #10003822386528537279 ��xy
           "y":4386448.54,  
           "areaId":354,    #
           "keywords":"�������� ���poi����",
           "qrw_str_poi_id":"10003822386528537279_7916147949828599617_1262860770325037055_1258741626105233407_1110128851060410059"
    }
    driverTest.setRequestHead(head)
    driverTest.setRequestBody(body)
    driverTest.doRequest()
    
    print "�������� ����poi����������Ǹ���poi"
    driverTest = GetDriver()
    head= {'reserved': 0, 'log_id': 0, 'body_len': 0, 'version': 0, 'magic_num':4218459028, 'provider': 'app_nresult', 'id': 0}
    body ={"userID":"xuxingjun", 
           "cuid":"hitskyer",
           "coor_sys":"baidu", 
           "x":13120816.99, #10003822386528537279 ��xy
           "y":4386448.54,  
           "areaId":354,    #
           "keywords":"�������� ����poi����������Ǹ���poi",
           "qrw_str_poi_id":"10003822386528537279_7916147949828599617_16303600450533180676_1258067019887017983_5530591450254066588"
    }
    driverTest.setRequestHead(head)
    driverTest.setRequestBody(body)
    driverTest.doRequest()
    
    print "�Ǹ������� һ���Ǹ���poi"
    driverTest = GetDriver()
    head= {'reserved': 0, 'log_id': 0, 'body_len': 0, 'version': 0, 'magic_num':4218459028, 'provider': 'app_nresult', 'id': 0}
    body ={"userID":"xuxingjun", 
           "cuid":"hitskyer",
           "coor_sys":"baidu", 
           "x":13120816.99, #10003822386528537279 ��xy
           "y":4386448.54,  
           "areaId":354,    #
           "keywords":"�Ǹ������� һ���Ǹ���poi",
           "qrw_str_poi_id":"5530591450254066588"
    }
    driverTest.setRequestHead(head)
    driverTest.setRequestBody(body)
    driverTest.doRequest()
    
    print "�Ǹ������� ����Ǹ���poi"
    driverTest = GetDriver()
    head= {'reserved': 0, 'log_id': 0, 'body_len': 0, 'version': 0, 'magic_num':4218459028, 'provider': 'app_nresult', 'id': 0}
    body ={"userID":"xuxingjun", 
           "cuid":"hitskyer",
           "coor_sys":"baidu", 
           "x":13120816.99, #10003822386528537279 ��xy
           "y":4386448.54,  
           "areaId":354,    #
           "keywords":"�Ǹ������� ����Ǹ���poi",
           "qrw_str_poi_id":"16303600450533180676_1258067019887017983_5530591450254066588"
    }
    driverTest.setRequestHead(head)
    driverTest.setRequestBody(body)
    driverTest.doRequest()
    
    print "�Ǹ������� xy ʧ��"
    driverTest = GetDriver()
    head= {'reserved': 0, 'log_id': 0, 'body_len': 0, 'version': 0, 'magic_num':4218459028, 'provider': 'app_nresult', 'id': 0}
    body ={"userID":"xuxingjun", 
           "cuid":"hitskyer",
           "coor_sys":"baidu", 
           "areaId":354,    #  
           "keywords":"�Ǹ������� xy ʧ��",
           "qrw_str_poi_id":"16303600450533180676_1258067019887017983_5530591450254066588"
    }
    driverTest.setRequestHead(head)
    driverTest.setRequestBody(body)
    driverTest.doRequest()
    exit(0)
