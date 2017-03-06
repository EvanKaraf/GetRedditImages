#!/usr/bin/python
import praw
import urllib
import os.path
from imgurpython import ImgurClient
from BeautifulSoup import BeautifulSoup

import ConfigParser

pathFolder = "downloaded_images"

def getimgurlink(s):
	client = ImgurClient(client_idImgur, client_secretImgur)
	index1 = s.rfind('.')
	index2 = s.rfind('/')
	if index2 < index1:
		imgid = s[index2+1:index1]
	else:
		imgid = s[index2+1:]
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
	if os.path.exists(title + ".jpg") == False:
		f = open(title + ".jpg",'wb')
		link = getimgurlink(submission.url)
		f.write(urllib.urlopen(link).read())
		f.close()

def flickrSave(submission,title):
	if os.path.exists(title) == False:
		link = getflickrlink(submission.url)
		print("GOTBACKFROMFUNCTION:",link)
		if link != "":
			f = open(title,'wb')
			f.write(urllib.urlopen(link).read())
			f.close()

def redditSave(submission,title):
	if os.path.exists(title + ".jpg") == False:
		f = open(title + ".jpg",'wb')
		f.write(urllib.urlopen(submission.url).read())
		f.close()

def main():
	config = ConfigParser.RawConfigParser()
	config.read('imgur.ini')
	client_idImgur = config.get('credentials', 'client_id')
	client_secretImgur = config.get('credentials', 'client_secret')

	reddit = praw.Reddit('bot1')
	subreddit = reddit.subreddit("EarthPorn")
	if not os.path.exists(pathFolder):
		os.mkdir(pathFolder)
	os.chdir(pathFolder)
	chars = ['!','.',' ','(',')','[',']','\\','/','?','*','|',",",':',"\""]
	first = True
	counter = 1
	maxLimit = input('Enter amount of posts to scan:')
	for submission in subreddit.hot(limit=maxLimit):
		title = submission.title
		for char in chars:
			title = title.replace(char,'_')
		print counter,"Downloading ",title
		if(submission.post_hint == 'image'):
			redditSave(submission,title)
		elif submission.post_hint == 'link' and submission.domain == 'imgur.com':
			imgurSave(submission,title)
		#elif submission.domain == "flickr.com":
			#flickrSave(submission,title)
		counter = counter + 1

	print("---------------------------------\n")

if __name__ == "__main__":
	main()