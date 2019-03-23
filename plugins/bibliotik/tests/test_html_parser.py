import json
import os

from django.test import TestCase

from plugins.bibliotik import html_parser
from plugins.bibliotik.models import BibliotikTorrent


class HtmlParserTests(TestCase):
    def _load_html(self, filename):
        with open(os.path.join(os.path.dirname(__file__), 'files', filename)) as f:
            return f.read()

    def test_ebook_590561(self):
        torrent = BibliotikTorrent()
        html = self._load_html('590561.html')
        html_parser.update_torrent_from_html(torrent, html)
        self.assertEqual(torrent.category, BibliotikTorrent.CATEGORY_EBOOKS)
        self.assertEqual(torrent.format, 'EPUB')
        self.assertTrue(torrent.retail)
        self.assertEqual(torrent.pages, None)
        self.assertEqual(torrent.language, 'English')
        self.assertEqual(torrent.tags, 'nonfiction, christianity, bible, commentary')
        self.assertEqual(torrent.publisher, 'Baker Publishing Group')
        self.assertEqual(torrent.year, 2011)
        self.assertEqual(torrent.joined_authors, 'Gordon D. Fee')
        self.assertEqual(json.loads(torrent.authors_json), [{'id': 240788, 'name': 'Gordon D. Fee'}])
        self.assertEqual(torrent.title, '1 & 2 Timothy, Titus (Understanding the Bible Commentary)')
        self.assertEqual(torrent.size, 3110000)
        self.assertEqual(
            torrent.cover_url,
            'https://imagecache.bibliotik.me/?url=ssl%3Aimg1.od-cdn.com%2FImageType'
            '-100%2F2003-1%2F%7BD12C4D94-D2A6-46BA-829B-E21261332E33%7DImg100.jpg&w=220&t=fitup',
        )
