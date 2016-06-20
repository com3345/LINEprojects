# -*- coding: utf-8 -*-


import scrapy


# Built-in implementation of ORM
class SongItem(scrapy.Item):
    name = scrapy.Field()
    singer = scrapy.Field()
    lyricist = scrapy.Field()
    composer = scrapy.Field()
    arranger = scrapy.Field()
    lyrics = scrapy.Field()
    # hits = scrapy.Field()
