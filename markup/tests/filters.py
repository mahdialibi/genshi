# -*- coding: utf-8 -*-
#
# Copyright (C) 2006 Edgewall Software
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://markup.edgewall.org/wiki/License.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://markup.edgewall.org/log/.

import doctest
import unittest

from markup.core import Stream
from markup.input import HTML, ParseError
from markup.filters import HTMLSanitizer


class HTMLSanitizerTestCase(unittest.TestCase):

    def test_sanitize_unchanged(self):
        html = HTML('<a href="#">fo<br />o</a>')
        self.assertEquals('<a href="#">fo<br/>o</a>',
                          str(html.filter(HTMLSanitizer())))

    def test_sanitize_escape_text(self):
        html = HTML('<a href="#">fo&amp;</a>')
        self.assertEquals('<a href="#">fo&amp;</a>',
                          str(html.filter(HTMLSanitizer())))
        html = HTML('<a href="#">&lt;foo&gt;</a>')
        self.assertEquals('<a href="#">&lt;foo&gt;</a>',
                          str(html.filter(HTMLSanitizer())))

    def test_sanitize_entityref_text(self):
        html = HTML('<a href="#">fo&ouml;</a>')
        self.assertEquals(u'<a href="#">fo&ouml;</a>',
                          str(html.filter(HTMLSanitizer())))

    def test_sanitize_escape_attr(self):
        html = HTML('<div title="&lt;foo&gt;"></div>')
        self.assertEquals('<div title="&lt;foo&gt;"/>',
                          str(html.filter(HTMLSanitizer())))

    def test_sanitize_close_empty_tag(self):
        html = HTML('<a href="#">fo<br>o</a>')
        self.assertEquals('<a href="#">fo<br/>o</a>',
                          str(html.filter(HTMLSanitizer())))

    def test_sanitize_invalid_entity(self):
        html = HTML('&junk;')
        self.assertEquals('&junk;', str(html.filter(HTMLSanitizer())))

    def test_sanitize_remove_script_elem(self):
        html = HTML('<script>alert("Foo")</script>')
        self.assertEquals('', str(html.filter(HTMLSanitizer())))
        html = HTML('<SCRIPT SRC="http://example.com/"></SCRIPT>')
        self.assertEquals('', str(html.filter(HTMLSanitizer())))
        self.assertRaises(ParseError, HTML, '<SCR\0IPT>alert("foo")</SCR\0IPT>')
        self.assertRaises(ParseError, HTML,
                          '<SCRIPT&XYZ SRC="http://example.com/"></SCRIPT>')

    def test_sanitize_remove_onclick_attr(self):
        html = HTML('<div onclick=\'alert("foo")\' />')
        self.assertEquals('<div/>', str(html.filter(HTMLSanitizer())))

    def test_sanitize_remove_style_scripts(self):
        # Inline style with url() using javascript: scheme
        html = HTML('<DIV STYLE=\'background: url(javascript:alert("foo"))\'>')
        self.assertEquals('<div/>', str(html.filter(HTMLSanitizer())))
        # Inline style with url() using javascript: scheme, using control char
        html = HTML('<DIV STYLE=\'background: url(&#1;javascript:alert("foo"))\'>')
        self.assertEquals('<div/>', str(html.filter(HTMLSanitizer())))
        # Inline style with url() using javascript: scheme, in quotes
        html = HTML('<DIV STYLE=\'background: url("javascript:alert(foo)")\'>')
        self.assertEquals('<div/>', str(html.filter(HTMLSanitizer())))
        # IE expressions in CSS not allowed
        html = HTML('<DIV STYLE=\'width: expression(alert("foo"));\'>')
        self.assertEquals('<div/>', str(html.filter(HTMLSanitizer())))
        html = HTML('<DIV STYLE=\'background: url(javascript:alert("foo"));'
                                 'color: #fff\'>')
        self.assertEquals('<div style="color: #fff"/>',
                          str(html.filter(HTMLSanitizer())))

    def test_sanitize_remove_src_javascript(self):
        html = HTML('<img src=\'javascript:alert("foo")\'>')
        self.assertEquals('<img/>', str(html.filter(HTMLSanitizer())))
        # Case-insensitive protocol matching
        html = HTML('<IMG SRC=\'JaVaScRiPt:alert("foo")\'>')
        self.assertEquals('<img/>', str(html.filter(HTMLSanitizer())))
        # Grave accents (not parsed)
        self.assertRaises(ParseError, HTML,
                          '<IMG SRC=`javascript:alert("RSnake says, \'foo\'")`>')
        # Protocol encoded using UTF-8 numeric entities
        html = HTML('<IMG SRC=\'&#106;&#97;&#118;&#97;&#115;&#99;&#114;&#105;'
                    '&#112;&#116;&#58;alert("foo")\'>')
        self.assertEquals('<img/>', str(html.filter(HTMLSanitizer())))
        # Protocol encoded using UTF-8 numeric entities without a semicolon
        # (which is allowed because the max number of digits is used)
        html = HTML('<IMG SRC=\'&#0000106&#0000097&#0000118&#0000097'
                    '&#0000115&#0000099&#0000114&#0000105&#0000112&#0000116'
                    '&#0000058alert("foo")\'>')
        self.assertEquals('<img/>', str(html.filter(HTMLSanitizer())))
        # Protocol encoded using UTF-8 numeric hex entities without a semicolon
        # (which is allowed because the max number of digits is used)
        html = HTML('<IMG SRC=\'&#x6A&#x61&#x76&#x61&#x73&#x63&#x72&#x69'
                    '&#x70&#x74&#x3A;alert("foo")\'>')
        self.assertEquals('<img/>', str(html.filter(HTMLSanitizer())))
        # Embedded tab character in protocol
        html = HTML('<IMG SRC=\'jav\tascript:alert("foo");\'>')
        self.assertEquals('<img/>', str(html.filter(HTMLSanitizer())))
        # Embedded tab character in protocol, but encoded this time
        html = HTML('<IMG SRC=\'jav&#x09;ascript:alert("foo");\'>')
        self.assertEquals('<img/>', str(html.filter(HTMLSanitizer())))


def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(HTMLSanitizerTestCase, 'test'))
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')