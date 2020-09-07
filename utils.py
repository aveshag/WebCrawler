from urllib.request import urlparse, urljoin
import random
import string


def save_file(response_byte, filepath):
    f = open(filepath, 'w+')
    f.write(response_byte)


def mark_link_crawled(collection, link, now, status_code):
    update = {"$set": {"isCrawled": 'true',
                       "lastCrawlDt": now, "responseStatus": status_code}}
    collection.update_one(link, update)


def get_file_name(content_type):

    letters_and_digits = string.ascii_letters + string.digits
    rand_name = ''.join((random.choice(letters_and_digits) for i in range(10)))

    extension = ''

    extension_lst = ['.css', '.csv', '.doc', '.gif', '.html', '.jpg', 'js',
                     'json', '.mp3', '.mpeg', '.png', '.pdf', '.ppt', '.sh',
                     '.tar', '.txt', '.zip', '.3gp', '.3gp']

    content_type_lst = ['text/css', 'text/csv', 'application/msword', 'image/gif',
                        'text/html', 'image/jpeg', 'text/javascript', 'application/json'
                        'audio/mpeg', 'video/mpeg', 'image/png', 'application/pdf',
                        'application/vnd.ms-powerpoint', 'application/x-sh', 'application/x-tar',
                        'text/plain', 'application/zip', 'video/3gpp', 'audio/3gpp']

    for i in range(len(extension_lst)):
        if content_type_lst[i] in content_type:
            extension = extension_lst[i]
            break

    return rand_name + extension


def join_url(base, url):
    return urljoin(base, url)


def is_valid(url):
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)
