import time
from datetime import datetime, timedelta
import requests
from utils import save_file, mark_link_crawled
from utils import get_file_name, join_url, is_valid
from pymongo import MongoClient
from cfg import config
from bs4 import BeautifulSoup
import os


client = MongoClient()
db = client['crawler_DB']
collection = db['Links']
path = "./response_files/"

i = 0
while i < 2:
    i += 1
    links = collection.find()

    count_links = collection.count_documents({})

    if count_links >= config['max_links']:
        print("Maximum limit reached!")
        continue

    for link in links:

        now = datetime.now()
        crawled_dt = link['lastCrawlDt']

        if crawled_dt is not None and (crawled_dt > now - timedelta(hours=24)):
            print(link['link'] + " is already crawled in last 24 hours!" )
            continue
        
        try:
            r = requests.get(link['link'])
        except requests.exceptions.RequestException as e:
            print("Connection Error!")
            continue

        if r.status_code != 200:
            update_link = {"$set": {"isCrawled": True,
                                    "lastCrawlDt": datetime.now(),
                                    "responseStatus": r.status_code}}
            collection.update_one(link, update_link)
            print(link['link'] + " have respose code other than 200" )
            continue

        
        content_type = r.headers['content-type']

        if 'text/html' in content_type:

            soup = BeautifulSoup(r.content, "html.parser")

            for link_i in soup.findAll('a'):
                href = link_i.get('href')
                
                if href == "" or href == "/" or href is None:
                    continue
                
                abs_url = join_url(link['link'], href)

                now = datetime.now()

                new_entry = {"link": abs_url,
                             "sourceLink": link['link'],
                             "isCrawled": False,
                             "lastCrawlDt": None,
                             "responseStatus": 0,
                             "contentType": "",
                             "contentLength": 0,
                             "filePath": "",
                             "createdAt": datetime.now()}

                collection.insert_one(new_entry)

            filename = get_file_name(content_type)

            open(path + filename, 'wb').write(r.content)
            # save_file(r.text, path + filename)

        else:

            filename = get_file_name(content_type)

            open(path + filename, 'wb').write(r.content)
            # save_file(r.text, path + filename)

        if link['filePath'] != "":
            try:
                os.remove(link['filePath'])
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))

        update_link = {"$set": {"isCrawled": True,
                                "lastCrawlDt": datetime.now(),
                                "responseStatus": r.status_code,
                                "contentType": content_type,
                                "contentLength": len(r.content),
                                "filePath": path + filename}}

        collection.update_one(link, update_link)


    time.sleep(config['sleep_time'])
