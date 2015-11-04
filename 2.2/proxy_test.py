#!/usr/bin/env python2
# Communication Systems Lab
# Assignment 2
# Task 2.2
# Author: Tong, Michael
# ##############################
# Description:
#

import urllib2
import gzip
import pprint

if __name__ == '__main__':
    # Proxy server setting
    proxy_support = urllib2.ProxyHandler({"http":"http://cslectures.tongsucn.com:8123"})
    opener = urllib2.build_opener(proxy_support)
    urllib2.install_opener(opener)

    # Opening URL via proxy
    res = urllib2.urlopen('http://www.studentenwerk-aachen.de/speiseplaene/ahornstrasse-w.html')

    # Printing response header from proxy server
    pprint.pprint(res.headers.dict)
    # Printing length of response content
    h = res.read()
    print(len(h))
