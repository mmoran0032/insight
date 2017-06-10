#!/usr/bin/env python3


import os
from pathlib import Path
import requests

from bs4 import BeautifulSoup


def main():
    base = 'http://web.mta.info/developers/'
    page_url = f'{base}turnstile.html'
    links = get_data_urls(page_url)
    create_data_directory()
    download_data(links)


def get_data_urls(url):
    r = requests.get(url)
    assert r.status_code == requests.codes.ok, r.status_code
    soup = BeautifulSoup(r.text, 'html.parser')
    info = soup.find('div', 'span-84')
    links = info.find_all('a')
    targets = [l.get('href') for l in links]
    return [f'{base}{t}' for t in targets]


def create_data_directory(directory='raw_data'):
    try:
        os.mkdir(directory)
    except FileExistsError:
        print(f'directory {directory} already exists...saving in {directory}')


def download_data(data_urls, directory='raw_data'):
    for url in data_urls:
        filename = url.split('/')[-1]
        data = requests.get(url)
        if data.status_code == requests.codes.ok:
            save_file(data, directory, filename)


def save_file(data, directory, filename):
    path = Path(directory) / filename
    with path.open('w') as f:
        f.write(data.text)

