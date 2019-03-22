import re

# from pyquery.pyquery import PyQuery
from plugins.bibliotik.models import BibliotikTorrent


class BibliotikHtmlParseException(Exception):
    pass


def _parse_authors(torrent, pq):
    authors = []
    for author in pq('p#creatorlist a').items():
        authors.append(author.text())
    torrent.author = ', '.join(authors)


def _parse_title(torrent, pq):
    torrent.title = pq('h1#title').text()
    if not torrent.title:
        raise BibliotikHtmlParseException('Title should not be empty.')


def _parse_format(torrent, details):
    torrent.format = details.pop(0)


def _parse_category(torrent, pq):
    torrent.category = pq('h1#title > img:first-child').attr('title')
    if torrent.category == 'Ebooks':
        assert torrent.format in BibliotikTorrent.EBOOK_FORMATS, u'Unknown eBook format {0}'.format(torrent.format)
    elif torrent.category == 'Applications':
        pass
    elif torrent.category == 'Articles':
        pass
    elif torrent.category == 'Audiobooks':
        pass
    elif torrent.category == 'Comics':
        pass
    elif torrent.category == 'Journals':
        pass
    elif torrent.category == 'Magazines':
        pass
    else:
        raise BibliotikHtmlParseException('Unknown category {0}'.format(torrent.category))


def _parse_retail(torrent, details):
    if details[0] == 'Retail':
        torrent.retail = True
        details.pop(0)
    else:
        torrent.retail = False


def _parse_pages(torrent, details):
    if details[0].endswith('pages'):
        torrent.pages = int(details[0][:-len('pages') - 1])
        details.pop(0)
    else:
        torrent.pages = 0


def _parse_abridged(torrent, details):
    if details[0] == 'Unabridged' or details[0] == 'Abridged':
        details.pop(0)


def _parse_language_isbn(torrent, details):
    if details[0].split(' ')[0] in BibliotikTorrent.LANGUAGES:
        parts = details.pop(0).split(' ')
        torrent.language = parts.pop(0)
        if len(parts):
            assert parts[0][0] == '(' and parts[0][-1] == ')', 'Unknown string after language'
            torrent.isbn = parts[0][1:-1]
            parts.pop()
        else:
            torrent.isbn = ''

        assert len(parts) == 0
    else:
        torrent.language = ''


def _parse_details(torrent, pq):
    details = pq('p#details_content_info').text().split(', ')
    assert len(details) and details[0]
    _parse_format(torrent, details)
    _parse_category(torrent, pq)
    _parse_retail(torrent, details)
    _parse_pages(torrent, details)
    _parse_abridged(torrent, details)
    _parse_language_isbn(torrent, details)
    if len(details) != 0:
        raise BibliotikHtmlParseException('All details must be parsed. Remaining: {0}'.format(', '.join(details)))


def _parse_cover_url(torrent, pq):
    torrent.cover_url = pq('div#sidebar > a[rel="lightbox"] > img').attr('src') or ''


def _parse_tags(torrent, pq):
    torrent.tags = ', '.join(i.text() for i in pq('span.taglist > a').items())


def _parse_publisher_year(torrent, pq):
    publisher_year = pq('p#published').text()
    if publisher_year:
        assert publisher_year.startswith('Published '), \
            "Publisher doesn't start with Published"
        publisher_year = publisher_year[len('Published '):]
        if publisher_year.startswith('by '):
            publisher_year = publisher_year[len('by '):]
            torrent.publisher = ';'.join(i.text() for i in pq('p#published > a').items())
            assert torrent.publisher, 'Publisher can not be empty'
            publisher_mod = ' , '.join(i.text() for i in pq('p#published > a').items())
            assert publisher_year.startswith(publisher_mod), \
                'publisher_year does not start with torrent.publisher'
            publisher_year = publisher_year[len(publisher_mod) + 1:]
        else:
            torrent.publisher = ''
        if publisher_year:
            assert publisher_year.startswith('in '), 'Invalid publisher_year'
            publisher_year = publisher_year[len('in '):]
            torrent.year = int(publisher_year)
        else:
            torrent.year = 0


def _parse_torrent_size(torrent, pq):
    file_info = pq('#details_file_info').text()
    match = re.match(r'(?P<size>\d*,?\d+(\.\d+)?) (?P<quant>B|KB|MB|GB),.*', file_info)
    torrent.size = float(match.group('size').replace(',', '')) * {
        'B': 1, 'KB': 1000, 'MB': 1000 ** 2, 'GB': 1000 ** 3}[match.group('quant')]


def update_torrent_from_html(torrent, html):
    pq = PyQuery(html)
    _parse_authors(torrent, pq)
    _parse_title(torrent, pq)
    _parse_details(torrent, pq)
    _parse_cover_url(torrent, pq)
    _parse_tags(torrent, pq)
    _parse_publisher_year(torrent, pq)
    _parse_torrent_size(torrent, pq)
