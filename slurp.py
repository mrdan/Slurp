#!/usr/bin/python
# coding: utf-8

##
## RSS IMG Slurp - Takes an rss feed and takes the first image from each entry (designed for use with google reader "starred item" feeds)
##

#TODO: blacklist support for ad domains
#TODO: some feeds stick in 1x1 images, probably for analytics, so they get counted. Annoying.
#TODO: currently assumes all images are JPGs!

import feedparser
import os
import urllib, string, getopt, sys, time, logging, re, random, codecs
from pickle import dump, load
from HTMLParser import HTMLParser

_filedir = "./slurped/"
userid = "000000000000000"
retrieveNum = "1000000000"

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='./slurp.log',
                    filemode='a+')

#   
# Gets and parses the feed
def getfeed(feedURL):
    feed = feedparser.parse( feedURL )
    return feed.entries
    
#
# Downloads the image from the URL in the feed
def downloadFromURL(URL, downloadName):
    downloadDetails = urllib.urlretrieve(URL, _filedir + downloadName)
    logging.info("Downloaded " + _filedir + downloadName + " from " + URL)
    return downloadDetails
    
#
# main function    
def main():
    valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    _filedir = "./slurped/"
    entries = getfeed("http://www.google.com/reader/public/atom/user/" + userid + "/state/com.google/starred?n=" + retrieveNum)
    x = 0
    print "Working…"
    while x < len(entries):
        safefilename = ""
        fieldtosearch = ""
        
        # Find which field to search for images
        if entries[x].has_key('content'):
            fieldtosearch = entries[x].content[0].value
        elif entries[x].has_key('summary'):
            fieldtosearch = entries[x].summary
      
        # Generate our filename
        if entries[x].has_key('link'):
            filename = entries[x].links[0].href
            safefilename = ''.join(c for c in filename if c in valid_chars)

        # Get images
        if fieldtosearch != "":
            m = re.search("(?<=img\ssrc\=[\x27\x22])[^\x27\x22]*(?=[\x27\x22])", fieldtosearch)
            if m != None:
                # We only want the first image
                if safefilename == "":
                    filename = time.strftime("%H%M%S%d%m%Y")
                    downloadFromURL(m.group(0), filename +"_" + str(random.randint(1, 1000)) + ".jpg") #TODO: mightnt actually be a jpg!
                else:
                    downloadFromURL(m.group(0), safefilename + ".jpg")
                    
        # Write companion text file
        if os.path.exists(_filedir+safefilename+".jpg"):
            ourfile = codecs.open(_filedir + safefilename+".txt", 'w', encoding="utf-8")
            ourfile.write("## " + entries[x].links[0].href + '\n')
            if entries[x].has_key('title'):
                ourfile.write("## " + entries[x].title + '\n')
            if fieldtosearch != "":
                ourfile.write('\n' + strip_tags(fieldtosearch) + '\n')

            ourfile.close()
            
        x = x + 1
    print "Done!"
#        
# Main program body
if __name__ == "__main__":
    main()