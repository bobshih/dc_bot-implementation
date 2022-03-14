import os
import urllib.request
from flask import Flask

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

@app.route("/hello_world")
def hello_world():
    return "<p>Hello, World!</p>"

heroku_link = os.environ['heroku_link']
# heroku_link = "http://127.0.0.1:5000/hello_world"

sched = BackgroundScheduler()

@sched.scheduled_job('interval', seconds=3)#, minutes = 19)
def scheduled_job():
    conn = urllib.request.urlopen(heroku_link)
    print(conn.read())
    for key, value in conn.getheaders():
        print(key, value)

sched.start()