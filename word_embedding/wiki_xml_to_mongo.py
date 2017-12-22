# -*- coding: utf-8 -*-
import sys
import thread
import datetime
import pymongo
from pymongo import MongoClient
from xml.sax import handler, make_parser
from xml.sax.saxutils import XMLFilterBase


class WikiPage(object):
    """
    Holds data related to one <page> element parsed from the dump
    """

    def __init__(self):
        self.title = u''
        self.id = u''
        self.text = u''
        self.sha1 = u''

    def __str__(self):
        return 'ID %s TITLE %s %s' % (self.id.encode('utf_8'),
                                      self.title.encode('utf_8'), self.sha1)

    def __unicode__(self):
        return 'ID %s TITLE %s %s' % (self.id, self.title, self.sha1)


class text_normalize_filter(XMLFilterBase):

    def __init__(self, upstream, downstream):
        XMLFilterBase.__init__(self, upstream)
        self._downstream = downstream
        self._accumulator = []

    def _complete_text_node(self):
        if self._accumulator:
            self._downstream.characters(''.join(self._accumulator))
            self._accumulator = []

    def characters(self, text):
        self._accumulator.append(text)

    def ignorableWhiteSpace(self, ws):
        self._accumulator.append(text)


def _wrap_complete(method_name):

    def method(self, *a, **k):
        self._complete_text_node()
        getattr(self._downstream, method_name)(*a, **k)

    method.__name__ = method_name
    setattr(text_normalize_filter, method_name, method)


for n in '''startElement endElement endDocument'''.split():
    _wrap_complete(n)


class WikiDumpHandler(handler.ContentHandler):
    """
    A ContentHandler designed to pull out page ids, titles and text from
    Wiki pages. These are assembled into WikiPage objects and sent off
    to the supplied callback.
    """

    def __init__(self, pageCallBack=None):
        handler.ContentHandler.__init__(self)
        self.currentTag = ''
        self.ignoreIdTags = False
        self.pageCallBack = pageCallBack
        self.pagesProcessed = 0

    def startElement(self, name, attrs):
        self.currentTag = name
        if (name == 'page'):
            # add a page
            self.currentPage = WikiPage()
        elif (name == 'revision'):
            # when we're in revision, ignore ids
            self.ignoreIdTags = True

    def endElement(self, name):
        if (name == 'page'):
            if self.pageCallBack is not None:
                self.pageCallBack(self.currentPage)
            self.pagesProcessed += 1
        elif (name == 'revision'):
            # we've finished the revision section
            self.ignoreIdTags = False
        self.currentTag = ''

    def characters(self, content):
        if (self.currentTag == 'id' and not self.ignoreIdTags):
            self.currentPage.id = content
        elif (self.currentTag == 'title'):
            self.currentPage.title = content
        elif (self.currentTag == 'text'):
            self.currentPage.text = content
        elif (self.currentTag == 'sha1'):
            self.currentPage.sha1 = content

    def endDocument(self):
        print "Processed %d pages" % self.pagesProcessed


def parseWithCallback(inputFileName, callback):
    parser = make_parser()
    parser.setFeature(handler.feature_namespaces, 0)

    # apply the text_normalize_filter
    wdh = WikiDumpHandler(pageCallBack=callback)
    filter_handler = text_normalize_filter(parser, wdh)

    filter_handler.parse(open(inputFileName))


def printPage(page):
    print page


#Settings
db_name = 'local'
collection_name = 'wiki_article'
client = MongoClient()

client = MongoClient('mongodb://172.17.0.1:27017/')

#Setup MongoDB Connection
mongo_db = client[db_name]
mongo_collection = mongo_db[collection_name]


def dumpPage(page):
    post = {}
    post['pageTitle'] = page.title
    post['pageID'] = page.id
    post['text'] = page.text
    post['sha1'] = page.sha1
    post['query'] = ""
    mongo_collection.insert(post)


if __name__ == "__main__":
    """
    When called as script, argv[1] is assumed to be a filename and we
    simply print pages found.
    """
    if (sys.argv[2] == 'dump'):
        now = datetime.datetime.now()
        print "Started at " + now.strftime("%Y-%m-%d %H:%M")
        parseWithCallback(sys.argv[1], dumpPage)
        now = datetime.datetime.now()
        print "Ended at " + now.strftime("%Y-%m-%d %H:%M")
    elif (sys.argv[2] == 'update'):
        parseWithCallback(sys.argv[1], printPage)
