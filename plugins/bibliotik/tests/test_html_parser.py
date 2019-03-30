import json
import os

from django.test import TestCase
from django.utils import timezone

from plugins.bibliotik import html_parser
from plugins.bibliotik.models import BibliotikTorrent
from torrents.models import TorrentInfo, Realm


class HtmlParserTests(TestCase):
    def _load_html(self, filename):
        with open(os.path.join(os.path.dirname(__file__), 'files', filename)) as f:
            return f.read()

    def _get_torrent(self, filename):
        realm = Realm.objects.create()
        torrent_info = TorrentInfo.objects.create(
            realm=realm,
            fetched_datetime=timezone.now(),
            is_deleted=False,
        )
        torrent = BibliotikTorrent(
            torrent_info=torrent_info,
            fetched_datetime=timezone.now(),
            is_deleted=False,
        )
        html = self._load_html(filename)
        html_parser.update_torrent_from_html(torrent, html)
        torrent.save()
        return torrent

    def test_ebook_590561(self):
        torrent = self._get_torrent('590561.html')

        self.assertEqual(torrent.category, BibliotikTorrent.CATEGORY_EBOOKS)
        self.assertEqual(torrent.format, 'EPUB')
        self.assertTrue(torrent.retail)
        self.assertEqual(torrent.pages, None)
        self.assertEqual(torrent.language, 'English')
        self.assertEqual(torrent.isbn, '9781441236456')
        self.assertEqual(
            torrent.cover_url,
            'https://imagecache.bibliotik.me/?url=ssl%3Aimg1.od-cdn.com%2FImageType'
            '-100%2F2003-1%2F%7BD12C4D94-D2A6-46BA-829B-E21261332E33%7DImg100.jpg&w=220&t=fitup',
        )
        self.assertEqual(torrent.tags, 'nonfiction, christianity, bible, commentary')
        self.assertEqual(torrent.publisher, 'Baker Publishing Group')
        self.assertEqual(torrent.year, 2011)
        self.assertEqual(torrent.joined_authors, 'Gordon D. Fee')
        self.assertEqual(json.loads(torrent.authors_json), [{'id': 240788, 'name': 'Gordon D. Fee'}])
        self.assertEqual(torrent.title, '1 & 2 Timothy, Titus (Understanding the Bible Commentary)')
        self.assertEqual(torrent.size, 3110000)

    def test_ebook_3188(self):
        torrent = self._get_torrent('3188.html')

        self.assertEqual(torrent.category, BibliotikTorrent.CATEGORY_EBOOKS)
        self.assertEqual(torrent.format, 'PDF')
        self.assertFalse(torrent.retail)
        self.assertEqual(torrent.pages, 1)
        self.assertEqual(torrent.language, 'English')
        self.assertEqual(torrent.isbn, '0028642449')
        self.assertEqual(
            torrent.cover_url,
            'https://imagecache.bibliotik.me/?url=ecx.images-amazon.com%2Fimages%2FI%2F5182NV43JFL.jpg&w=220&t=fitup',
        )
        self.assertEqual(torrent.tags, 'nonfiction, music, guitar, learning, hobbies')
        self.assertEqual(torrent.publisher, None)
        self.assertEqual(torrent.year, None)
        self.assertEqual(torrent.joined_authors, 'Frederick Noad')
        self.assertEqual(json.loads(torrent.authors_json), [{'id': 3026, 'name': 'Frederick Noad'}])
        self.assertEqual(torrent.title, 'The Complete Idiot\'s Guide to Playing Guitar (2nd Edition)')
        self.assertEqual(torrent.size, 8530000)

    def test_ebook_6588(self):
        torrent = self._get_torrent('6588.html')

        self.assertEqual(torrent.category, BibliotikTorrent.CATEGORY_EBOOKS)
        self.assertEqual(torrent.format, 'PDF')
        self.assertFalse(torrent.retail)
        self.assertEqual(torrent.pages, 144)
        self.assertEqual(torrent.language, 'English')
        self.assertEqual(torrent.isbn, '9781584350415')
        self.assertEqual(
            torrent.cover_url,
            'https://imagecache.bibliotik.me/?url=ecx.images-amazon.com%2Fimages%2FI%2F415zlOhIAvL.jpg&w=220&t=fitup',
        )
        self.assertEqual(torrent.tags, 'nonfiction, philosophy')
        self.assertEqual(torrent.publisher, 'Semiotext(e)')
        self.assertEqual(torrent.year, 2007)
        self.assertEqual(torrent.joined_authors, 'Jean Baudrillard')
        self.assertEqual(json.loads(torrent.authors_json), [{'id': 775, 'name': 'Jean Baudrillard'}])
        self.assertEqual(torrent.title, 'Forget Foucault (Foreign Agents)')
        self.assertEqual(torrent.size, 2200000)

    def test_audiobook_590771(self):
        torrent = self._get_torrent('590771.html')

        self.assertEqual(torrent.category, BibliotikTorrent.CATEGORY_AUDIOBOOKS)
        self.assertEqual(torrent.format, 'M4B 64 kbps')
        self.assertFalse(torrent.retail)
        self.assertEqual(torrent.pages, None)
        self.assertEqual(torrent.language, 'English')
        self.assertEqual(torrent.isbn, None)
        self.assertEqual(
            torrent.cover_url,
            'https://imagecache.bibliotik.me/?url=ssl%3Am.media-amazon.com%2Fimages%2FI%2F51s1X5B91gL.jpg&w=220&t=fitup',
        )
        self.assertEqual(torrent.tags, 'nonfiction, history, biography, collectibles, rare books')
        self.assertEqual(torrent.publisher, 'Penguin Audio')
        self.assertEqual(torrent.year, 2019)
        self.assertEqual(torrent.joined_authors, 'Margaret Leslie Davis')
        self.assertEqual(json.loads(torrent.authors_json), [{'id': 144964, 'name': 'Margaret Leslie Davis'}])
        self.assertEqual(torrent.title,
                         'The Lost Gutenberg: The Astounding Story of One Book\'s Five-Hundred-Year Odyssey')
        self.assertEqual(torrent.size, 174970000)

    def test_audiobook_375080(self):
        torrent = self._get_torrent('375080.html')

        self.assertEqual(torrent.category, BibliotikTorrent.CATEGORY_AUDIOBOOKS)
        self.assertEqual(torrent.format, 'MP3 64 kbps')
        self.assertEqual(torrent.title, 'Dr. York, Miss Winnie, and the Typhoid Shot')
