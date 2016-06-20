# -*- coding: utf-8 -*-

'''
Pipelines for
1)  filtering duplicated items
2)  save to csv

Pipelines will be run after default parse function in spider
and process item from it.

'''


from urllib import request, parse
from scrapy.selector import Selector
from scrapy.exceptions import DropItem
from song import settings
from csv import DictWriter
from .useragent import agentslist
import random

import logging


class DuplicatesPipeline(object):
    '''Class for dropping dupllcates
    Its intance will use process_item() to:
    1)  receive the item parsed from response
    2)  pass the item into next pipeline (WriteToCsv) if it
            1. is not duplicate or 2. have more hits than exsiting one
        or drop the item which has lessr hits
    '''
    def __init__(self):
        # keep a dict to record pair: (name of song, singer)
        self._names_seen = {}

    def process_item(self, item, spider):
        name, cur_singer = item['name'], item['singer'].split(',')[0]
        if name not in self._names_seen:
            self._names_seen[name] = cur_singer
            logging.info("{0}'s {1} is added!".format(cur_singer, name))
            return item
        else:
            prev_singer = self._names_seen[name]
            prev_hits, cur_hits = (
                self._get_hits(name, prev_singer),
                self._get_hits(name, cur_singer))
            if cur_hits > prev_hits:
                raise DropItem(
                    "{0}'s {1} is dropped since lesser hits".format(
                        prev_singer, name))

                # update the singer of exsiting song
                self._names_seen[name] = cur_singer
                return item
            else:
                raise DropItem(
                    "{0}'s {1} is dropped since lesser hits".format(
                        cur_singer, name))

    def _get_hits(self, name, singer):
        # A method used to crawl the number of result pages of Google
        query = name + ' ' + singer
        url = "http://www.google.com/search?q=%s" % parse.quote_plus(query)
        req = request.Request(url)

        # choice a useragent from pool to avoid being blocked
        useragent = random.choice(agentslist)
        # print(useragent)
        req.add_header('User-Agent', useragent)
        with request.urlopen(req) as resp:
            body = resp.read()
            raw = Selector(text=body).xpath(
                "//div[@id='resultStats']/text()").extract()
        return int(''.join(raw[0].split()[1].split(',')))


class WriteToCsv(object):
    '''Class for saving item as a row into csv file
    '''
    def __init__(self):
        # A flag for deciding to write csv header or not
        self._first_line = True

    def write_to_csv(self, item):
        fieldnames = [
            'name', 'singer', "lyricist", "composer", "arranger", "lyrics"]
        writer = DictWriter(
            open(settings.csv_file_path, 'a'),
            lineterminator='\n',
            delimiter='\t',
            fieldnames=fieldnames)

        if self._first_line:
            writer.writeheader()
            self._first_line = False
        writer.writerow(item)

    def process_item(self, item, spider):
        self.write_to_csv(item)
        return item
