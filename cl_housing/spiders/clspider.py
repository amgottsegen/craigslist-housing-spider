# -*- coding: utf-8 -*-
import scrapy, json, sys, codecs, datetime, os

CITY = "philadelphia"

def generateURLs():
    urls = []
    sections = json.loads(open('sections.json').read())
    zipcodes = json.loads(open('zips.json').read())['zipcodes']
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
            print "Error saving XML for section {}: {}. Continuing...".format(section, sys.exc_info()[0])
            pass
