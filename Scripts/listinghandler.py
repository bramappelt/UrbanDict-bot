''' Module for converting reddit api listing types to python objects '''


import itertools
import reprlib


class Thread:
    ''' reoccuring object representing a specific listing level '''
    def __init__(self, data):
        self.__data = data
        self.childs = self.get_children(self.children)

    def __getattr__(self, key):
        ''' dynamic attribute accessment '''
        try:
            return self.__data['data'][key]
        except KeyError:
            raise

    def __repr__(self):
        fmt_str = '0'
        if self.childs:
            fmt_str = str(len(self.childs))
        return 'Thread(#children : {})'.format(fmt_str)

    def get_children(self, children):
        ''' provides mapping of thead's children if exists'''
        if children:
            return [ElementType(c) for c in children]


class ElementType:
    ''' A thread's children content object '''
    def __init__(self, data):
        self.kind = data['kind']
        self.__data = data

    def __getattr__(self, key):
        ''' dynamic attribute accessment '''
        try:
            return self.__data['data'][key]
        except KeyError:
            raise

    def __repr__(self):
        ''' create kind dependent representation '''
        if self.kind == 't1':
            return 'ElementType(t1, {})'.format(reprlib.repr(self.body))
        elif self.kind == 't3':
            return 'ElementType(t3, {})'.format(reprlib.repr(self.title))
        else:
            return 'ElementType({})'.format(self.kind)


class ChildScanner:
    ''' create a convenient stream of child members from current level '''
    def __init__(self, listing):
        self.listing = [listing]

    def __iter__(self):
        ''' obtain childs at current thread level '''
        chain = [a.childs for a in self.listing if a.childs]
        return itertools.chain.from_iterable(chain)


class CommentScanner(ChildScanner):
    ''' create a convenient stream of comments from all levels '''
    def __init__(self, listing):
        super().__init__(listing)

    def __iter__(self):
        ''' traverse the complete tree and obtain all comments '''
        yield from super().__iter__()
        while True:
            # loop over children, if any has a reply add thread to next layer
            # you can call the pep8 police but I will resist for readability
            next_layer = [Thread(c.replies) for c in super().__iter__() if c.replies]
            if next_layer:
                self.listing = next_layer
                yield from super().__iter__()
            else:
                break


if __name__ == '__main__':
    import json
    jsons = []
    for f in ['all_articles.json', 'tree1.json', 'tree2.json']:
        f = '..\\data\\' + f
        with open(f, 'r') as fr:
            jsons.append(json.loads(fr.read()))
    articles, tree1, tree2 = jsons

    # iterate over the articles
    for i in ChildScanner(Thread(articles)):
        print(i)

    # traverse comment tree > seven iterations
    tree1Thread = Thread(tree1[1])
    for j in CommentScanner(tree1Thread):
        print(j)

    # empty comment tree > zero iterations
    tree2Thread = Thread(tree2[1])
    for k in CommentScanner(tree2Thread):
        print(k)
