import os
import re
import sys
import time
#import asyncio
import requests
from clint.textui import progress
from bs4 import BeautifulSoup

def banner():
    # App banner
    banner_ascii = """
  ____                                 ____ _____ _____ 
 / ___|___  _   _ _ __ ___  ___       / ___| ____|_   _|
| |   / _ \| | | | '__/ __|/ _ \_____| |  _|  _|   | |  
| |__| (_) | |_| | |  \__ \  __/_____| |_| | |___  | |  
 \____\___/ \__,_|_|  |___/\___|      \____|_____| |_|  
                                                        
"""

    return banner_ascii
'''
def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f, *args, **kwargs)
    return wrapped
'''


class BadLinkException(Exception):
    def __init__(self, ok):
        self.ok = ok

def make_directory(course_name):
    # create folder to store anime
    if not os.path.exists(course_name):
        os.mkdir(course_name)

def clear_tmp(directory):
    # clear tmp files
    for i in os.listdir(directory):
        if i[-3:] == "tmp":
            os.remove(os.path.join(directory, i))

def name_parser(name):
    #https://downloadly.net/?s=figma%20professional
    #split the name spaces with the %20 
    new_name =  name.replace(' ', '%20')
    return new_name
#above solved 

def get_course_result(search_item):
    #this function scrapes the first layer of the website and gets all courses 
    #related to the search term, while showiung the user the number of courses on that search key

    search_url = "https://downloadly.net/?s="  + search_item
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    search_result = []
    response = requests.get(search_url, headers=headers)
    #time.sleep(2)
    soup = BeautifulSoup(response.text, 'lxml')
    item_body = soup.findAll('div', {'class':'w-post-elm post_image usg_post_image_1 stretched'})

    for i in item_body:
        #print(i.find('a')['href'])
        #print(i.find('a')['aria-label'])
        search_result.append({
            'Title': i.find('a')['aria-label'],
            'link': i.find('a')['href']})
    #for i in range(len(search_result)):
        #print(f'{i+1}. {search_result[i]["Title"]}')
    
    

    return search_result
#print(banner())
#print(get_course_result()[1]['link'])

def download_link(choice):

    search_url =  str(choice)   #get_course_result()[choice]['link'])  # + search_item
    #'https://downloadly.net/2021/26/61819/12/become-a-ux-designer/19/'
     #actual link
     #https://downloadly.net/2022/05/66873/02/complete-web-design-from-figma-to-webflow-to-freelancing-2/16/?#/66873-udemy-012207052611.html
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    search_result = []
    response = requests.get(search_url, headers=headers)
    time.sleep(2)

    soup = BeautifulSoup(response.text, 'lxml')
    item_body = [tag['href'] for tag in soup.select('p a[href]')] #soup.findAll('div', {'class':'wp-video'})
    #lll = 

    for i in item_body:
        if i[-4:] == '.rar':
            search_result.append({
                'link': i})

    return search_result

#print(download_link())

#@background
def download_file(course_name, download_url):

    # download anime and store in the folder the same name
    # don't download files that exist and clear tmp files after download
    filename = os.path.basename(download_url)
    download_path = os.path.join(course_name, filename)
    if not os.path.exists(download_path):
        # Due to the existence of multiple streams of download
        # we prepare a download url with i as subdomain index variant
        _url = download_url
        print("\nTrying " + _url + " ...")

        #def download(url, fn):
            #r = requests.get(_url)
            #with open(str(fn), "wb") as f:
                 #f.write(r.content)

        try:
            # send a download request with current url
            r = requests.get(_url, stream=True)

            print('Gotten Verified Download link!')
            print("Downloading", name_parser(filename))

            # download if response of download url request is ok
            with open(download_path, 'wb') as out:
                total_length = int(r.headers.get('content-length'))
                for chunk in progress.bar(r.iter_content(chunk_size=1024), expected_size=(total_length/1024) + 1):
                    if chunk:
                        out.write(chunk)
                        out.flush()

            clear_tmp(course_name)
        except BadLinkException as e:
            print(e)

def get_user_choice(cap):
    LIST_OF_ALLOWED_DIGITS = [d for d in "0123456789"]
    choice = input("\nWhich one? Enter the number of your choice ::: ")

    # ensure choice is not empty
    if len(choice) == 0:
        return get_user_choice(cap)

    # separate each digit of the choice string
    digits = [c for c in choice]

    # look for any element that isn't a digit
    for digit in digits:
        if digit not in LIST_OF_ALLOWED_DIGITS:
            print("Your input is invalid! pick another number")
            return get_user_choice(cap)
    
    if int(choice) > cap or int(choice) == 0:
        print("Your input is invalid! pick another number")
        return get_user_choice(cap)
    
    return abs(int(
        choice))

if __name__ == "__main__":
    print(banner())
    print("\nAll Courses are gotten from https://downloadly.net/")
    print('File password (s) is: www.downloadly.ir')

    course_name = input("\nWhat course do you wanna download today ::: ")

    c_name = name_parser(course_name)

    search_result = get_course_result(c_name)

    if len(search_result) == 0:
        print(
            "We couldn't find the course you searched for, check the spelling and try again")
        exit()

    print("\nSearch results for", course_name)

    for i, j in enumerate(search_result):
        print(i + 1, " - " + j["Title"])

    choice = get_user_choice( len(search_result) )

    course = search_result[choice - 1]

    #this would return direct downloafd links to the .rar file 
    chosen_course = download_link(course["link"]) 

    make_directory(course["Title"])
    print("\nPress CTRL + C to cancel your download at any time")

    try:
        print("Aye aye captain, downloading about to begin, hit CTRL + C to cancel anytime")
        start = time.perf_counter()

        for i in chosen_course:
            
            download_file(course["Title"], i['link'])
        end = time.perf_counter()
        print(f'\ncompleted download in {int(end-start)} seconds')
        print("\nFinished downloading all .rar files of ", course["Title"])
    except Exception as e:
        print(e)