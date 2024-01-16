from lxml import etree
import requests
from requests import Response
from Functions import regexify

class Parser:
    """Html class for response."""

    def __init__(self):
        self.dom = None

    def set(self, response: Response):
        if isinstance(response, requests.Response):
            self.dom = etree.HTML(response.content)

    def stringify(self, xpath, elements):
        if elements is None:
            return None
        if xpath.endswith('/text()') or regexify(r'(@\w+)$', xpath):
            return [str(element).strip() for element in elements]
        return elements

    def get_xpath_elements(self, xpaths):
        for xpath in xpaths:
            elements = self.stringify(xpath, self.dom.xpath(xpath))
            if elements:
                return elements
        return None

    def find(self, string):
        return self.dom.find(string)
