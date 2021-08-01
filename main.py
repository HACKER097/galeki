import curses
from curses import textpad
import time
import vlc
from pytube import YouTube, Search, Channel
import urllib.request
import re
import threading




def key_events(stdscr, menu1):
	key = stdscr.getch()

	if key == ord("s"):
		menu1.issearch = True

	if key == ord(" "):
		if menu1.ismedia:
			if menu1.media.is_playing:
				menu1.media.pause()
			else:
				menu1.media.unpause()

			if round(menu1.media.get_position()*100) == 100:
				menu1.media = vlc.MediaPlayer(menu1.link)
				menu1.media.play()

	if key == curses.KEY_LEFT:
		if menu1.ismedia:
			menu1.media.set_time(menu1.media.get_time()-5000)

	if key == curses.KEY_RIGHT:
		if menu1.ismedia:
			menu1.media.set_time(menu1.media.get_time()+5000)

	if key == ord("q"):
		exit()

	if key == curses.KEY_UP:
		if menu1.toppos < 1 and menu1.selected_search == 0:
			pass
		else:
			menu1.selected_search -= 1
			if menu1.selected_search < 0:
				if menu1.toppos < 0:
					menu1.selected_search = 0
				else:
					menu1.toppos-=1
					menu1.botpos-=1
					menu1.selected_search += 1


	if key == curses.KEY_DOWN:
		if menu1.searchlist_links[menu1.selected_search] == menu1.search_results[-1]:
			pass

		else:


			menu1.selected_search += 1
			if menu1.selected_search > menu1.maxlistlen-1:
				if menu1.botpos < menu1.maxlistlen:
					menu1.selected_search = len(menu1.search_results)
				else:
					menu1.toppos+=1
					menu1.botpos+=1
					menu1.selected_search -= 1

	if key == curses.KEY_ENTER or key == 10 or key == 13:  # this is enter key
		try:
			link = menu1.searchlist_links[menu1.selected_search]
			#menu1.playlink(menu1.searchlist_links[menu1.selected_search])
			getsongthread = threading.Thread(target=menu1.playlink, args=(link,))
			getsongthread.daemon = True
			getsongthread.start()

		except IndexError:
			pass


	

def GetLinks(search_string):
	links = []
	html = urllib.request.urlopen("https://www.youtube.com/results?search_query=" + search_string.replace(" ", "+"))
	video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
	for link in video_ids:
		links.append("http://youtube.com/watch?v=" + link)
	return links

class menu:
	def __init__(self):
		self.issearch = False
		self.ismedia = False
		self.search_results = []
		self.search_titles = []
		self.toppos = 0
		self.botpos = 5
		self.selected_search = 0
		self.maxlistlen = 5
		self.isnotify = False
		self.notifystring = ""
		self.notifyendtime = 0

	def notify(self, stdscr, maxx):
		if self.isnotify:
			curses.textpad.rectangle(stdscr, 0, 5, 2, maxx-1)
			stdscr.addstr(1,6, self.notifystring[:maxx-6])
			if int(time.time()) >= self.notifyendtime:
				self.isnotify = False

	def playlink(self, link):
		video = YouTube(link)
		self.video_name = video.title
		self.link = video.streams.get_by_itag(251).url
		
		if self.ismedia:
			self.media.stop()

		self.media = vlc.MediaPlayer(self.link)
		self.media.play()
		self.ismedia = True

		self.video_data = [ "Uploader: " + video.author , "Upload Date: " + str(video.publish_date)[:10], "Views: " + "{:,}".format(video.views)]

	def get_links(self):

		self.search_results = GetLinks(self.search_term)

		self.search_titles = []

		for link in self.search_results:
			self.search_titles.append(YouTube(link).title)


	def searchbar(self, stdscr, maxy, maxx):
		stdscr.addstr(1,1," ▶ ", curses.color_pair(1) | curses.A_BOLD)

		if self.issearch:

			stdscr.attron(curses.color_pair(2))

			curses.textpad.rectangle(stdscr, 0, 5, 2, maxx-1)
			stdscr.addstr(1,6,"SEARCH : ")

			stdscr.attroff(curses.color_pair(2))

			curses.echo()
			curses.nocbreak()
			stdscr.nodelay(False)
			stdscr.keypad(False)
			curses.curs_set(1)

			self.search_term = str(stdscr.getstr())

			curses.noecho()
			curses.cbreak()
			stdscr.nodelay(True)
			stdscr.keypad(True)
			curses.curs_set(0)

			self.issearch = False

			#self.get_links()

			self.botpos = maxy-(6)
			self.toppos = 0
			self.selected_search = 0
			self.maxlistlen = maxy-(6)

			self.notifystring = "GETTING LINKS"
			self.notifyendtime = int(time.time()) + 5
			self.isnotify = True

			get_linksthread = threading.Thread(target=self.get_links,)
			get_linksthread.daemon = True
			get_linksthread.start()



		else:

			curses.textpad.rectangle(stdscr, 0, 5, 2, maxx-1)
			stdscr.addstr(1,6,"SEARCH : ", curses.A_BOLD)

	def searchbox(self, stdscr, maxy, maxx):

		stdscr.attron(curses.color_pair(2))

		curses.textpad.rectangle(stdscr, 3, int(maxx/2), maxy-2, maxx-1)

		stdscr.attroff(curses.color_pair(2))

		self.searchlist_links = self.search_results[self.toppos:self.botpos]
		searchlist = self.search_titles[self.toppos:self.botpos]


		for i in range(len(searchlist)):
			if i == self.selected_search:

				stdscr.addstr(4+i, int(maxx/2)+1, searchlist[i][:int(maxx/2)-3], curses.A_REVERSE)
			else:
				stdscr.addstr(4+i, int(maxx/2)+1, searchlist[i][:int(maxx/2)-3])

	def lyricbox(self, stdscr, maxy, maxx):

		curses.textpad.rectangle(stdscr, 3, 0, int((maxy-2)/3), int(maxx/2)-1)

		stdscr.addstr(3, 1, self.video_name[:int(maxx/2)-2], curses.A_REVERSE)

		for i in range(len(self.video_data)):
			stdscr.addstr(4+1+i, 1, self.video_data[i][:int(maxx/2)-3])




class progress_bar:
	def __init__(self):
		pass

	def display(self, stdscr, maxy, maxx, progress, menu1):
		stdscr.addstr(maxy-1, 9, "─"*(maxx-10), curses.color_pair(3))
		stdscr.addstr(maxy-1, 9, "─"*int(maxx*progress - 10)+"╼", curses.color_pair(2))

		if menu1.ismedia:
			stdscr.addstr(maxy-1, 0, time.strftime('%M:%S', time.gmtime(int(menu1.media.get_time()/1000))))
			if menu1.media.is_playing():
				stdscr.addstr(maxy-1, 6, "⏸", curses.A_BOLD)
			else:
				stdscr.addstr(maxy-1, 6, "▶", curses.A_BOLD)
		else:
			stdscr.addstr(maxy-1, 0, "00:00")
			stdscr.addstr(maxy-1, 6, "▶", curses.A_BOLD)

def main():
	run = True
	stdscr = curses.initscr()
	stdscr.nodelay(True)
	stdscr.keypad(True)
	curses.curs_set(0)
	curses.start_color()
	curses.noecho()
	curses.cbreak()

	curses.use_default_colors()

	curses.init_pair(1, 0, curses.COLOR_RED)
	curses.init_pair(2, curses.COLOR_RED, -1)
	curses.init_pair(3, 235, -1)

	menu1 = menu()
	progress_bar1 = progress_bar()

	maxy,maxx = stdscr.getmaxyx()

	progress = 0

	try:
		while run:
			start = time.time()

			stdscr.erase()

			if curses.is_term_resized(maxy,maxx):
				maxy,maxx = stdscr.getmaxyx()
				menu1.botpos = maxy-(6)
				menu1.toppos = 0
				menu1.selected_search = 0
				menu1.maxlistlen = maxy-(6)


			progress_bar1.display(stdscr, maxy, maxx, progress, menu1)

			menu1.searchbox(stdscr, maxy, maxx)

			if menu1.ismedia:
				progress = menu1.media.get_position()

				menu1.lyricbox(stdscr, maxy, maxx)

			menu1.searchbar(stdscr, maxy, maxx)

			menu1.notify(stdscr, maxx)


			stdscr.refresh()


	

			key_events(stdscr, menu1)

			time.sleep(max(0.01 - (time.time() - start), 0))
	finally:
		curses.echo()
		curses.nocbreak()
		curses.curs_set(1)
		stdscr.keypad(False)
		stdscr.nodelay(False)
		curses.endwin()


main()

