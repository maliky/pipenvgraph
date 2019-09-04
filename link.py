# -*- coding: utf-8 -*-


class Link:
    def __init__(self, required, source: "Node", target: "Node"):
        """Define a dependency between a module and its dependencies"""
        self.required = required
        self.source = source
        self.target = target

    def __repr__(self):
        source = self.source.__repr__(short=True)
        target = self.target.__repr__(short=True)
        rep = f'{source} -> {target} [label="{self.required}"];'
        return rep

    def __eq__(self, other):
        return (
            self.required == other.required
            and self.source == other.source
            and self.target == other.target
        )


