import base64
import zlib

from singleton import singleton

__author__ = 'feldsherov'


@singleton
class DirectIndex:
    class DirectIndexRecord:
        def __init__(self, row):
            url_id, b64_defl_sentences, img, summary, title = row.rstrip().split("\t")
            self.url_id = int(url_id)
            defl_sentences = base64.b64decode(b64_defl_sentences)
            self.sentences = zlib.decompress(defl_sentences).split("\n")
            self.img_url = self.get_value(img)
            self.summary = zlib.decompress(base64.b64decode(self.get_value(summary)))
            self.title = zlib.decompress(base64.b64decode(self.get_value(title)))

        def get_value(self, field):
            assert(" " in field)
            field1 = field.split(" ")[1]
            return field1 if field else None

    def __init__(self, path):
        self.index_file = open(path, "r")
        self.offset_dict = dict()

        offset = self.index_file.tell()
        while True:
            row = self.index_file.readline()
            if not row:
                break
            record = self.DirectIndexRecord(row)
            self.offset_dict[int(record.url_id)] = offset
            offset = self.index_file.tell()

    def record_by_id(self, url_id):
        offset = self.offset_dict[url_id]
        self.index_file.seek(offset)
        row = self.index_file.readline().rstrip()
        return self.DirectIndexRecord(row)

