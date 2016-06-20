import scrapy
import MeCab
from song.items import SongItem
import logging


class KasiTimeSpider(scrapy.Spider):

    name = "kasitime"
    MAX_PAGES = 79082

    def __init__(self, n_pages=MAX_PAGES, *args, **kwargs):
        super(KasiTimeSpider, self).__init__(*args, **kwargs)
        self.start_urls = (
            "http://www.kasi-time.com/item-{0}.html".format(str(i))
            for i in range(1, int(n_pages) + 1))
        self._set_xpath_and_regex()
        self._mt = MeCab.Tagger()

    def _set_xpath_and_regex(self):
        self._r, desc_ = {}, ['singer', 'lyricist', 'composer', 'arranger']
        for i, key in enumerate(desc_, 1):
            self._r[key] = (
                "//div[@class='person_list']/table/tr[{0}]//a/text()".format(i),
                r"[^\t\n]{1,}")
        self._r['name'] = ("//h1/text()", '^.+ ')
        self._r['lyrics'] = ("//script/text()", "lyrics\s=\s'(.+)'")

    def _not_in_dict(self, word):
        return len(self._mt.parse(word).splitlines()) > 2

    def parse(self, response):
        word = response.xpath(
            self._r['name'][0]).re(self._r['name'][1])[0].strip()
        if self._not_in_dict(word):
            logging.info('{0} is not in neologd'.format(word))
            return
        item = SongItem()
        for key in self._r:
            values = response.xpath(self._r[key][0]).re(self._r[key][1])
            if key == 'name':
                item[key] = values[0].strip()
            else:
                item[key] = ','.join([value.strip() for value in values])
        return item
