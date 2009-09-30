#!/usr/bin/env python

"""
@author Joel Cumberland

@contact zeme_6@hotmail.com

@version 0.1.6a

@status: Alpha, non-release

@copyright 2009

@license: GPL

"""

import sys, re, socket, MySQLdb, getpass, os
from optparse import OptionParser

_version = "0.1.6a"
domain_found = "Domain Not Found"
domain_foundadv = "Domain Found but could be Parked, a Dead Site or a Redirected Domain" 

class whois_server:
        
    """
    TODO // Have a way to produce a fall-back/Redundant server if the default one FAILS!!!
    A list of whois server to be used
    """
    whoismap = {        'com': 'whois.verisign-grs.com', \
                        'org': 'whois.pir.org', \
                        'net': 'whois.internic.net', \
                        'biz': 'whois.neulevel.biz', \
                        'edu': 'whois.educause.net', \
                        'info': 'whois.afilias.info' } # Will add more Whois Servers later.
    
    """Regular expression displayed by the output of the whois query performed"""
    exmap =     {       'com': 'No match for', \
                        'org': 'NOT FOUND', \
                        'net': 'No match for', \
                        'biz': 'Not found:', \
                        'edu': 'No Match', \
                        'info': 'NOT FOUND' }
    
    
    def who(self, tld):
        try:
            w = self.whoismap[tld]
            return w
        except Exception, e:
            print "Error finding %s please use a different tld to search for." % (e) 
            sys.exit()
    
    def ex(self, regex):
        x = self.exmap[regex]
        return x
    
    """Whois connection"""
    def connection(self, domain, who, tld):
        self.domain = domain
        self.tld = tld
        self.response = ''
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)        
        s.connect((who, 43))
        if tld == "com":
            domain = "="+domain
        s.send(domain + "\r\n")
        while True:
            d = s.recv(4096)
            self.response += d
            if d == '': break     
        s.close()
        
    def single(self):
        print self.response
    
    """Print/Display and write a basic whois search to file """
    def basic(self, file):
        if re.search(self.ex(self.tld), self.response):
            indent = command_display().format_this(self.domain, 30)
            print >>file,  self.domain + indent + domain_found 
            print self.domain + indent + domain_found
        
    """
    Print/Display and write a advanced whois search to file           
    Print domains that are not found on the whois server/s
    """ 
    def advance(self, file):
        indent = command_display().format_this(self.domain, 30)
        if re.search(self.ex(self.tld), self.response):
            print >>file, self.domain + indent + domain_found
            print self.domain + indent + domain_found   
        else:
            """
            Prints out the domains that are not found by the advanced domain search. These domains could be dead
            sites, not being used on port 80 or could be parked domains. These domains are registred on the whois server
            """
            print >>file, self.domain + indent + domain_foundadv
            print self.domain + indent + domain_foundadv
    
    """Create a wordlist from a mysql database"""
    def db_conn(self, user, passwd, host, port, database, table, column, file):
    
        if port == None: port = 3306
        if host == None: host = '127.0.0.1'
        
        try:
            db = MySQLdb.connect(host=host, port=port, user=user, passwd=passwd, db=database)
            query = db.cursor()
            query.execute("SELECT %s FROM %s" % (column, table) ) 
            result = query.fetchall()
            file = open(file, 'w')
            for record in result:
                    print >>file, record[0]
        except Exception, e: print e
            

class command_display:
    
    def __init__(self):
       """Used by the progress_bar() to keep track of the percentage being used"""
       self.already = 0
    
    """Used by the advanced search, so the user can be shown the program is still running :) """
    def progress_bar(self, number, total,  char):
       percentage = int(100 - round(number*100.0/total))
       if percentage > 0:
           xchar = char * (percentage-self.already)
           self.already = percentage 
           sys.stdout.write(xchar)
           sys.stdout.flush()                                      
                
                
    """Counts the number of lines in a file for the progress_bar()"""
    def count_lines(self, file):
        linecount = 0
        f = open(file)
        it = iter(f)
        try: 
            while it.next():
                linecount += 1
        except StopIteration:
                    pass
        return linecount
    
    """Indents the command line display to make it look pretty"""
    def format_this(self, word, indent):
        wcount = len(word)
        num = (indent - wcount)
        whitespace = " "
        format = whitespace * num
        return format
  
class whois_search:
    
    def __init__(self, domain, tld, wordlist, domainlist):
       
       self.domain = domain
       self.tld = tld
       self.wordlist = wordlist
       self.domainlist = domainlist

    def single_search(self):

        try:
            domainame,tld = self.domain.split(".") #NOTE // If using a tld like .com.au this will fail, need a better way to determine the tld
            w = whois_server()
            whois = w.who(tld)
            w.connection(self.domain, whois, tld)
            w.single()
        except Exception, e: print e
        return

    
    def basic_search(self):
        
        dlist = open(self.domainlist, 'w')
        fr = open(self.wordlist, 'r')
        for line in fr:
            line = line.rstrip() + "." + self.tld
            if not line: break
            try:
                w = whois_server()
                whois = w.who(self.tld)
                w.connection(line, whois, self.tld)
                w.basic(dlist)
            except Exception, e: print e
        dlist.close()
        fr.close()
        return        

    
    def advance_search(self):
     
        advfile = open(self.domainlist + ".adv", 'w')
        wordlist = open(self.wordlist, 'r')
        c = command_display()
        countline = c.count_lines(self.wordlist)
        total = countline
        
        print "Performing a Advanced Search..."
        for line in wordlist:
            c.progress_bar(countline, total, "*")
            line = line.rstrip() + "." + self.tld
            countline-=1
            if not line: break
            try: socket.getaddrinfo(line, socket.AF_INET, 0, socket.SOCK_STREAM)
            except Exception, e:
                while True:
                    print >>advfile,line
		    break 
        print "100%"
        advfile.close()
        wordlist.close()
        
        dlist = open(self.domainlist, 'w')
        advfile = open(self.domainlist + ".adv", 'r')
        for advline in advfile:
            advline = advline.rstrip()
            if not advline: break
            try:
                w = whois_server()
                whois = w.who(self.tld)
                w.connection(advline, whois, self.tld)
                w.advance(dlist)
            except Exception, e: print e
        advfile.close()
        dlist.close()
        return 

def main():
    usage = "usage: %prog [options] -i [file-to-read-from] -o [file-to-write-too]\n \n Examples:\n xwhois -t net -i /tmp/wordlist -o /tmp/domains\n xwhois -s sourceforge.net\n\nWordlists Found @ http://www.packetstormsecurity.org/Crackers/wordlists/"
    parser = OptionParser(usage=usage)

    try:
        parser.add_option("-t", "--tld", action="store", type="string", dest="tld",
                          help="--tld com/net/org/biz/edu/info - Search for these TLD's (Only use one of these tlds for each whois search")
        parser.add_option("-s", "--single", action="store_true", dest="single", help="Single domain search")
        parser.add_option("-a", "--advance", action="store_true", dest="advance", help="Advanced domain search")
        parser.add_option("-i", "--file-in", dest="filein",  type="string", help="File to read from")
        parser.add_option("-o", "--file-out", dest="fileout", type="string",  help="File to write to")
        parser.add_option("--sql", action="store_true", dest="sql", help="Connect to a MySQL database")
        parser.add_option("--host", dest="host", type="string", help="Host address for MySQL database connection (Default 127.0.0.1)")
        parser.add_option("--port", dest="port", type="int", help="Port to use for MySQL database connection (Default 3306)")
        parser.add_option("--user", dest="user", type="string", help="User to use for MySQL database connection")
        parser.add_option("-p", "--passwd", action='store_true', dest="passwd",  help="Prompt for a password to use with MySQL database connection")
        parser.add_option("--database", dest="database", type="string", help="Database to use for MySQL database query")
        parser.add_option("--table", dest="table", type="string", help="Table to use for MySQL database query")
        parser.add_option("--column", dest="column", type="string", help="Column to use for MySQL database query")

        (options, args) = parser.parse_args()
        
        if options.single == True:
            w = whois_search(sys.argv[2], None, None, None)
            w.single_search()
        else:
            if options.sql == True:
                options.filein = options.fileout + ".tmp"
                if options.passwd == True:
                    options.passwd = getpass.getpass()
                conn = whois_server()
                conn.db_conn(options.user, options.passwd, options.host, options.port, options.database, options.table, \
                                        options.column, options.filein)
            w = whois_search(None, options.tld, options.filein, options.fileout)
            if options.advance == True:
                w.advance_search()
            else:
                w.basic_search()
                
        try: os.remove(options.fileout + ".tmp")
        except Exception, e: pass
        
    except Exception, e: 
        print e
        print ""
        print parser.get_usage()
        sys.exit()
        


if __name__ == "__main__":
        main()
