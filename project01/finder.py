#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Read words from wiki dumps data 
(https://dumps.wikimedia.org/jawiki/latest/)
Save the word which is not in the mecab-ipadic-neologd
 and its yomi to txt file 
(https://github.com/neologd/mecab-ipadic-neologd)
'''

__author__ = 'Spike'

from collections import deque
import MeCab

class newWordFinder(object):
    """Class used to find a new word and save it to file:

    Usage:
        if newWordFinder.is_new_word(word):
            newWordFinder.save('somefile.txt')

        The attr 'window_size'
        sets the length of a double-ended queue, which maintains the 
        lastest k words before the current word, inorder to prevent
        from adding duplicates into files.
            e.x:
            ->  Bye-Bye
                Bye-Bye_(ブラックビスケッツの曲)
                Bye-Bye_(光GENJIの曲)
                Bye-Bye_(島谷ひとみの曲)
                Bye-Bye×Hello
                Bye-bye_circus
            ->  Bye_Bye
                Bye_Bye_(アルバム)
                Bye_Bye_(風の曲)
    
    Example:
        >>> nwf = newWordFinder()
        >>> filename = 'test.txt'
        >>> word = '桜流し'
        >>> if nwf.is_new_word(word): nwf.save2file(filename)
        >>> word = '辞書にあるわけない単語'
        >>> if nwf.is_new_word(word): nwf.save2file(filename)
        A new word:'辞書にあるわけない単語' added!
    """
    def __init__(self, window_size=10):
        self._tagger = MeCab.Tagger('-Ochasen')
        self._window_size = window_size
        self._preword = ''
        self._curword = ''
        self._q = deque()

    def is_new_word(self, word):
        self._curword = self._clean_word(word)
        
        # I don't like entity which is too long
        if len(self._curword) > 15:
            return False
        
        if (self._in_white_list() and self._not_in_black_list() and
            self._not_in_dict() and self._not_duplicated()):
            self._q.append(self._curword)
            if len(self._q) > self._window_size:
                self._q.popleft()
            return True
        return False

    def save2file(self, filename):
        yomi = self._get_yomi()
        with open(filename, 'a', encoding='utf-8') as f:
            f.write(self._curword + '\t' + yomi + '\n')
        self._preword = self._curword
        # print("A new word:'{0}' added!".format(self._curword))

    def _clean_word(self, word):
        word = word.strip()

        # For entities which have same representation, only save one
        # ex: 'Bye-Bye_(光GENJIの曲)' and 'Bye-Bye_(島谷ひとみの曲)'
        index = word.find('_(')
        if index != -1:
            word = word[:index]
        self._curword = word
        return word

    def _get_yomi(self):
        total_yomi = ''

        # For every line in parsed data, 
        # find the columns of yomi(col1) and part of speech(col3)
        for part in self._parsed:
            attributes = part.split('\t')
            yomi, part_of_speech = attributes[1], attributes[3]

            # For words such as '愛の叫び！？', we don't read '！？'
            if part_of_speech != '記号-一般':
                total_yomi += yomi
        return total_yomi

    def _not_in_dict(self):
        parsed = self._tagger.parse(self._curword).strip().splitlines()[:-1]

        # When a word is divided into parts, the word is not in NeoLogd
        if len(parsed) > 1:
            self._parsed = parsed
            return True
        return False

    def _not_duplicated(self):
        # Since the wiki dumpy
        return self._curword != self._preword and self._curword not in self._q


    def _in_white_list(self):
        initial = self._curword[0]
        # alphabet
        if initial.isalpha():
            return True

        # Chinese characters
        if 0x4E00 <= ord(initial) <= 0x9FA0:
            return True

        # hiragana
        if 0x3041 <= ord(initial) <= 0x3093:
            return True

        return False

    def _not_in_black_list(self):
        # remove case: years
        if self._curword[-1] == '年':
            return False

        # remove case: 'アニメソング一覧表' etc.
        if '一覧' in self._curword:
            return False
        return True


nwf = newWordFinder()

with open('jawiki-latest-all-titles', 'r', encoding='utf-8') as f:
    for word in f:
        if nwf.is_new_word(word):
            nwf.save2list('new_words.txt')

# if __name__ == '__main__':
#     import doctest
#     doctest.testmod()
