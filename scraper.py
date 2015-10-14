# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# USAGE: This script will crawl a podbay.fm show page, follow all the episode links,
# then follow all the mp3 download links on the episode pages.
# The show URL is hardcoded in to the script, edit it at the bottom of this file.

__author__ = 'JWhong'

import sys

if (sys.version_info > (3, 0)):
    pass
else:
    print("Python 3 required!")
    raw_input("Press Enter to finish...")
    exit(0)

import urllib.request
import re
import time
import os
import traceback

class Reporter(object):
    """
    Keeps track of bytes downloaded on a particular file.
    Meant to be instantiated, then have reportHook fed in to urllib.request.urlretrieve
    """
    def __init__(self):
        self.bytes_downloaded = 0
        self.tstart = time.time()
        print("")
    def reportHook(self, count, block_size, total_size):
        self.bytes_downloaded += block_size
        #if count == 0:
            #print("Server reports target file is %.3fMB"%(total_size/(1024*1024.)))
        if (not (count%64)):
            dt = time.time()-self.tstart
            b_dl = self.bytes_downloaded/(1024*1024)
            t_dl = total_size/(1024*1024)
            sys.stdout.write("\r%04.1f%% done :: %04.2fMB/s :: %05.2fMB/%05.2fMB"%(100*self.bytes_downloaded/total_size,b_dl/dt,b_dl,t_dl))
            sys.stdout.flush()

class PodbayShowScraper(object):
    def __init__(self):
        self.mp3_matcher     = re.compile('(?<=")[^"]+\.mp3(?=")')
        self.episode_matcher = re.compile('(?<=")[^"]+podbay.fm[^"]+autostart\=1(?=")')
    def tryNTimes(self, f, n):
        """
        Generic exception catcher
        :param f: Callable to try
        :param n: number of times to try
        :return: whatever the callable returns, None on exception
        """
        rval = None
        for i in range(n):
            try:
                rval = f()
                break
            except Exception:
                print("Lambda error!  Attempt %d"%i)
                traceback.print_exc()
                rval = None
        return rval
    def scrapeEpisodePage(self, page_url):
        """
        :param target_url: A string of a podbay.fm episode page, eg. http://podbay.fm/show/354668519/e/1442458800?autostart=1
        :return:
        """
        rval = self.tryNTimes(lambda:urllib.request.urlopen(page_url), 5)
        if rval == None:
            print("Failed to scrape %s"%page_url)
            return
        payload = str(rval.read())
        urls = self.mp3_matcher.findall(payload)
        for url in urls:
            reporter = Reporter()
            split = url.rsplit('/',1)
            fname = split[1]
            if os.path.isfile(fname):
                print("Already downloaded:", fname)
                continue
            print("Downloading", url)
            self.tryNTimes(lambda:urllib.request.urlretrieve(url,fname,reporter.reportHook), 10)
            print()

    def scrapeShowPage(self, target_url):
        """
        Downloads all a show's episodes to the local directory
        :param target_url: A string of a podbay.fm podcast url, eg http://podbay.fm/show/354668519
        :return: None
        """
        print("\nStarting scrape of", target_url)
        rval = self.tryNTimes(lambda:urllib.request.urlopen(target_url), 5)
        if rval == None:
            print("Failed to scrape %s"%target_url)
            return
        payload = str(rval.read())                  # Get the website's page payload as a string
        urls = self.episode_matcher.findall(payload)# Find all matching urls
        urls = list(set(urls))                      # Remove duplicates
        print("Matched", len(urls), "urls")
        for i in range(len(urls)):
            print("Episode %d of %d"%(i+1,len(urls)))
            self.scrapeEpisodePage(urls[i])
        print("\nFinished scraping", target_url)

if __name__=="__main__":
    scraper = PodbayShowScraper()
    
    ############################## BELOW IS THE LINE YOU SHOULD EDIT ###################################
    scraper.scrapeShowPage("http://podbay.fm/show/216713308")
    ############################## ABOVE IS THE LINE YOU SHOULD EDIT ###################################
    
    input("Press Enter to finish...")
