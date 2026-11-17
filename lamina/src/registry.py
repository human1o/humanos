"""Glyph registry: every drawing registers itself with its name, code point
and spacing on each side."""

GLYPHS = {}   # name -> (func, unicodes)
ORDER = []


def glyph(name, uni=None, aliases=()):
    def deco(fn):
        unis = [uni] if isinstance(uni, int) else list(uni or [])
        GLYPHS[name] = (fn, unis + list(aliases))
        ORDER.append(name)
        return fn
    return deco


class G:
    """A drawn glyph: outline plus spacing.

    left / right: sidebearing in font units, or a key of the spacing table
    ('S' straight, 'R' round, 'SC', 'RC', ...). If `advance` is given the
    outline is used as drawn (no automatic sidebearings).
    """

    def __init__(self, shape, left=None, right=None, advance=None, components=None, anchors=None):
        self.shape = shape
        self.left = left
        self.right = right
        self.advance = advance
        self.components = components  # list of (glyph_name, dx, dy)
        self.anchors = anchors or {}
