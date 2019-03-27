import json
import re

from bs4 import BeautifulSoup

from plugins.bibliotik.models import BibliotikTorrent

HTML_PARSER = 'html5lib'

SIZE_REGEX = r'(?P<size>[\d,.]+ (B|KB|MB|GB))'
LANGUAGE_REGEX = '|'.join(re.escape(lang) for lang in BibliotikTorrent.LANGUAGES)
EBOOK_FORMATS_REGEX = '|'.join(re.escape(format) for format in BibliotikTorrent.EBOOK_FORMATS)
AUDIOBOOK_FORMATS_REGEX = '|'.join(re.escape(format) for format in BibliotikTorrent.AUDIOBOOK_FORMATS)
AUDIOBOOK_BITRATES_REGEX = '|'.join(re.escape(format) for format in BibliotikTorrent.AUDIOBOOK_BITRATES)


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
    creator_list = soup.find('p', id='creatorlist')
    creator_links = creator_list.find_all('a') if creator_list else []
    for author in creator_links:
        authors.append({
            'id': int(author['href'].split('/')[-1]),
            'name': author.text.strip(),
        })
    torrent.joined_authors = ', '.join(a['name'] for a in authors)
    torrent.authors_json = json.dumps(authors)


def _parse_publisher_year_isbn(torrent, soup):
    tag = soup.find('p', id='published')

    if tag:
        publisher_tag = tag.find('a', class_='publisherLink')
        torrent.publisher = publisher_tag.text.strip() if publisher_tag else None

        isbn_tag = tag.find('span', id='torrentISBN')
        torrent.isbn = isbn_tag.text.strip() if isbn_tag else None

        match = re.match(r'.*in (\d{4}).*', tag.text.strip())
        torrent.year = int(match.group(1)) if match else None


def _parse_language_pages(torrent, soup):
    tag = soup.find('p', id='details_content_info')

    if torrent.category == BibliotikTorrent.CATEGORY_EBOOKS:
        if not tag:
            raise BibliotikHtmlParseException('Unable to find p#details_content_info')
        match = re.match(
            r'^(?P<language>{})'
            r'(, (?P<pages>\d+) pages)?'
            r'(, Supplementary material included)?'
            r'$'.format(LANGUAGE_REGEX),
            tag.text.strip())
        if not match:
            raise BibliotikHtmlParseException('Unable to match language_pages')
        torrent.language = match.group('language')
        torrent.pages = int(match.group('pages')) if match.group('pages') else None
    elif torrent.category == BibliotikTorrent.CATEGORY_AUDIOBOOKS:
        if not tag:
            raise BibliotikHtmlParseException('Unable to find p#details_content_info')
        match = re.match(
            r'^(?P<language>{})'
            r'(, \d+ hours?( \d+ minutes?)?)?'
            r'(, (?P<pages>\d+) pages)?'
            r'(, (Unabridged|Abridged))'
            r'$'.format(LANGUAGE_REGEX),
            tag.text.strip())
        if not match:
            raise BibliotikHtmlParseException('Unable to match audio book language_pages {}'.format(tag.text.strip()))
        torrent.language = match.group('language')
        torrent.pages = int(match.group('pages')) if match.group('pages') else None
    else:
        torrent.language = None
        torrent.pages = None


def _parse_tags(torrent, soup):
    details_tags = soup.find('p', id='details_tags')
    tag_links = details_tags.find_all('a', class_='tagLink') if details_tags else []
    torrent.tags = ', '.join(i.text.strip() for i in tag_links)


def _parse_torrent_size(size):
    parts = size.split(' ')
    sizes = {'B': 1, 'KB': 1000, 'MB': 1000 ** 2, 'GB': 1000 ** 3}
    return int(float(parts[0].replace(',', '')) * sizes[parts[1]])


def _parse_retail_format_size(torrent, soup):
    tag = soup.find('p', id='details_file_info')
    if not tag:
        raise BibliotikHtmlParseException('Unable to find p#details_content_info')
    value = tag.text.strip().replace('\n', '')
    if torrent.category == BibliotikTorrent.CATEGORY_EBOOKS:
        match = re.match(
            r'^(?P<retail>Retail )?(?P<format>{}), +{}.*$'.format(EBOOK_FORMATS_REGEX, SIZE_REGEX),
            value,
        )
        if not match:
            raise BibliotikHtmlParseException('Unable to match language_pages: {}'.format(value))
        torrent.retail = bool(match.group('retail'))
        torrent.format = match.group('format')
        torrent.size = _parse_torrent_size(match.group('size'))
    elif torrent.category == BibliotikTorrent.CATEGORY_AUDIOBOOKS:
        match = re.match(
            r'^(?P<format>{})( (?P<bitrate>{}))?, +{}.*$'.format(
                AUDIOBOOK_FORMATS_REGEX, AUDIOBOOK_BITRATES_REGEX, SIZE_REGEX),
            value,
        )
        if not match:
            raise BibliotikHtmlParseException('Unable to match language_pages: {}'.format(value))
        torrent.retail = False
        torrent.format = match.group('format')
        if match.group('bitrate'):
            torrent.format += ' ' + match.group('bitrate')
        torrent.size = _parse_torrent_size(match.group('size'))
    else:
        torrent.retail = False
        torrent.format = None
        torrent.size = None


def _parse_cover_url(torrent, soup):
    img = soup.select_one('div#sidebar > a[rel="lightbox"] > img')
    if img:
        torrent.cover_url = img['src']
    else:
        torrent.cover_url = None


def update_torrent_from_html(torrent, html):
    soup = BeautifulSoup(html, HTML_PARSER)
    _parse_category(torrent, soup)
    _parse_title(torrent, soup)
    _parse_authors(torrent, soup)
    _parse_publisher_year_isbn(torrent, soup)
    _parse_language_pages(torrent, soup)
    _parse_tags(torrent, soup)
    _parse_retail_format_size(torrent, soup)
    _parse_cover_url(torrent, soup)


def parse_search_results(html):
    soup = BeautifulSoup(html, HTML_PARSER)
    table_tag = soup.find('table', id='torrents_table')
    results = []
    for row_tag in table_tag.find_all('tr', class_='torrent'):
        row_id = row_tag['id']
        if not row_id.startswith('torrent-'):
            raise Exception('Invalid row_id {}'.format(row_id))
        results.append({
            'tracker_id': int(row_id[len('torrent-'):]),
            'title': row_tag.find('span', class_='title').text.strip()
        })
    return results
