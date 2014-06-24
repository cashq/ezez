#! /usr/bin/python
# -*- coding: utf-8 -*-
import os
import re
import sys
import urllib
import getopt
import shutil
import datetime
import BeautifulSoup

import eyed3

DEBUG = True
NO_DOWNLOAD = False
verbose = False

siteurl = "http://easyfm.azurewebsites.net"
mp3url = "%s/%s" % (siteurl, "mod.cri.cn/eng/ez/morning")
ezm_start_year = 2004

info_url_template = "http://easyfm.azurewebsites.net/$year/$mon/$day"
mp3_url_template = "http://easyfm.azurewebsites.net/mod.cri.cn/eng/ez/morning/$year/ezm$myear$mon$day.mp3"

html_code = {r"&quot;":"\"", r"&amp;":"&", r"&nbsp;":" ", r"&lt;":"<", r"&gt;":">", r"&#61;":"=", r"&#8230;":"..."}
def replace_html_code(line):
    out = line
    for k in html_code.keys():
        out = re.sub(k, html_code[k], out)
    return out

def trim(line):
    out = re.sub(r'^\s*', '', line)
    out = re.sub(r'^\s*', '', out)
    return out

def usage():
    print "%s [-hv] -o out_dir -y year -m month -d day -a artwork"

try:
    opts, args = getopt.getopt(sys.argv[1:], "fhivo:y:m:d:a:", ["help", "output=", "year=", "month=", "day=", "artwork="])
except getopt.GetoptError as err:
    print err
    usage()
    sys.exit(2)

dt = datetime.datetime.now().timetuple()
is_current_year = False
is_current_month = False 
is_interactive = True

for o, a in opts:
    if o == "-v":
        verbose = True
    elif o in ("-h", "--help"):
        usage()
        sys.exit()
    elif o in ("-i"):
        print "site url:", siteurl
        print "info url:", info_url_template
        print "mp3 url: ", mp3_url_template
        sys.exit()
    elif o in ("-o", "--output"):
        outdir = re.sub(r'/*$', '', a)
    elif o in ("-f"):
        is_interactive = False
    elif o in ("-y", "--year"):
        year = int(a)
        if year < ezm_start_year and (year > dt[0]):
            print "Invalid year. *", year, "*/", mon, "/", day
            sys.exit(1)
        if year == dt[0]:
            is_current_year = True
    elif o in ("-m", "--month"):
        mon = int(a)
        if mon > 12 or (is_current_year and mon > dt[1]):
            print "Invalid month:", year, "/*", mon, "*/", day
            sys.exit(1)
        if is_current_year and (mon == dt[1]):
            is_current_month = True
    elif o in ("-d", "--day"):
        day = int(a)
        if day > 32 or (is_current_month and day > dt[2]):
            print "Invalid day:", year, "/", mon, "/*", day, "*"
            sys.exit(1)
    elif o in ("-a", "--artwork"):
        artwork = a
        if not os.path.exists(artwork):
            print "Specified artwork does not exist:", a
            if is_interactive:
                while answer is None or ((not answer is "Y") and (not answer is "n")):
                    answer = input('Abort? (Y/n)')
                if answer is "Y":
                    artwork = None
                else:
                    sys.exit(2)
            else:
                artwork = None

            if artwork is None:
                print "No artwork will be attached."
    else:
        usage()
        sys.exit(1)

if not outdir:
    outdir = "output"
    if DEBUG:
        print "Default output directory:", outdir

#outdir = re.sub(r'/*$', '', sys.argv[1])
#year = int(sys.argv[2])
#mon = int(sys.argv[3])
#day = int(sys.argv[4])
#artwork = sys.argv[5]

artist = u"小飞 & 喻舟"
album = u"Easy Morning 飞鱼秀"

outdir = "%s/%s" % (os.path.abspath(outdir), year)
if not os.path.exists(outdir):
    os.makedirs(outdir)

myear = year % 100
mon = "%02d" % mon
day = "%02d" % day

fname = "%s_%s%s_info.html" % (year, mon, day)
info_url = u"%s/%s/%s/%s/" % (siteurl, year, mon, day)
if DEBUG:
    print info_url

urllib.urlretrieve(info_url.encode("UTF-8"), fname)
if os.path.exists(fname):
    soup = BeautifulSoup.BeautifulSoup(open(fname))
    divs = soup.findAll("div", attrs={"class":"audio-content"})
    for div in divs:
        doit = False
        if not div is None and not div.p is None:
            try:
                if len(div.p.contents) > 1:
                    target = div.p.contents[1]
                else:
                    target = div.p.contents[0]
                target = trim(target)
                title = replace_html_code(target)
                if DEBUG:
                    print title
                try:
                    m = re.search(r'\d+-(\d+)-(\d+)', title)
                    if DEBUG:
                        print "original mon", mon
                        print "original day", day 
                        print "adjusted mon", m.group(1)
                        print "adjusted day", m.group(2)
                    mon = m.group(1)
                    day = m.group(2)
                except AttributeError:
                    print "not found date information"

                title = unicode(title)
                if NO_DOWNLOAD:
                    doit = False
                else:
                    doit = True
                if os.path.exists(fname):
                    os.unlink(fname)
            except IndexError:
                if DEBUG:
                    print "Problem with %s%s%s" % (year, mon, day)

                if not DEBUG and os.path.exists(fname):
                    os.unlink(fname)

        outfile = "ezm_%s%s.mp3" % (mon, day)
        if doit and not os.path.exists(("%s/%s") % (outdir, outfile)):
            down_url = "%s/%s/ezm%s%s%s.mp3" % (mp3url, year, myear, mon, day)
            if DEBUG:
                print down_url

            if doit:
                print "Start: ", title
                urllib.urlretrieve(down_url, outfile)
                if os.path.exists(outfile):
                    mp3 = eyed3.load(outfile)
                    if not mp3 is None:
                        if mp3.tag is None:
                            mp3.initTag()
                        mp3.tag.artist = artist
                        mp3.tag.album = album
                        mp3.tag.title = title
                        if artwork:
                            image = open(artwork, "rb").read()
                            mp3.tag.images.set(3, image, "image/jpeg")
                        mp3.tag.save()
                        shutil.move(outfile, ("%s/%s") % (outdir, outfile))
                        print "Done: ", title
                    elif DEBUG:
                        print "download link", down_url

else:
    print "Skip: %s%s%s" % (year, mon, day)
    if os.path.exists(outfile):
        os.remove(outfile)

if not DEBUG and os.path.exists(outfile):
    os.remove(outfile)
