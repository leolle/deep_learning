# from graph_upload import UploadGraph
class IterateFileRex(object):

    def __init__(self, path, rex):
        self._fw = open(path, 'r')
        self.string = self._fw.read()
        self.rex = rex
        # self.last_span = self.search(self._fw).span()[0]

    # def __iter__(self):
    #     return self

    def read(self):
        #        matched = self.rex.search(self.string,self.last_span)
        for matched in re.finditer(self.rex, self.string):
            # self.last_span = matched.span()[1]
            yield matched

    def readlines(self):
        """ Line iterator """

        for line in self._fw:
            yield line


a = IterateFileRex(category_link_path, wiki_category_link_re)
