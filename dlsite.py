import ssl

ssl.HAS_SNI = False

import re
import requests as r

from bs4 import BeautifulSoup


class RJError(Exception):
    def __init__(self, code):
        self._code = code

    def __str__(self):
        return "RJError occured for RJCode: " + self._msg


class InvalidCodeError(RJError):
    def __str__(self):
        return "Invalid RJCode: " + self._msg


class WorkNotFoundError(RJError):
    def __str__(self):
        return "Failed to find DLsite page for RJCode: " + self._msg


class ParseError(RJError):
    pass


class URLParseError(ParseError):
    def __str__(self):
        return "URL Parsing Failed for RJCode: " + self._msg


class DOMParseError(ParseError):
    def __str__(self):
        return "DOM Parsing Failed for RJCode: " + self._msg


class Patterns:
    P_RICH = re.compile(r"(RJ|VJ|BJ)\d{6}")
    P_RAW = re.compile(r"(?<=\D)\d{6}(?=\D)")
    P_CATEGORY = re.compile(r"(?<=dlsite.com/).+(?=/work)")


class Utils:
    _REQCACHE = {}

    @classmethod
    def request_code(cls, richcode):
        URL = "https://www.dlsite.com/soft/work/=/product_id/%s.html"
        if richcode in cls._REQCACHE:
            return cls._REQCACHE[richcode]
        else:
            res = r.get(URL % richcode, verify=False)
            cls._REQCACHE[richcode] = res
            return res

    @staticmethod
    def get_image(path, richcode, url):
        res = r.get(url, verify=False)
        if res.status_code != 200:
            raise WorkNotFoundError(richcode)

        with open(path, 'wb') as fp:
            fp.write(res.content)

    @staticmethod
    def assert_code(code):
        if len(code) != 8:
            raise InvalidCodeError(code)
        found = Patterns.P_RICH.search(code)
        if not found:
            raise InvalidCodeError(code)
        return found

    @staticmethod
    def validate_code(code):
        if len(code) != 8:
            return False
        found = Patterns.P_RICH.search(code)
        if not found:
            return False
        return True

    @staticmethod
    def normalize(text):
        found = Patterns.P_RICH.search(text)
        if found:
            return found.group()

        found = Patterns.P_RAW.search(text)
        if found:
            rawcode = found.group()
            for prefix in ["RJ", "VJ", "BJ"]:
                richcode = prefix + rawcode
                res = Utils.request_code(richcode)
                if res.status_code == 200:
                    return richcode
        return None


class Work():
    CATEGORY = {
        'home': False,
        'soft': False,
        'maniax': True,
        'book': True,
        'pro': True
    }

    def __init__(self, richcode):
        Utils.assert_code(richcode)
        self._code = richcode

        res = Utils.request_code(richcode)
        if res.status_code != 200:
            raise WorkNotFoundError(richcode)

        self._url = res.url

        found = Patterns.P_CATEGORY.search(res.url)
        if not found:
            raise URLParseError(richcode)
        self._category = found.group()

        try:
            soup = BeautifulSoup(res.text, 'html5lib')
            self._title = soup.find(id='work_name').findChild().text
            img_items = soup.select('li.slider_item.active')
            if img_items:
                self._img = 'https:' + img_items[0].findChild().attrs['src']
            else:
                self._img = None
            maker_items = soup.select('span.maker_name')
            self._maker_name = maker_items[0].findChild().text
        except Exception as e:
            raise DOMParseError(richcode) from e

    @property
    def dict(self):
        return {
            'product_id': self._code,
            'title': self._title,
            'category': self._category,
            'maker_name': self._maker_name,
            'is_nsfw': self.is_nsfw,
            'req_url': self._url,
            'img_url': self._img,
        }

    @property
    def is_nsfw(self):
        try:
            return self.CATEGORY[self._category]
        except KeyError as e:
            raise NotImplementedError from e

    @property
    def code(self): return self._code

    @property
    def category(self): return self._category

    @property
    def title(self): return self._title

    @property
    def img(self): return self._img

    @property
    def maker_name(self): return self._maker_name
