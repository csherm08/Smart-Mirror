from tkinter import *   # python3
import locale
import threading
import time
import requests
import json
import traceback
import feedparser
import email
import imaplib
#import Tkinter as tk   # python
from contextlib import contextmanager
from PIL import Image, ImageTk

LOCALE_LOCK = threading.Lock()

TITLE_FONT = ("Helvetica", 18, "bold")
ip = '<IP>'
ui_locale = '' # e.g. 'fr_FR' fro French, '' as default
time_format = 12 # 12 or 24
date_format = "%b %d, %Y" # check python doc for strftime() for options
news_country_code = 'us'
weather_api_token = 'bdd065dd3c5ab1602abfdcce073493e6' # create account at https://darksky.net/dev/
weather_lang = 'en' # see https://darksky.net/dev/docs/forecast for full list of language parameters values
weather_unit = 'us' # see https://darksky.net/dev/docs/forecast for full list of unit parameters values
latitude = None # Set this if IP location lookup does not work for you (must be a string)
longitude = None # Set this if IP location lookup does not work for you (must be a string)
xlarge_text_size = 94
large_text_size = 48
medium_text_size = 28
small_text_size = 18
xsmall_text_size = 9
count=0

@contextmanager
def setlocale(name): #thread proof function to work with locale
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)

icon_lookup = {
    'clear-day': "assets/Sun.png",  # clear sky day
    'wind': "assets/Wind.png",   #wind
    'cloudy': "assets/Cloud.png",  # cloudy day
    'partly-cloudy-day': "assets/PartlySunny.png",  # partly cloudy day
    'rain': "assets/Rain.png",  # rain day
    'snow': "assets/Snow.png",  # snow day
    'snow-thin': "assets/Snow.png",  # sleet day
    'fog': "assets/Haze.png",  # fog day
    'clear-night': "assets/Moon.png",  # clear sky night
    'partly-cloudy-night': "assets/PartlyMoon.png",  # scattered clouds night
    'thunderstorm': "assets/Storm.png",  # thunderstorm
    'tornado': "assests/Tornado.png",    # tornado
    'hail': "assests/Hail.png"  # hail
}

class SampleApp(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        topFrame = Frame(self, background = 'black')
        bottomFrame = Frame(self, background = 'black')
        topFrame.pack(side=TOP, fill="both", expand=True)
        bottomFrame.pack(side=BOTTOM, fill="both", expand=True)

        self.state = False
        self.frames = {}
        self.bind("<Return>", self.toggle_fullscreen)
        self.bind("<Escape>", self.toggle_fullscreen)

        ## LIST OF PAGES
        self.EmailFrame = Email(parent=topFrame, controller=self)
        self.WeatherFrame = Weather(parent=topFrame, controller=self)
        self.NewsFrame = News(parent=topFrame, controller=self)
        self.ClockFrame= Clock(parent=topFrame, controller=self)
        self.EmailCountFrame = EmailCount(parent=topFrame, controller=self)

        ## STORE IN ARRAY
        self.frames= [self.EmailCountFrame, self.WeatherFrame, self.ClockFrame, self.NewsFrame, self.EmailFrame]

        # TEMP BUTTON TO GO PAGE TO PAGE (Replace with Python button)
        self.CurrentButton = Button(bottomFrame, text="Next Page", command=self.next_page)
        self.CurrentButton.pack()

        # We want certain frames on the same page, so get array of pages count
        self.unique_pages = []
        for F in self.frames:
            if F.page not in self.unique_pages:
                self.unique_pages.append(F.page)
        print(len(self.unique_pages))

        self.show_frames()
    def next_page(self):
        global count
        count = count + 1
        self.show_frames()
    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.attributes("-fullscreen", self.state)
        return "break"
    def end_fullscreen(self, event=None):
        self.state = False
        tk.attributes("-fullscreen", False)
        return "break"

    def show_frames(self):
        for F in self.frames:
            modCount = count%len(self.unique_pages)
            if F.page == modCount:
                F.pack(side=F.side, anchor=F.anchor, padx=100, pady=60)
            else:
                F.pack_forget()

class Email(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, background = 'black')
        self.page=1
        self.side=LEFT
        self.anchor=N
        self.username = "carterjsherman"
        self.password = "bmxrbieixabzkzbn"
        self.unreadEmails = []
        self.readEmails()
        self.config(bg='black')
        self.title = 'Email'
        self.unreadEmailsText = "You have " + str(len(self.unreadEmails)) + " emails"
        self.unreadEmailsLabel = Label(self, text=self.unreadEmailsText, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.unreadEmailsLabel.pack(side=TOP, anchor=W)

        for tuple1 in self.unreadEmails:
            fromText=tuple1[0]
            subjectText=tuple1[1]
            print(tuple1[0])
            self.fromLabel = Label(self, text=fromText, font=('Helvetica', small_text_size), fg="white", bg="black")
            self.subjectLabel = Label(self, text=subjectText, font=('Helvetica', xsmall_text_size), fg="white", bg="black")
            self.fromLabel.pack(anchor=W)
            self.subjectLabel.pack(anchor=W, padx=20)

    def readEmails(self):
        conn = imaplib.IMAP4_SSL("imap.gmail.com", 993)

        try:
            (retcode, capabilities) = conn.login(self.username, self.password)
        except:
            print(sys.exc_info()[1])
            sys.exit(1)

        conn.select('INBOX') # Select inbox or default namespace
        (retcode, messages) = conn.search(None, 'UNSEEN')
        messages_parsed = messages[0].split()

        print(len(messages[0].split()))
        if retcode == 'OK':
            for num in messages[0].split():
                typ, data = conn.fetch(num,'(RFC822)')
                msg = email.message_from_string(data[0][1].decode('utf-8'))
                typ, data = conn.store(num,'-FLAGS','\\Seen')
                emailTuple = (msg['From'], msg['Subject'])
                self.unreadEmails.append(emailTuple)
                #print(msg['From'])
                #print(msg['Subject'])
        conn.close()
        #print(self.unreadEmails)

class News(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, background = 'black')
        self.page=2
        self.side=TOP
        self.anchor=W
        self.config(bg='black')
        self.title = 'News' # 'News' is more internationally generic
        self.newsLbl = Label(self, text=self.title, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.newsLbl.pack(side=TOP, anchor=W)
        self.headlinesContainer = Frame(self, bg="black")
        self.headlinesContainer.pack(side=TOP)
        self.get_headlines()
    def get_headlines(self):
        try:
            # remove all children
            for widget in self.headlinesContainer.winfo_children():
                widget.destroy()
            if news_country_code == None:
                headlines_url = "https://news.google.com/news?ned=us&output=rss"
            else:
                headlines_url = "https://news.google.com/news?ned=%s&output=rss" % news_country_code

            feed = feedparser.parse(headlines_url)

            for post in feed.entries[0:5]:
                headline = NewsHeadline(self.headlinesContainer, post.title)
                headline.pack(side=TOP, anchor=W)
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get news.") % e

        self.after(600000, self.get_headlines)


class NewsHeadline(Frame):
    def __init__(self, parent, event_name=""):
        Frame.__init__(self, parent, bg='black')

        image = Image.open("assets/Newspaper.png")
        image = image.resize((25, 25), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)

        self.iconLbl = Label(self, bg='black', image=photo)
        self.iconLbl.image = photo
        self.iconLbl.pack(side=LEFT, anchor=N)

        self.eventName = event_name
        self.eventNameLbl = Label(self, text=self.eventName, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.eventNameLbl.pack(side=LEFT, anchor=N)

class Clock(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent, bg='black')
        self.page=0
        self.side=RIGHT
        self.anchor=N
        # initialize time label
        self.time1 = ''
        self.timeLbl = Label(self, font=('Helvetica', large_text_size), fg="white", bg="black")
        self.timeLbl.pack(side=TOP, anchor=E)
        # initialize day of week
        self.day_of_week1 = ''
        self.dayOWLbl = Label(self, text=self.day_of_week1, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dayOWLbl.pack(side=TOP, anchor=E)
        # initialize date label
        self.date1 = ''
        self.dateLbl = Label(self, text=self.date1, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.dateLbl.pack(side=TOP, anchor=E)
        self.iconLbl = Label(self, bg="black")
        self.iconLbl.pack(side=TOP, anchor=E)

        #### THIS IS SO WRONG FUCKING FIX IT
        image = Image.open("assets/emailLogo.png")
        image = image.resize((100, 100), Image.ANTIALIAS)
        image = image.convert('RGB')
        photo = ImageTk.PhotoImage(image)
        self.iconLbl.config(image=photo)
        self.iconLbl.image = photo
        self.tick()

    def tick(self):
        with setlocale(ui_locale):
            if time_format == 12:
                time2 = time.strftime('%I:%M %p') #hour in 12h format
            else:
                time2 = time.strftime('%H:%M') #hour in 24h format

            day_of_week2 = time.strftime('%A')
            date2 = time.strftime(date_format)
            # if time string has changed, update it
            if time2 != self.time1:
                self.time1 = time2
                self.timeLbl.config(text=time2)
            if day_of_week2 != self.day_of_week1:
                self.day_of_week1 = day_of_week2
                self.dayOWLbl.config(text=day_of_week2)
            if date2 != self.date1:
                self.date1 = date2
                self.dateLbl.config(text=date2)
            # calls itself every 200 milliseconds
            # to update the time display as needed
            # could use >200 ms, but display gets jerky
            self.timeLbl.after(200, self.tick)


class Weather(Frame):
    def __init__(self, parent,controller):
        Frame.__init__(self, parent, bg='black')
        self.page = 0
        self.side=LEFT
        self.anchor=N
        self.temperature = ''
        self.forecast = ''
        self.location = ''
        self.currently = ''
        self.icon = ''
        self.degreeFrm = Frame(self, bg="black")
        self.degreeFrm.pack(side=TOP, anchor=W)
        self.temperatureLbl = Label(self.degreeFrm, font=('Helvetica', xlarge_text_size), fg="white", bg="black")
        self.temperatureLbl.pack(side=LEFT, anchor=N)
        self.iconLbl = Label(self.degreeFrm, bg="black")
        self.iconLbl.pack(side=LEFT, anchor=N, padx=20)
        self.currentlyLbl = Label(self, font=('Helvetica', medium_text_size), fg="white", bg="black")
        self.currentlyLbl.pack(side=TOP, anchor=W)
        self.forecastLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.forecastLbl.pack(side=TOP, anchor=W)
        self.locationLbl = Label(self, font=('Helvetica', small_text_size), fg="white", bg="black")
        self.locationLbl.pack(side=TOP, anchor=W)
        self.get_weather()

    def get_ip(self):
        try:
            ip_url = "http://jsonip.com/"
            req = requests.get(ip_url)
            print(req)
            ip_json = json.loads(req.text)
            return ip_json['ip']
        except Exception as e:
            traceback.print_exc()
            return "Error: %s. Cannot get ip." % e

    def get_weather(self):
        try:

            if latitude is None and longitude is None:
                # get location
                location_req_url = "http://freegeoip.net/json/%s" % self.get_ip()
                print(location_req_url)
                r = requests.get(location_req_url)
                location_obj = json.loads(r.text)

                lat = location_obj['latitude']
                lon = location_obj['longitude']

                location2 = "%s, %s" % (location_obj['city'], location_obj['region_code'])

                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, lat,lon,weather_lang,weather_unit)
            else:
                location2 = ""
                # get weather
                weather_req_url = "https://api.darksky.net/forecast/%s/%s,%s?lang=%s&units=%s" % (weather_api_token, latitude, longitude, weather_lang, weather_unit)

            r = requests.get(weather_req_url)
            weather_obj = json.loads(r.text)

            degree_sign= u'\N{DEGREE SIGN}'
            temperature2 = "%s%s" % (str(int(weather_obj['currently']['temperature'])), degree_sign)
            currently2 = weather_obj['currently']['summary']
            forecast2 = weather_obj["hourly"]["summary"]

            icon_id = weather_obj['currently']['icon']
            icon2 = None

            if icon_id in icon_lookup:
                icon2 = icon_lookup[icon_id]

            if icon2 is not None:
                if self.icon != icon2:
                    self.icon = icon2
                    print(icon2)
                    image = Image.open(icon2)
                    image = image.resize((100, 100), Image.ANTIALIAS)
                    image = image.convert('RGB')
                    photo = ImageTk.PhotoImage(image)

                    self.iconLbl.config(image=photo)
                    self.iconLbl.image = photo
            else:
                # remove image
                self.iconLbl.config(image='')

            if self.currently != currently2:
                self.currently = currently2
                self.currentlyLbl.config(text=currently2)
            if self.forecast != forecast2:
                self.forecast = forecast2
                self.forecastLbl.config(text=forecast2)
            if self.temperature != temperature2:
                self.temperature = temperature2
                self.temperatureLbl.config(text=temperature2)
            if self.location != location2:
                if location2 == ", ":
                    self.location = "Cannot Pinpoint Location"
                    self.locationLbl.config(text="Cannot Pinpoint Location")
                else:
                    self.location = location2
                    self.locationLbl.config(text=location2)
        except Exception as e:
            traceback.print_exc()
            print ("Error: %s. Cannot get weather." % e)

        self.after(600000, self.get_weather)

    @staticmethod
    def convert_kelvin_to_fahrenheit(kelvin_temp):
        return 1.8 * (kelvin_temp - 273) + 32

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()
