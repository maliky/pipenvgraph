# -*- coding: utf-8 -*-

# a class representing a package and it's ancestor

class Node:
    def __init__(
        self, name: str, pkgtype: str, version: str, ancestor: "Node" = None
    ):
        """A Node has an name, a pkgtype (root or node), a version and 0 or 1 ancestor"""
        self.name = name.replace("-", "_")
        self.pkgtype = pkgtype
        self.version = version
        self.ancestor = ancestor
        self.importance = 1

    def __repr__(self, short=False):
        if short:
            return f"{self.name}"

        rep = f"{self.name}"
        shape = "rectangle" if self.pkgtype == "root" else "ellipse"
        rep += f' [label="{self.name}:\\n{self.version}", shape={shape}];'
        return rep

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version
