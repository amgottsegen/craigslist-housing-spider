# -*- coding: utf-8 -*-
import scrapy, json, sys, codecs, datetime, os

CITY = "philadelphia"

def open_json(filename):
    try:
	       data = open(filename).read()
	          return json.loads(data)
    except:
	       raise Exception("Error reading craigslist sections JSON: %s" % sys.exc_info())

def generateURLs():
    urls = []
    sections = open_json('sections.json')
    zipcodes = open_json('zips.json')['zipcodes']
    for section in sections:
        for subsection in sections[section].values():
	           for zipcode in zipcodes:
                   urls.append('https://{}.craigslist.org/search/{}?search_distance=0&postal={}&format=rss'.format(CITY,section,zipcode))
    return urls

class CLSpider(scrapy.Spider):
    name = "clspider"
    start_urls = generateURLs()

    def parse(self, response):
        now = datetime.datetime.now()
        section = response.url.split("?")[0][-3:]
        zipcode = response.url.split("=")[2][0:5]
        dest = "raw/{}/{}".format(subsection, zipcode) + now.strftime('/%Y-%m-%d/%H_%M.xml')
        try:
            os.makedirs(os.path.dirname(dest))
        except:
            pass

        try:
            f = codecs.open(dest,'w')
            f.write(result)
            self.log('Saved file %s' % filename)
        except:
            print ("Error saving XML for section %s: %s. Continuing...") % (section, sys.exc_info()[0])
            pass
