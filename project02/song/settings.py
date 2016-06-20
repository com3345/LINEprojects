# -*- coding: utf-8 -*-

'''
settings for spider
'''

BOT_NAME = 'song'

SPIDER_MODULES = ['song.spiders']
NEWSPIDER_MODULE = 'song.spiders'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

ITEM_PIPELINES = {
    'song.pipelines.DuplicatesPipeline': 300,
    'song.pipelines.WriteToCsv': 400,
}
csv_file_path = 'test.csv'
