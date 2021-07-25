from flexx import flx


def _clean_attrs(attrs):
    if 'klass' in attrs:
        attrs['class'] = attrs['klass']
        del attrs['klass']
    return attrs
    pass


class Tag:
    def __init__(self, parent: 'Html', tag_type: str, attributes):
        self.parent_doc = parent
        self.tag_type = tag_type
        self.attrs = attributes
        self.children = []
        self.parent_tag = None

    def __enter__(self):
        self.parent_tag = self.parent_doc.current_tag
        self.parent_doc.current_tag = self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is None:
            tag = flx.create_element(self.tag_type, self.attrs, self.children)
            if self.parent_tag is not None:
                self.parent_tag.children.append(tag)
                self.parent_doc.current_tag = self.parent_tag
            return tag


class Html:
    def __init__(self):
        self.current_tag = Tag(self, 'div', {})

    def tag(self, tag_type, **kwargs):
        return Tag(self, tag_type, _clean_attrs(kwargs))

    def text(self, *args):
        for a in args:
            self.current_tag.children.append(a)

    def tagtext(self):
        return self, self.tag, self.text

    def finalize(self):
        return self.current_tag.__exit__(None, None, None)
