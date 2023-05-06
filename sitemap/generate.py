import xml.etree.ElementTree as ET
import os
import datetime
import logging
import requests
import boto3
import urllib.parse

logging.basicConfig(level=logging.DEBUG)

os.makedirs('generate_sitemap', exist_ok=True)

API_URL = os.environ.get('API_URL')
CLIENT_URL = os.environ.get('CLIENT_URL')

# Wasabi connection info
S3_BUCKET = os.environ.get('S3_BUCKET')
S3_DIR = os.environ.get('S3_DIR')
REGION_NAME = os.environ.get('REGION_NAME')
ACCESS_KEY = os.environ.get('ACCESS_KEY')
SECRET_ACCESS_KEY = os.environ.get('SECRET_ACCESS_KEY')

SITEMAP_CONTENT_PATH = ['/works', '/users']
SITEMAP_CONTENT_API_PATH = {'/works': '/works?limit=9999', '/users': '/users'}

dt_now = datetime.datetime.utcnow()


def getDate():
    logging.debug(dt_now)
    date = str(dt_now.year) + str(dt_now.month).zfill(2) + \
        str(dt_now.day).zfill(2)
    logging.debug(date)
    return date


GENERATE_XML_PATH = f'./generate_sitemap/sitemap_{getDate()}.xml'


def apiClient(path: str):
    res = requests.get(f'{API_URL}{SITEMAP_CONTENT_API_PATH[path]}')

    logging.debug(res)

    res.raise_for_status()
    res_json = res.json()

    return res_json


def _addWorks(url_element: ET.Element, item):
    for asset in item['assets']:
        if asset['asset_type'] == 'image':
            image = ET.SubElement(url_element, 'image:image')
            image_loc = ET.SubElement(image, 'image:loc')
            image_loc.text = asset['url']

        elif asset['asset_type'] == 'video':
            video = ET.SubElement(url_element, 'video:video')

            video_title = ET.SubElement(video, 'video:title')
            video_title.text = item['title']

            video_description = ET.SubElement(
                video, 'video:description')
            item_description = item['description']
            if len(item_description) > 2045:
                item_description = item_description[0:2045] + '...'
            video_description.text = item_description

            video_thumbnail_loc = ET.SubElement(video, 'video:thumbnail_loc')
            video_thumbnail_loc.text = item['thumbnail']['url']

            video_content_loc = ET.SubElement(
                video, 'video:content_loc')
            video_content_loc.text = asset['url']

            video_publication_date = ET.SubElement(
                video, 'video:publication_date')
            video_publication_date.text = asset['created_at']
            video_uploader = ET.SubElement(
                video, 'video:uploader')
            video_uploader.set(
                'info', f"{CLIENT_URL}/users/{item['user']['id']}")
            video_uploader.text = item['user']['name']

            for tag in item['tags']:
                video_tag = ET.SubElement(video, 'video:tag')
                video_tag.text = tag['name']


def _addUsers(url_element: ET.Element, item):
    image = ET.SubElement(url_element, 'image:image')
    image_loc = ET.SubElement(image, 'image:loc')
    image_loc.text = item['avatar_url']


def addUrlsToXml(urlset: ET.Element):
    for path in SITEMAP_CONTENT_PATH:
        try:
            res = apiClient(path)

            logging.info(f'path: {path} -> OK')

            for item in res:
                url_element = ET.SubElement(urlset, 'url')
                loc = ET.SubElement(url_element, 'loc')
                lastmod = ET.SubElement(url_element, 'lastmod')
                changefreq = ET.SubElement(url_element, 'changefreq')
                changefreq.text = 'daily'
                lastmod.text = item["updated_at"]+'Z'
                loc.text = f'{CLIENT_URL}{path}/{item["id"]}'
                match path:
                    case '/works':
                        _addWorks(url_element, item)
                    case '/users':
                        _addUsers(url_element, item)

        except requests.HTTPError:
            logging.info(f'path: {path} -> NO')
            continue


def generateXml():
    logging.info('Start generate')

    urlset = ET.Element('urlset')
    urlset.set("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    urlset.set("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")
    urlset.set("xmlns:video", "http://www.google.com/schemas/sitemap-video/1.1")

    tree = ET.ElementTree(element=urlset)
    url_element = ET.SubElement(urlset, 'url')
    loc = ET.SubElement(url_element, 'loc')
    changefreq = ET.SubElement(url_element, 'changefreq')
    changefreq.text = 'daily'
    loc.text = f'{CLIENT_URL}'

    addUrlsToXml(urlset)
    tree.write(
        GENERATE_XML_PATH, encoding='utf-8', xml_declaration=True)

    logging.info('Success generate')


def uploadSitemap():
    logging.info('Uploading ...')
    wasabi = boto3.client("s3", endpoint_url=f"https://s3.{REGION_NAME}.wasabisys.com",
                          aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_ACCESS_KEY)
    wasabi.upload_file(GENERATE_XML_PATH, S3_BUCKET,
                       f"{S3_DIR}/sitemap.xml", ExtraArgs={"ContentType": "application/xml"})
    # wasabi.upload_file(GENERATE_XML_PATH, S3_BUCKET, f"{S3_DIR}/sitemap.xml")
    logging.info('Success uploading')


if __name__ == '__main__':
    logging.info('Start job')
    generateXml()
    uploadSitemap()
    logging.info('End job')
