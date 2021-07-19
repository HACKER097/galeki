from pytube import YouTube
from pygame import mixer
from pydub import AudioSegment
import urllib.request
import os
import re

def reduce(function, iterable, initializer=None):
    it = iter(iterable)
    if initializer is None:
        try:
            initializer = next(it)
        except StopIteration:
            raise TypeError('reduce() of empty sequence with no initial value')
    accum_value = initializer
    for x in it:
        accum_value = function(accum_value, x)
    return accum_value

def splitlist(iterable, where):
    def splitter(acc, item, where=where):
        if item == where:
            acc.append([])
        else:
            acc[-1].append(item)
        return acc
    return reduce(splitter, iterable, [[]])


def getsubs(link):
	subs = YouTube(link).captions.all()[0].generate_srt_captions()
	return subs

def subcleaner(sub):
	seperated = splitlist(sub.split("\n"), "")
	for i in range(len(seperated)):
		seperated[i][1] = seperated[i][1].split(" --> ")
		time1 = seperated[i][1][0].split(",") 
		time1[0] = time1[0].split(":")
		time1  = int(time1[0][0])*60*60 + int(time1[0][1])*60 + int(time1[0][2])
		seperated[i][1][0] = time1

		time1 = seperated[i][1][1].split(",") 
		time1[0] = time1[0].split(":")
		time1  = int(time1[0][0])*60*60 + int(time1[0][1])*60 + int(time1[0][2])
		seperated[i][1][1] = time1
	return seperated 

def GetLinks(search_string):
    html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_string.replace(" ", "+"))
    video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
    return "http://youtube.com/watch?v=" + str(video_ids[0])


def GetSong(link):

    video = YouTube("http://youtube.com/" + link.split("/")[-1] )

    try:
        video.streams
    except:
        return "WRONG LINK ERROR"

    try:
        songfile = str(video.streams.get_by_itag(251).download(timeout=30))
    except:
        return "DOWNLOAD ERROR"

    try:
        AudioSegment.from_file(songfile, "webm").export(str(songfile + ".ogg"), format="ogg")
    except:
        return "CONVERT ERROR"

    os.remove(songfile) 
    if os.name == "posix":
        songpath = str(songfile+".ogg").split("/")[-1]
    else:
        songpath = str(songfile+".ogg").split("\\")[-1]
        
    os.rename(songfile+".ogg", songpath)

    return songpath

link = GetLinks(input("ENTER SONG NAME: "))

slean = subcleaner(getsubs(link))
mixer.init()
mixer.music.load(GetSong(link))
mixer.music.play()

while True:

	for i in range(len(slean)):
		if slean[i][1][0]==int(mixer.music.get_pos()/1000):
			print(slean[i][2])

