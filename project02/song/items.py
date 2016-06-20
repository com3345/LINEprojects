# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class SongItem(scrapy.Item):
    name = scrapy.Field()
    singer = scrapy.Field()
    lyricist = scrapy.Field()
    composer = scrapy.Field()
    arranger = scrapy.Field()
    lyrics = scrapy.Field()
    # hits = scrapy.Field()
