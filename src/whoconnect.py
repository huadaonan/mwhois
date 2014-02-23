#!/usr/bin/env python 

import socket
import time
import logging

from exception import WhoException


class WhoisServerConnection():
    
    def __init__(self, whoinfo):
        
        self.logger = logging.getLogger(__name__)

        self.logger.debug('constructor: __init__()')
        
        self.whoinfo = whoinfo
        self.sleep = 0
        self.no_of_attempts = 0
        
    def connection(self):
        
        self.logger.debug('called connection()')
        
        if self.whoinfo.whoisserver is not None or self.whoinfo.whoiserver is not '':
            
            self.logger.debug('sleep for %f', self.sleep)
            time.sleep(self.sleep)
            
            try:
                self.logger.debug('socket: creating socket: fingers crossed ')
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)        
                self.logger.debug('socket: %s', sock)
            
            except socket.error as e:
                self.logger.error('socket: open socket error %s', e)
                sock.close()
                
            try:
                self.logger.debug('connecting to server: %s', self.whoinfo.whoisserver)
                sock.connect((self.whoinfo.whoisserver, 43))
            
            except socket.error as e:
                self.logger.error('socket: connect socket error %s', e, exc_info=True)
                sock.close()
                
            try:
                self.logger.debug('socket: now sending data to server (data:%s)', self.whoinfo.domain)
                sock.send(self.whoinfo.domain + '\r\n')
            
            except socket.error as e:
                self.logger.error('socket: send error %s', e, exc_info=True)
                sock.close()
                    
            try:
                
                self.logger.debug('socket: lets clear self.response so we get fresh data')
                self.whoinfo.response = ''
                
                while True:
                    data = sock.recv(4096)
                    self.logger.debug('socket: receiving data')
                    self.whoinfo.response += data
                    if data == '':
                        self.logger.debug('socket: end of data sequence')
                        break     
                
                self.logger.debug('socket: closing socket object %s', sock)
                sock.close()
            
            except WhoException as e:
                    self.logger.error(e, exc_info=True)
                    sock.close()
        else:
                self.logger.debug('no whois server is set :( ')

        return