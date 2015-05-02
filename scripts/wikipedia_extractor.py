# coding:utf-8
'''
WikipediaのAPIを使ってコンテンツをダウンロードしてくる
'''

import xml.sax
import xml.sax.handler
from HTMLParser import HTMLParser
from urllib import urlopen


class WikipediaExtractor():
    def __init__(self, logger, writer):
        self._logger = logger
        self._xml_parser = xml.sax.make_parser()
        self._html_parser = None

    def get_subcategories_titles(self, cat_name):
        # TODO limitが500まで, それ以上欲しければcmcontinueを追う仕組みが必要

        # init
        wlist = list()
        catlist = list()
        self._xml_parser.setContentHandler(
            CategoryXmlHandler(wlist, catlist))

        # Wikipedia API
        request = (
            'http://ja.wikipedia.org/w/api.php?'
            'format=json&action=query&list=categorymembers'
            '&cmlimit=500&cmtitle=Category:%s&format=xml' % cat_name
        )
        self._logger.info('request to Wikipedia\n%s' % request)
        result = urlopen(request)

        # parse xml
        self._xml_parser.parse(result)
        return wlist, catlist

    def get_content(self, title):
        # init
        cxhandler = ContentXmlHandler()
        self._html_parser = ContentHtmlHandler()
        self._xml_parser.setContentHandler(cxhandler)

        # Wikipedia API
        request = (
            'http://ja.wikipedia.org/w/api.php?'
            'format=xml&action=query&prop=revisions&rvparse'
            '&rvprop=content&titles=%s' % title
        )
        self._logger.info('request to Wikipedia\n%s' % request)
        result = urlopen(request)

        # parse xml html
        self._xml_parser.parse(result)
        xml_parsed = cxhandler.get_content()
        self._html_parser.feed(xml_parsed)
        html_parsed = self._html_parser.get_content().encode('utf-8')
        return html_parsed


class CategoryXmlHandler(xml.sax.handler.ContentHandler):
    def __init__(self, wl, cl):
        self._wlist = wl
        self._catlist = cl

    def startElement(self, name, attrs):  # noqa
        if name == 'cm':
            title = attrs['title'].encode('utf-8')
            if title.startswith('Category:'):
                self._catlist.append(":".join(title.split(":")[1:]))
            else:
                self._wlist.append(title)


class ContentXmlHandler(xml.sax.handler.ContentHandler):
    def __init__(self):
        self._flag = False
        self._content = ''

    def startElement(self, name, attrs):  # noqa
        if name == 'rev':
            self._flag = True

    def characters(self, content):
        if self._flag:
            self._content += content

    def endElement(self, name):
        self._flag = False

    def get_content(self):
        return self._content


class ContentHtmlHandler(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self._content = ''

    def handle_data(self, content):
        self._content += content

    def get_content(self):
        return self._content
