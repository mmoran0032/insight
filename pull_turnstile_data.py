#!/usr/bin/env python3


import os
from pathlib import Path
import requests

from bs4 import BeautifulSoup


def main():
    page_url = r'http://web.mta.info/developers/turnstile.html'
    data_base_url = r'http://web.mta.info/developers/data/nyct/turnstile/'
    filenames = get_data_filenames(page_url)
    filenames = keep_undownloaded_files(filenames)
    urls = generate_file_urls(filenames, data_base_url)
    download_data(urls, filenames)


def get_data_filenames(url):
    r = requests.get(url)
    assert r.status_code == requests.codes.ok, r.status_code
    links = find_links_on_page(r)
    return reduce_to_filenames(links)


def find_links_on_page(request_obj):
    soup = BeautifulSoup(request_obj.text, 'html.parser')
    info = soup.find('div', 'span-84')
    links = info.find_all('a')
    return [link.get('href') for link in links]


def reduce_to_filenames(links):
    paths = [Path(link) for link in links]
    return [path.parts[-1] for path in paths]


def keep_undownloaded_files(filenames):
    downloaded = os.listdir('raw_data')
    return list(filter(lambda x: x not in downloaded, filenames))


def generate_file_urls(filenames, base_url):
    return [f'{base_url}{filename}' for filename in filenames]


def download_data(data_urls, filenames):
    for url, filename in zip(data_urls, filenames):
        data = requests.get(url)
        if data.status_code == requests.codes.ok:
            save_file(data, filename)


def save_file(data, filename):
    path = Path('raw_data') / filename
    with path.open('w') as f:
        print(f'saving {filename}')
        f.write(data.text)


if __name__ == '__main__':
    main()
