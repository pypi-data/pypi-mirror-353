# Support for direct script execution
# This is a workaround for running the script directly without installing it as a package.
if __name__ == "__main__" and __package__ is None:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + "/.."))

# End of workaround

import argparse
import json
import requests
import sys
import time
import tomllib
from dataclasses import dataclass
from html.parser import HTMLParser
from importlib.resources import files
from io import BytesIO
from jinja2 import Environment, FileSystemLoader
from os import getenv, makedirs, symlink, link
from os.path import basename, isfile, splitext
from platformdirs import user_config_dir
from random import randbytes
from shutil import copyfileobj, move
from torf import Torrent
from urllib.parse import quote, urljoin
from vcsi import vcsi
from clips2share import qbittorrent_client
from pathlib import Path

@dataclass
class Tracker:
    name: str
    announce_url: str
    category: str
    source_tag: str

@dataclass
class C4SData:
    title: str
    studio: str
    price: str
    date: str
    duration: str
    size: str
    format: str
    resolution: str
    description: str
    category: str
    related_categories: list[str]
    keywords: list[str]
    url: str
    image_url: str

class HTMLFilter(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text = ''

    def handle_data(self, data):
        self.text += data

    def handle_starttag(self, tag, attrs):
        if tag == 'br':
            self.text += '\n'
        if tag == 'p':
            self.text += '\n'

def html2text(html):
    filter = HTMLFilter()
    filter.feed(html)
    return filter.text

DECODER = json.JSONDecoder()

def extract_clip_data(url: str) -> C4SData:
    api_url = urljoin(url, '?_data=routes%2F%28%24lang%29.studio.%24id_.%24clipId.%24clipSlug')
    response = requests.get(api_url, timeout=10)
    response.raise_for_status()
    obj, _ = DECODER.raw_decode(response.text)
    clip = obj['clip']
    title = clip['title']
    studio = clip['studioTitle']
    price = clip['price']
    date = clip['dateDisplay'].split(' ')[0] #no split would also give you the timestamp
    duration = clip['duration']
    size = clip['size_mb']
    format = clip['format']
    resolution = clip['resolution']
    description = html2text(clip['description_sanitized'])
    category = clip['category_name']
    related_categories = []
    keywords = []

    if 'related_category_links' in clip:
        related_category_links = clip['related_category_links']
        related_categories = [category['category'] for category in related_category_links]

    if 'keyword_links' in clip:
        keyword_links = clip['keyword_links']
        keywords = [keyword['keyword'] for keyword in keyword_links]

    image_url = clip['cdn_previewlg_link']

    return C4SData(
        title=title,
        studio=studio,
        price=price,
        date=date,
        duration=duration,
        size=size,
        format=format,
        resolution=resolution,
        description=html2text(description),
        category=category,
        related_categories=related_categories,
        keywords=keywords,
        url=url,
        image_url=image_url
    )

def chevereto_image_upload(img_path, chevereto_host, chevereto_api_key):
    """
    Uploads an image to given chevereto instance and returns the image url on success
    """

    def make_it_unique(input, output):
        copyfileobj(input, output)
        output.write(randbytes(16))
        return output

    headers = {'X-API-Key': chevereto_api_key}

    with open(img_path, 'rb') as f:
        output_buffer = BytesIO()
        unique_buffer = make_it_unique(f, output_buffer)
        unique_buffer.seek(0)
        file = {'source': (basename(img_path), unique_buffer)}
        r = requests.post(f'https://{chevereto_host}/api/1/upload', headers=headers, timeout=10, files=file)

    if r.json()['status_code'] == 200:
        return r.json()['image']['url']
    else:
        raise RuntimeError(r.json())

def format_tags_with_dots(source_list):
    return [s.replace(' ', '.') for s in source_list]

def print_torrent_hash_process(torrent, filepath, pieces_done, pieces_total):
    print(f'[{filepath}] {pieces_done/pieces_total*100:3.0f} % done')

def get_font_path():
    return str(files('clips2share') / 'fonts')

def parse_arguments():
    parser = argparse.ArgumentParser(description="clips2share CLI")
    parser.add_argument('-V', '--video', type=str, help="Path to the video file")
    parser.add_argument('-u', '--url', type=str, help="Clip Store URL")
    parser.add_argument('-D', '--delay-seconds', type=int, help="Auto-continue delay in seconds after torrent is created")
    return parser.parse_args()

def main():
    args = parse_arguments()
    config_path = getenv('C2S_CONFIG_PATH') if getenv('C2S_CONFIG_PATH') else user_config_dir(appname='clips2share') + '/config.toml'
    if not isfile(config_path):
        print(f'config_path {config_path} does not exist, download example config here: '
              f'https://codeberg.org/c2s/clips2share/src/branch/main/config.toml.example '
              f'change to your needs and run again!')
        sys.exit(1)
    with open(config_path, 'rb') as f:
        toml_data = tomllib.load(f)

    torrent_temp_dir = toml_data['torrent']['temporary_directory']
    upload_dir = toml_data['client']['qbittorrent']['upload_directory']
    qbittorrent_watch_dir = toml_data['client']['qbittorrent']['watch_directory']
    static_tags = toml_data['torrent']['static_tags']
    delayed_seed = toml_data['client']['qbittorrent']['delayed_seed']
    use_hardlinks = toml_data['torrent'].get('use_hardlinks', False)  # Default to False if not present

    chevereto_api_key = toml_data['image_host']['chevereto']['api_key']
    chevereto_host = toml_data['image_host']['chevereto']['host']

    use_qb_api = toml_data['client']['qbittorrent']['use_api']
    qb_url = toml_data['client']['qbittorrent']['url']
    qb_category = toml_data['client']['qbittorrent']['category']

    if use_qb_api:
        qbt_client = qbittorrent_client.QBittorrentClient(qb_url)

    if "trackers" in toml_data:
        trackers = [ Tracker(**t) for t in toml_data.get('trackers', [])]
    print(trackers) # TODO: Is there a better way to show this information to the user?

    video_path = args.video if args.video else input("Video Path: ")
    video_basename = basename(video_path)
    video_clipname = splitext(video_basename)[0]
    print(f'https://www.clips4sale.com/clips/search/{quote(video_clipname)}/category/0/storesPage/1/clipsPage/1')
    c4s_url = args.url if args.url else input("C4S Url: ")

    if not isfile(video_path):
        print('Video file does not exists: ', video_path)
        sys.exit(2)

    clip = extract_clip_data(c4s_url)
    print(clip)

    target_dir = upload_dir + f'{clip.studio} - {clip.title}'

    # Create dir structure
    makedirs(target_dir + '/images')

    target_file_path = f'{target_dir}/{clip.studio} - {clip.title}{splitext(video_path)[1]}'

    # Create hardlink or symlink to video file in upload dir
    if use_hardlinks:
        print(f"Creating hardlink: {target_file_path}")
        link(src=video_path, dst=target_file_path)
    else:
        print(f"Creating symlink: {target_file_path}")
        symlink(src=video_path, dst=target_file_path)

    # Download Header Image from C4S
    r = requests.get(clip.image_url, timeout=10)
    r.raise_for_status()
    with open(target_dir + '/images/header.jpg', 'wb') as header:
        header.write(r.content)

    # Upload header image
    header_image_link = chevereto_image_upload(target_dir + '/images/header.jpg', chevereto_host=chevereto_host, chevereto_api_key=chevereto_api_key)

    # Create Thumbnail Image (using default vcsi parameters copied from interactive debug run)
    vcsi_args = argparse.Namespace(output_path=target_dir + '/images/thumbnail.jpg', config=None,
                              start_delay_percent=7,
                              end_delay_percent=7, delay_percent=None, grid_spacing=None, grid_horizontal_spacing=5,
                              grid_vertical_spacing=5, vcs_width=1500, grid=vcsi.Grid(x=4, y=4), num_samples=None,
                              show_timestamp=True, metadata_font_size=16,
                              metadata_font=get_font_path() + '/DejaVuSans-Bold.ttf', timestamp_font_size=12,
                              timestamp_font=get_font_path() + '/DejaVuSans.ttf', metadata_position='top',
                              background_color=vcsi.Color(r=0, g=0, b=0, a=255),
                              metadata_font_color=vcsi.Color(r=255, g=255, b=255, a=255),
                              timestamp_font_color=vcsi.Color(r=255, g=255, b=255, a=255),
                              timestamp_background_color=vcsi.Color(r=0, g=0, b=0, a=170),
                              timestamp_border_color=vcsi.Color(r=0, g=0, b=0, a=255), metadata_template_path=None,
                              manual_timestamps=None, is_verbose=False, is_accurate=False, accurate_delay_seconds=1,
                              metadata_margin=10, metadata_horizontal_margin=10, metadata_vertical_margin=10,
                              timestamp_horizontal_padding=3, timestamp_vertical_padding=3,
                              timestamp_horizontal_margin=5, timestamp_vertical_margin=5, image_quality=100,
                              image_format='jpg', recursive=False, timestamp_border_mode=False,
                              timestamp_border_size=1,
                              capture_alpha=255, list_template_attributes=False, frame_type=None, interval=None,
                              ignore_errors=False, no_overwrite=False, exclude_extensions=[], fast=False,
                              thumbnail_output_path=None, actual_size=False, timestamp_format='{TIME}',
                              timestamp_position=vcsi.TimestampPosition.se)
    vcsi.process_file(f'{target_dir}/{clip.studio} - {clip.title}{splitext(video_path)[1]}', args=vcsi_args)
    thumbnail_image_link = chevereto_image_upload(target_dir + '/images/thumbnail.jpg', chevereto_host=chevereto_host, chevereto_api_key=chevereto_api_key)

    script_dir = Path(__file__).resolve().parent
    template_dir = script_dir / 'templates'

    jinja_env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True)

    t = Torrent(path=target_dir)
    t.private = True
    t._metainfo['metadata'] = dict()
    t._metainfo['metadata']['title'] = f'{clip.studio} - {clip.title}'
    t._metainfo['metadata']['cover url'] = header_image_link
    t._metainfo['metadata']['taglist'] = format_tags_with_dots(clip.keywords + static_tags)
    template = jinja_env.get_template('default_bbcode.jinja')
    t._metainfo['metadata']['description'] = template.render(
        clip=clip,
        header_image_link=header_image_link,
        thumbnail_image_link=thumbnail_image_link,
    )
    print("BBCode:\n-----TORRENT DESCRIPTION-----\n" + t._metainfo['metadata']['description'] + "\n-----DESCRIPTION END-----\n")

    t.generate(callback=print_torrent_hash_process, interval=1)

    # Create Torrents
    for tracker in trackers:
        t.trackers = tracker.announce_url
        t.source = tracker.source_tag

        # TODO: category is not working, this is probably unsupported on luminance currently?
        t._metainfo['metadata']['category'] = tracker.category

        print(f'creating torrent for {tracker.source_tag}... {t}')

        t.write(f'{torrent_temp_dir}[{tracker.source_tag}]{clip.studio} - {clip.title}.torrent')
        if delayed_seed:
            if args.delay_seconds:
                print(f'Upload torrent to tracker {tracker.source_tag}. Waiting {args.delay_seconds} seconds before autoloading to qBittorrent...')
                time.sleep(args.delay_seconds)
            else:
                input(f'Upload torrent to tracker {tracker.source_tag}, then hit Enter to autoload to qBittorrent...')

        torrent_filename = f'[{tracker.source_tag}]{clip.studio} - {clip.title}.torrent'
        torrent_path = f'{torrent_temp_dir}{torrent_filename}'

        if use_qb_api:
            print(f"Uploading {torrent_filename} via qBittorrent API...")
            torrent_name = f'{clip.studio} - {clip.title}'
            try:
                with open(torrent_path, 'rb') as f:
                    torrent_bytes = f.read()
                qbt_client.send_torrent(
                    torrent_bytes=torrent_bytes,
                    name=torrent_name,
                    category=qb_category,
                    savepath=upload_dir,
                )
                print("API Upload successful.")
                # Clean up the temporary torrent file after successful upload
                try:
                    os.remove(torrent_path)
                except OSError as e:
                    print(f"Error removing temp torrent {torrent_path}: {e}")
            except Exception as e:
                print("API upload failed:", e)
                sys.exit(3)
        else:
            watch_target = f'{qbittorrent_watch_dir}{torrent_filename}'
            print(f"Using watch folder: {watch_target}")
            move(torrent_path, watch_target)

        t.trackers.clear()
        t.source = None
        print('done...')


if __name__ == "__main__":
    main()
