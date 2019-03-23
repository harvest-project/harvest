import json
import re

from bs4 import BeautifulSoup

from plugins.bibliotik.models import BibliotikTorrent


class BibliotikHtmlParseException(Exception):
    pass


def _parse_category(torrent, soup):
    torrent.category = soup.select_one('h1#title > img:first-child')['title']
    if torrent.category not in {c[0] for c in BibliotikTorrent.CATEGORY_CHOICES}:
        raise BibliotikHtmlParseException('Unknown category {0}'.format(torrent.category))


def _parse_title(torrent, soup):
    title_tag = soup.find('h1', id='title')
    if title_tag:
        torrent.title = title_tag.text.strip()
    else:
        raise BibliotikHtmlParseException('Title should not be empty.')


def _parse_authors(torrent, soup):
    authors = []
    for author in soup.select('p#creatorlist a'):
        authors.append({
            'id': int(author['href'].split('/')[-1]),
            'name': author.text.strip(),
        })
    torrent.joined_authors = ', '.join(a['name'] for a in authors)
    torrent.authors_json = json.dumps(authors)


def _parse_publisher_year_isbn(torrent, soup):
    tag = soup.find('p', id='published')
    if not tag:
        raise BibliotikHtmlParseException('Unable to find p#published')
    match = re.match(r'^Published by (?P<publisher>.+) in (?P<year>\d+)( \((?P<isbn>.+)\))?$', tag.text.strip())
    if not match:
        raise BibliotikHtmlParseException('Unable to match publisher_year_isbn: {}'.format(value))
    torrent.publisher = match.group('publisher')
    torrent.year = int(match.group('year'))
    torrent.isbn = match.group('isbn')


def _parse_language_pages(torrent, soup):
    tag = soup.find('p', id='details_content_info')
    if not tag:
        raise BibliotikHtmlParseException('Unable to find p#details_content_info')
    language_options = '|'.join(re.escape(lang) for lang in BibliotikTorrent.LANGUAGES)
    match = re.match(r'^(?P<language>{})(, (?P<pages>\d+) pages)?$'.format(language_options), tag.text.strip())
    if not match:
        raise BibliotikHtmlParseException('Unable to match language_pages')
    torrent.language = match.group('language')
    torrent.pages = int(match.group('pages')) if match.group('pages') else None


def _parse_tags(torrent, soup):
    torrent.tags = ', '.join(i.text.strip() for i in soup.select('p#details_tags a.tagLink'))


def _parse_torrent_size(size):
    parts = size.split(' ')
    sizes = {'B': 1, 'KB': 1000, 'MB': 1000 ** 2, 'GB': 1000 ** 3}
    return int(float(parts[0].replace(',', '')) * sizes[parts[1]])


def _parse_retail_format_size(torrent, soup):
    tag = soup.find('p', id='details_file_info')
    if not tag:
        raise BibliotikHtmlParseException('Unable to find p#details_content_info')
    value = tag.text.strip().replace('\n', '')
    format_options = '|'.join(re.escape(format) for format in BibliotikTorrent.EBOOK_FORMATS)
    match = re.match(
        r'^(?P<retail>Retail )?(?P<format>{}), +(?P<size>[\d,.]+ (B|KB|MB|GB)).*$'.format(format_options),
        value,
    )
    if not match:
        raise BibliotikHtmlParseException('Unable to match language_pages: {}'.format(value))
    torrent.retail = bool(match.group('retail'))
    torrent.format = match.group('format')
    torrent.size = _parse_torrent_size(match.group('size'))


def _parse_cover_url(torrent, soup):
    img = soup.select_one('div#sidebar > a[rel="lightbox"] > img')
    if img:
        torrent.cover_url = img['src']
    else:
        torrent.cover_url = None


def update_torrent_from_html(torrent, html):
    soup = BeautifulSoup(html, 'html5lib')
    _parse_category(torrent, soup)
    _parse_title(torrent, soup)
    _parse_authors(torrent, soup)
    _parse_publisher_year_isbn(torrent, soup)
    _parse_language_pages(torrent, soup)
    _parse_tags(torrent, soup)
    _parse_retail_format_size(torrent, soup)
    _parse_cover_url(torrent, soup)
