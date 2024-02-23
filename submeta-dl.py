# Check My Comment

import json
import yt_dlp
import requests
from bs4 import BeautifulSoup
import sys

def getJson(url):
    headers = {
        "User-Agent": 'Mozilla/5.0'#"Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"
    }

    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser")
    data = soup.find(type="application/json")
    for child in data.children:
        # print(json.loads(child.string))
        return json.loads(child.string)

def getCourse(jsonData):
        course = {}
        chapters = jsonData['props']['pageProps']['course']['chapters']
        for chapter in chapters:
            course[chapter['title']] = {}
            for video in chapter['contents']:
                # print(video)
                if video['__typename'] == 'Video':
                    course[chapter['title']][video['title']] = video['id'] # video['videoRef'] not exists
                    # course[chapter['title']][video['title']] = video['videoRef'] 
        
        return course

def downloader(course, args):
    url_prefix = 'https://customer-3j2pofw9vdbl9sfy.cloudflarestream.com/' # This url is not exits check it first
    url_suffix = '/manifest/video.mpd'
    
    for chapter in course:
        for video in course[chapter]:
            video_index = list(course[chapter]).index(video) + 1
            video_title = video
            filename = str(video_index) + '. ' + video_title
            if '/' or '\\' in filename:
                filename = filename.replace('/', '\\')
                filename = filename.replace('/', '\\')
                
            chapter_index = list(course).index(chapter) + 1
            chapter_title = chapter
            download_path = ''
            if len(args) == 3:
                download_path = args[2] + '/'
            filepath = download_path + str(chapter_index) + '. ' + chapter_title

            url = url_prefix + course[chapter][video] + url_suffix

            ydl_opts = {'extract_flat': 'discard_in_playlist',
                     'fragment_retries': 10,
                     'http_headers': {'Referer': 'https://submeta.io'},
                     'external_downloader': {'default': 'aria2c'},
                     'ignoreerrors': 'only_download',
                     'outtmpl': {'default': filename + '.%(ext)s'},
                     'paths': {'home': filepath},
                     'postprocessors': [{'key': 'FFmpegConcat',
                                         'only_multi_video': True,
                                         'when': 'playlist'}],
                     'retries': 10
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

def main(args):
    if len(args) not in [2,3]:
        print('usage: submeta-dl.py <URL> <download path(optional)>')
        return -1
    json = getJson(args[1])
    course = getCourse(json)
    downloader(course, args)
    print("Download complete!")

if __name__ == "__main__":
    main(sys.argv)
