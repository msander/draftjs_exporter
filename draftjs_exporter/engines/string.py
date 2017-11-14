from __future__ import absolute_import, unicode_literals

from draftjs_exporter.engines.base import DOMEngine

try:
    # Python 3.2 and above.
    from html import escape
except ImportError:
    import cgi

    def escape(s):
        # Force quote escaping in Python 2.7.
        return cgi.escape(s, quote=True).replace('\'', '&#x27;')

# http://w3c.github.io/html/single-page.html#void-elements
# https://github.com/html5lib/html5lib-python/blob/0cae52b2073e3f2220db93a7650901f2200f2a13/html5lib/constants.py#L560
VOID_ELEMENTS = {
    'area',
    'base',
    'br',
    'col',
    'embed',
    'hr',
    'img',
    'input',
    'link',
    'meta',
    'param',
    'source',
    'track',
    'wbr',
}


class DOMString(DOMEngine):
    """
    String concatenation implementation of the DOM API.
    """

    @staticmethod
    def create_tag(type_, attr=None):
        return {
            'type': type_,
            'attr': attr,
            'children': [],
        }

    @staticmethod
    def parse_html(markup):
        """
        Allows inserting arbitrary HTML into the exporter output.
        Treats the HTML as if it had been escaped and was safe already.
        """
        return {
            'type': 'escaped_html',
            'attr': None,
            'children': None,
            'markup': markup,
        }

    @staticmethod
    def append_child(elt, child):
        # This check is necessary because the current wrapper_state implementation
        # has an issue where it inserts elements multiple times.
        # This must be skipped for text, which can be duplicated.
        is_existing_ref = isinstance(child, dict) and child in elt['children']
        if not is_existing_ref:
            elt['children'].append(child)

    @staticmethod
    def render_attrs(attr):
        return ''.join(sorted([' %s="%s"' % (k, escape(v)) for k, v in attr.items()]))

    @staticmethod
    def render_children(children):
        return ''.join([DOMString.render(c) if isinstance(c, dict) else escape(c) for c in children])

    @staticmethod
    def render(elt):
        type_ = elt['type']
        attr = DOMString.render_attrs(elt['attr']) if elt['attr'] else ''
        children = DOMString.render_children(elt['children']) if elt['children'] else ''

        if type_ == 'fragment':
            return children

        if type_ in VOID_ELEMENTS:
            return '<%s%s/>' % (type_, attr)

        if type_ == 'escaped_html':
            return elt['markup']

        return '<%s%s>%s</%s>' % (type_, attr, children, type_)

    @staticmethod
    def render_debug(elt):
        type_ = elt['type']
        attr = DOMString.render_attrs(elt['attr']) if elt['attr'] else ''
        children = DOMString.render_children(elt['children']) if elt['children'] else ''

        if type_ in VOID_ELEMENTS:
            return '<%s%s/>' % (type_, attr)

        if type_ == 'escaped_html':
            return elt['markup']

        return '<%s%s>%s</%s>' % (type_, attr, children, type_)