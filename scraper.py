# -*- coding: utf-8 -*-
import json
import re
import requests
from bs4 import BeautifulSoup
from argparse import ArgumentParser


class InstagramEntry:
    def __init__(self, edge):
        self.edge = edge

    def text(self):
        return self.edge['node']['edge_media_to_caption']['edges'][0]['node']['text'].replace('\n', '')

    def photo_url(self):
        return self.edge['node']['display_url']

    def like_count(self):
        return int(self.edge['node']['edge_liked_by']['count'])


def show_instagram_entry(entry):
    print('text: ', entry.text())
    print('photo_url: ', entry.photo_url())
    print('like_count: ', entry.like_count())
    print()


def get_user_entries(user_name):
    url = 'https://www.instagram.com/{}/'.format(user_name)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html5lib')
    js = soup.find("script", text=re.compile("window._sharedData")).text
    data = js[js.find("{"):js.rfind("}")+1]
    try:
        edges = json.loads(data)['entry_data']['ProfilePage'][0]['graphql']['user']['edge_owner_to_timeline_media']['edges']
    except KeyError:
        raise KeyError('user_nameが見つかりません.')
    return [InstagramEntry(edge) for edge in edges if not edge['node']['is_video']]


def get_tag_entries(tag):
    url = 'https://www.instagram.com/explore/tags/{}/'.format(tag)
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'html5lib')
    js = soup.find("script", text=re.compile("window._sharedData")).text
    data = js[js.find("{"):js.rfind("}")+1]
    try:
        edges = json.loads(data)['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
    except KeyError:
        raise KeyError('タグが見つかりません.')
    return [InstagramEntry(edge) for edge in edges if not edge['node']['is_video']]


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('--user_name', nargs='?', type=str, help='user_nameを指定して画像をスクレイプ')
    parser.add_argument('--tag', nargs='?', type=str, help='ハッシュタグを指定して画像をスクレイプ')
    args = parser.parse_args()
    if args.user_name:
        entries = get_user_entries(args.user_name)
        for entry in entries:
            show_instagram_entry(entry)
    if args.tag:
        entries = get_tag_entries(args.tag)
        for entry in entries:
            show_instagram_entry(entry)
    if not args.user_name and not args.tag:
        print('try \'python scraper.py --help\'.')

