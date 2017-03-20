#!/usr/bin/python
import sys
import requests
import urllib
import praw
import prawcore
import os.path
from imgurpython import ImgurClient
import BeautifulSoup

import ConfigParser

green = '\033[92m'
resetCol = '\033[0m'
pathFolder = "downloaded_images"
counter = 0
client_idImgur = ""
client_secretImgur = ""

def getimgurlink(s):
    client = ImgurClient(client_idImgur, client_secretImgur)
    index1 = s.rfind('.')
    index2 = s.rfind('/')
    if index2 < index1:
        imgid = s[index2+1:index1]
    else:
        imgid = s[index2+1:]
    if "/a/" in s:
    	return ""
    item = client.get_image(imgid)
    return item.link

def getflickrlink(s):
    print('flickr link:',s)
    if "/in/" not in s:
        opener = urllib.FancyURLopener({})
        page = opener.open(s).read()
        parsed = BeautifulSoup(page)
        div = parsed.find('div', id='allsizes-photo')
        children = div.findChildren()
        return children[0].get('src')
    else:
        return ""

def imgurSave(submission,title):
    link = getimgurlink(submission.url)
    if link == "":
        return False
    return downloadFile(title,submission.url)

def flickrSave(submission,title):
    if os.path.exists(title) == False:
        link = getflickrlink(submission.url)
        if link != "":
            f = open(title,'wb')
            f.write(urllib.urlopen(link).read())
            f.close()

def redditSave(submission,title):
    return downloadFile(title,submission.url)
  

def downloadFile(filename,url):
	global counter
	if ".gif" in url:
		filename = filename + '.gif'
	else:
		filename = filename + '.jpg'
	if os.path.exists(filename) == True:
		return False
	with open(filename, "wb") as file:
	    response = requests.get(url, stream = True)

	    fsize = response.headers.get('content-length')

	    downloaded = 0

	    if fsize is not None:
	        fsize = int(fsize)
	        print( "%s. Downloading %s") % (counter, filename)
	        for packet in response.iter_content(chunk_size = 2048):
	            downloaded += len(packet)
	            file.write(packet)
	            progress = 50 * downloaded/fsize
	            sys.stdout.write("\r[%s%s%s%s%s]" % (green,'=' * int(progress-1),'>', ' ' * (49 - int(progress)), resetCol))
	            sys.stdout.flush()
	    print
	    counter += 1

def main():
    config = ConfigParser.RawConfigParser()
    config.read('imgur.ini')
    global client_idImgur
    global client_secretImgur
    client_idImgur = config.get('credentials', 'client_id')
    client_secretImgur = config.get('credentials', 'client_secret')
    reddit = praw.Reddit('bot1')
    subName = raw_input("Enter desired subreddit:")

    try:
        subreddit = reddit.subreddit(subName)
        for submission in subreddit.hot(limit=1):
            title = submission.title
    except (praw.exceptions.PRAWException, prawcore.Redirect) as e:
        print e
        print "Subbreddit doesn't exist,exiting.."
        sys.exit()

    global pathFolder
    pathFolder += subName
    if not os.path.exists(pathFolder):
        os.mkdir(pathFolder)
    os.chdir(pathFolder)
    chars = ['!','.',' ','(',')','[',']','\\','/','?','*','|',",",':',"\""]
    first = True
    maxLimit = raw_input('Enter amount of posts to scan:')
    maxLimit = int(maxLimit)
    global counter
    counter = 1
    for submission in subreddit.hot(limit=maxLimit):
        title = submission.title
        for char in chars:
            title = title.replace(char,'_')
        if not hasattr(submission,'post_hint'):
        	continue
        if(submission.post_hint == 'image'):
         	redditSave(submission,title)
        elif submission.post_hint == 'link' and submission.domain == 'imgur.com':
           	imgurSave(submission,title)
            #elif submission.domain == "flickr.com":
                #flickrSave(submission,title)

    print("---------------------------------\n")
    print "Result:",counter-1,"/",maxLimit

if __name__ == "__main__":
    main()
