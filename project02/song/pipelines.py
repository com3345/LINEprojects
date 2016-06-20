# -*- coding: utf-8 -*-

from urllib import request, parse
from scrapy.selector import Selector
from scrapy.exceptions import DropItem
from song import settings
from csv import DictWriter

import logging


class DuplicatesPipeline(object):

    def __init__(self):
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
                self._names_seen[name] = cur_singer
                return item
            else:
                raise DropItem(
                    "{0}'s {1} is dropped since lesser hits".format(
                        cur_singer, name))

    def _get_hits(self, name, singer):
        query = name + ' ' + singer
        url = "http://www.google.com/search?q=%s" % parse.quote_plus(query)
        req = request.Request(url)
        req.add_header('User-Agent', "Mozilla/5.0")
        with request.urlopen(req) as resp:
            body = resp.read()
            raw = Selector(text=body).xpath(
                "//div[@id='resultStats']/text()").extract()

        return int(''.join(raw[0].split()[1].split(',')))


class WriteToCsv(object):
    def __init__(self):
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
