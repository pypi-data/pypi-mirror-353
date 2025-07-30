"""Internet-related functions."""
from __future__ import annotations

from collections.abc import Callable, Iterator, Sequence
from getpass import getuser
from html import escape
from http import HTTPStatus
from itertools import chain
from os import scandir
from pathlib import Path
from typing import TYPE_CHECKING, Literal, NotRequired, TypedDict, cast
import contextlib
import logging
import plistlib
import re
import urllib
import urllib.parse

from bs4 import BeautifulSoup as Soup, Tag
import keyring
import requests

from .chromium import generate_chrome_user_agent
from .string import hexstr2bytes
from .system import IS_LINUX

if TYPE_CHECKING:
    from .typing import FileDescriptorOrPath, StrPath

__all__ = ('BookmarksDataset', 'BookmarksHTMLAnchorAttributes', 'BookmarksHTMLFolder',
           'BookmarksHTMLFolderAttributes', 'BookmarksHTMLLink', 'RecurseBookmarksHTMLCallback',
           'check_bookmarks_html_urls', 'generate_html_dir_tree', 'parse_bookmarks_html',
           'recurse_bookmarks_html', 'upload_to_imgbb', 'where_from')

log = logging.getLogger(__name__)
KEY_ORIGIN_URL = 'user.xdg.origin.url'
KEY_WHERE_FROMS = 'com.apple.metadata:kMDItemWhereFroms'


def _getxattr(file: FileDescriptorOrPath,
              name: str,
              *,
              follow_symlinks: bool = False) -> bytes:  # pragma: no cover
    from os import getxattr  # noqa: PLC0415
    return getxattr(file, name, follow_symlinks=follow_symlinks)


def where_from(file: FileDescriptorOrPath, *, webpage: bool = False) -> str | None:
    """Determine where a file came from based on metadata in extended attributes."""
    index = 1 if webpage else 0
    attr_value = _getxattr(file, KEY_ORIGIN_URL if IS_LINUX else KEY_WHERE_FROMS).decode()
    if not IS_LINUX:
        return cast('Sequence[str]', plistlib.loads(hexstr2bytes(attr_value)))[index]
    return attr_value


def generate_html_dir_tree(start_dir: StrPath,
                           *,
                           follow_symlinks: bool = False,
                           depth: int = 2) -> str:
    """Generate a HTML directory listing."""
    def recurse_cwd(path: Path, _cur_depth: int = 0) -> Iterator[str]:
        for entry in sorted(sorted(scandir(path), key=lambda x: x.name),
                            key=lambda x: not x.is_dir(follow_symlinks=follow_symlinks)):
            if (entry.is_dir(follow_symlinks=follow_symlinks) and _cur_depth < depth):
                yield ('<li class="dir mui--text-dark mui--text-body2"><details><summary>'
                       f'<code>{escape(entry.name)}/</code></summary><ul>')
                yield from recurse_cwd(Path(entry), _cur_depth=_cur_depth + 1)
                yield '</ul></details></li>'
            else:
                isd = entry.is_dir(follow_symlinks=follow_symlinks)
                class_ = 'file' if not isd else 'dir'
                slash = '' if not isd else '/'
                yield (
                    f'<li class="{class_} mui--text-dark mui--text-body1"><a class="mui--text-dark"'
                    f' href="./{entry.path}"><code>{escape(entry.name)}{slash}</code></a></li>')

    start_dir = Path(start_dir).resolve(strict=True)
    with contextlib.chdir(start_dir):
        title = start_dir.name
        files = ''.join(chain.from_iterable(recurse_cwd(start_dir)))
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Contents of {title}/</title>
<link rel="stylesheet" href="https://cdn.muicss.com/mui-0.10.3/css/mui.min.css"
crossorigin="anonymous">
<style>
ul {{
    list-style: none;
    padding-inline-start: 1em;
}}
.dir {{
    cursor: pointer;
}}
.mui-appbar {{
    margin-bottom: 2em;
}}
</style>
</head>
<body>
<header class="mui-appbar mui--z1">
<div class="mui-container-fluid">
<h1 class="mui--text-title">Contents of {title}</h1>
</div>
</header>
<div class="mui-container-fluid">
<ul>{files}</ul>
</div>
</body>
</html>"""


def upload_to_imgbb(path: StrPath,
                    *,
                    api_key: str | None = None,
                    keyring_username: str | None = None,
                    timeout: float = 5) -> requests.Response:
    """
    Upload an image to ImgBB.

    Get an API key at https://api.imgbb.com/ and set it with ``keyring set imgbb keyring_username``.
    """
    r = requests.post(
        'https://api.imgbb.com/1/upload',
        files={'image': Path(path).resolve(strict=True).read_bytes()},
        params={'key': api_key or keyring.get_password('imgbb', keyring_username or getuser())},
        timeout=timeout)
    r.raise_for_status()
    return r


def stripped_strings_fixed(child: Tag) -> str:
    return re.sub(r'\s+', ' ', ' '.join(child.stripped_strings))


class BookmarksHTMLAnchorAttributes(TypedDict):
    """Attributes of a bookmark link."""
    add_date: str
    href: str
    icon: NotRequired[str]


class BookmarksHTMLFolderAttributes(TypedDict):
    """Attributes of a bookmark folder."""
    add_date: str
    last_modified: str
    personal_toolbar_folder: NotRequired[Literal['true']]


class BookmarksHTMLLink(TypedDict):
    """A bookmark link."""
    attrs: BookmarksHTMLAnchorAttributes
    title: str
    type: Literal['link']


class BookmarksHTMLFolder(TypedDict):
    """A bookmark folder."""
    attrs: BookmarksHTMLFolderAttributes
    children: list[BookmarksHTMLLink | BookmarksHTMLFolder]
    name: str
    type: Literal['folder']


BookmarksDataset = list[BookmarksHTMLFolder | BookmarksHTMLLink]
"""Bookmark top structure."""

RecurseBookmarksHTMLCallback = Callable[
    [BookmarksHTMLAnchorAttributes, str, Sequence[tuple[str, BookmarksHTMLFolderAttributes]]], None]
"""Callback for :py:func:`recurse_bookmarks_html` to call for each link."""


def recurse_bookmarks_html(soup: Tag, callback: RecurseBookmarksHTMLCallback) -> None:
    """Traverse the ``bookmarks.html`` tree and call the callback for each link."""
    for child in soup.children:
        if not isinstance(child, Tag):
            continue
        match child.name:
            case 'dl' | 'dt' | 'html' | 'body':
                recurse_bookmarks_html(child, callback)
            case 'a':
                folder_path: list[tuple[str, BookmarksHTMLFolderAttributes]] = []
                for parent in child.parents:
                    if parent.name == 'dl' and (h3 := parent.find_previous_sibling('h3')):
                        assert isinstance(h3, Tag)
                        folder_path.append((stripped_strings_fixed(h3),
                                            cast('BookmarksHTMLFolderAttributes', h3.attrs)))
                        break
                callback(cast('BookmarksHTMLAnchorAttributes', child.attrs),
                         stripped_strings_fixed(child), folder_path)


def create_parsed_tree_structure(
        folder_path: Sequence[tuple[str, BookmarksHTMLFolderAttributes]],
        data: BookmarksDataset) -> list[BookmarksHTMLFolder | BookmarksHTMLLink]:
    keys = [f[0] for f in folder_path]
    ref = data
    # This breaks for folders that are named the same at the same depth
    for i, key in enumerate(keys):
        try:
            next(x for x in ref if x['type'] == 'folder' and x['name'] == key)
        except StopIteration:
            new_level: BookmarksHTMLFolder = {
                'attrs': folder_path[i][1],
                'children': [],
                'name': key,
                'type': 'folder'
            }
            ref.append(new_level)
            ref = new_level['children']
    return ref


def parse_bookmarks_html(html_content: str) -> BookmarksDataset:
    """Parse a browser's exported ``bookmarks.html``."""
    from bs4 import BeautifulSoup as Soup  # noqa: PLC0415
    data: BookmarksDataset = []

    def callback(attrs: BookmarksHTMLAnchorAttributes, title: str,
                 folder_path: Sequence[tuple[str, BookmarksHTMLFolderAttributes]]) -> None:
        ref = create_parsed_tree_structure(folder_path, data)
        ref.append({'type': 'link', 'title': title, 'attrs': attrs})

    recurse_bookmarks_html(Soup(html_content, 'html5lib'), callback)
    return data


def check_bookmarks_html_urls(
        html_content: str) -> tuple[BookmarksDataset, BookmarksDataset, BookmarksDataset]:
    """
    Check a browser's exported bookmarks.html's URLs.

    Checks for URLs that are not valid any more (status ``404``) or have changed (statuses ``301``
    and ``302``).
    """
    # After html5lib fixes it, the structure is:
    # DL -> many p -> many DT -> H3 (folder), DL then
    #   p or DT -> A or H3 (folder where structure repeats), DL
    data: BookmarksDataset = []
    changed: BookmarksDataset = []
    not_found: BookmarksDataset = []
    session = requests.Session()
    session.headers.update({
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'referer': 'https://www.google.com/',
        'upgrade-insecure-requests': '1',
        'user_agent': generate_chrome_user_agent()
    })

    def callback(attrs: BookmarksHTMLAnchorAttributes, title: str,
                 folder_path: Sequence[tuple[str, BookmarksHTMLFolderAttributes]]) -> None:
        ref = create_parsed_tree_structure(folder_path, data)
        new_data: BookmarksHTMLLink = {'type': 'link', 'title': title, 'attrs': attrs}
        if 'href' in attrs and re.match(r'^https?://', attrs['href']):
            log.debug('HEAD %s', attrs['href'])
            r = session.head(attrs['href'])
            if r.status_code in {HTTPStatus.MOVED_PERMANENTLY, HTTPStatus.FOUND}:
                new_location = r.headers['location']
                if not re.match(r'^https://', new_location):
                    parsed = urllib.parse.urlparse(attrs['href'])
                    port_str = f':{parsed.port}' if parsed.port else ''
                    new_location = f'{parsed.scheme}://{parsed.netloc}{port_str}{new_location}'
                log.info('%d: "%s" @ "%s" -> "%s"', r.status_code, ' / '.join(
                    [*(f[0] for f in folder_path), title]), attrs['href'], new_location)
                attrs['href'] = new_location
                changed.append(new_data)
            elif r.status_code == HTTPStatus.NOT_FOUND:
                log.error('%d: "%s" @ "%s"', r.status_code,
                          ' / '.join([*(f[0] for f in folder_path), title]), attrs['href'])
                not_found.append(new_data)
        ref.append(new_data)

    recurse_bookmarks_html(Soup(html_content, 'html5lib'), callback)
    return data, changed, not_found
