# -*- coding: utf-8 -*-
import scrapy, json, sys, codecs, datetime, os, urllib2, re
from bs4 import BeautifulSoup

CITY = "philadelphia"
DATA_URL = "https://www.cs.drexel.edu/~amg463/craigslist"

def open_json(url_suffix):
    try:
        response = urllib2.urlopen("{}/{}/{}".format(DATA_URL,CITY,url_suffix));
        data = json.loads(response.read())
        return data
    except:
        raise Exception("Error fetching JSON: {}".format(sys.exc_info()))

def generateURLs():
    urls = []
    sections = open_json('sections.json')
    zipcodes = open_json('zips.json')['zipcodes']
    for section in sections:
        for subsection in sections[section].values():
            for zipcode in zipcodes:
                urls.append('https://{}.craigslist.org/search/{}?search_distance=0&postal={}&format=rss'.format(CITY,subsection,zipcode))
    return urls

def createRecord(section, listing, zipcode):
    record = {'section':section}
    record['zipcode'] = zipcode
    record['url'] = listing.find("link").string
    raw_title = listing.find("title").string
    record['raw_title'] = raw_title

    price_split = raw_title.split('&#x0024;')
    title = price_split[0].strip()
    record['title'] = title
    #if has price
    if len(price_split) > 1:
        specs = price_split[1].strip()
        groups = re.search('(\d+)\s?(?:(\d+)bd)*\s?(?:(\d+)ft)*',specs)
        record['price'] = groups.group(1) or None
        record['beds'] = groups.group(2) or None
        record['area'] = groups.group(3) or None

    with_loc = re.search('(.+)\(([^(]+)\)$', title)
    record['loc'] = None
    if with_loc:
        record['title'] = with_loc.group(1).strip()
        record['loc'] = with_loc.group(2)

    record['desc'] = listing.find("description").string
    record['timestamp'] = listing.find("date").string
    record['has_image'] = True if listing.find("enclosure") else False
    return record

class CLSpider(scrapy.Spider):
    name = "clspider"
    start_urls = generateURLs()

    def parse(self, response):
        now = datetime.datetime.now()
        section = response.url.split("?")[0][-3:]
        zipcode = response.url.split("=")[2][0:5]
        #dest = "raw/{}/{}".format(section, zipcode) + now.strftime('/%Y-%m-%d/%H_%M.xml')
        parsed = BeautifulSoup(response.body, "xml", from_encoding='utf-8')
        listings = parsed.findAll("item")
        for listing in listings:
            yield createRecord(section,listing,zipcode)
