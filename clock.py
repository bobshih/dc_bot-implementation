import os
import urllib

from apscheduler.schedulers.blocking import BlockingScheduler

heroku_link = os.environ['heroku_link']

sched = BlockingScheduler()

@sched.scheduled_job('interval', minutes = 19)
def scheduled_job():
    conn = urllib.request.urlopen(heroku_link)
        
    for key, value in conn.getheaders():
        print(key, value)

sched.start()