# -*- coding: utf-8 -*-
import sys
import os
import re
from binascii import b2a_hex
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
from pdfminer.converter import PDFPageAggregator
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
import sys
import logging
import six
import pdfminer.settings
pdfminer.settings.STRICT = False
import pdfminer.high_level
import pdfminer.layout
from pdfminer.image import ImageWriter

# class P2T():

#     def __init__(self):
#         return

#     def with_pdf(self, pdf_doc, fn, pdf_pwd, *args):
#         result = ""
#         try:
#             fp = open(pdf_doc, 'rb')
#             parser = PDFParser(fp)
#             doc = PDFDocument(parser, pdf_pwd)
#             parser.set_document(doc)
#             if doc.is_extractable:
#                 result = fn(doc, *args)

#             fp.close()
#         except:
#             pass
#         return result

#     def _parse_toc(self, doc):
#         toc = []
#         try:
#             outlines = doc.get_outlines()
#             for (level, title, dest, a, se) in outlines:
#                 toc.append((level, title))
#         except:
#             pass
#         return toc

#     def get_toc(self, pdf_doc, pdf_pwd=''):
#         return self.with_pdf(pdf_doc, self._parse_toc, pdf_pwd)

#     def write_file(self, folder, filename, filedata, flags='w'):
#         result = false
#         if os.path.isdir(folder):
#             try:
#                 file_obj = open(os.path.join(folder, filename), flags)
#                 file_obj.write(filedata)
#                 file_obj.close()
#                 result = True
#             except IOErro:
#                 pass
#         return result

#     def determine_image_type(self, stream_first_4_bytes):
#         file_type = None
#         bytes_as_hex = b2a_hex(stream_first_4_bytes)
#         if bytes_as_hex.startswith('ffd8'):
#             file_type = '.jpeg'
#         elif bytes_as_hex == '89504e47':
#             file_type = ',png'
#         elif bytes_as_hex == '47494638':
#             file_type = '.gif'
#         elif bytes_as_hex.startswith('424d'):
#             file_type = '.bmp'
#         return file_type

#     def save_image(self, it_image, page_number, images_folder):
#         result = None
#         if it_image.stream:
#             file_stream = it_image.stream.get_rawdata()
#             if file_stream:
#                 file_ext = self.determine_image_type(file_stream[0:4])
#                 print file_ext
#                 if file_ext:
#                     file_name = ''.join(
#                         [str(page_number), '_', it_image.name, file_ext])
#                     if self.write_file(
#                             images_folder, file_name, file_stream, flags='wb'):
#                         result = file_name
#         return result

#     def to_bytestring(self, s, enc='utf-8'):
#         if s:
#             if isinstance(s, str):
#                 return s
#             else:
#                 return s.encode(enc)

#     def update_page_text_hash(self, h, lt_obj, pct=0.1):
#         x0 = lt_obj.bbox[0]
#         x1 = lt_obj.bbox[2]
#         key_found = False
#         for k, v in h.items():
#             hash_x0 = k[0]
#             if x0 >= (hash_x0 * (1.0 - pct)) and (hash_x0 * (1 + pct)) >= x0:
#                 hash_x1 = k[1]
#                 if x1 >= (hash_x1 * (1 - pct)) and (hash_x1 * (1 + pct)) >= x1:
#                     key_found = True
#                     v.append(self.to_bytestring(lt_obj.get_text()))
#                     h[k] = v
#         if not key_found:
#             h[(x0, x1)] = [self.to_bytestring(lt_obj.get_text())]
#         return h

#     def parse_lt_objs(self, lt_objs, page_number, images_folder, text=[]):
#         text_content = []
#         page_text = {}
#         result = ""
#         for lt_obj in lt_objs:
#             if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
#                 page_text = self.update_page_text_hash(page_text, lt_obj)
#         # elif isinstance(lt_obj,LTImage):
#         #   saved_file = self.save_image(lt_obj,page_number,images_folder)
#         #   if saved_file:
#         #       text_content.append('<img src="' + os.path.join(images_folder,saved_file)+'"/>')
#         #   else:
#         #       print >> sys.stderr,"error saving image on page", page_number,lt_obj.__repr__
#             elif isinstance(lt_obj, LTFigure):
#                 text_content.append(
#                     self.parse_lt_objs(lt_obj, page_number, images_folder,
#                                        text_content))

#         for k, v in sorted([(key, value)
#                             for (key, value) in page_text.items()]):
#             text_content.append(''.join(v))
#         return result.join(text_content)

#     def _parse_pages(self, doc, images_folder):
#         rsrcmgr = PDFResourceManager()
#         laparams = LAParams()
#         device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#         interpreter = PDFPageInterpreter(rsrcmgr, device)

#         text_content = []
#         for i, page in enumerate(PDFPage.create_pages(doc)):
#             interpreter.process_page(page)
#             layout = device.get_result()
#             text_content.append(
#                 self.parse_lt_objs(layout, (i + 1), images_folder))
#         return text_content

#     def get_pages(self, pdf_doc, pdf_pwd='', images_folder='/tmp'):
#         return self.with_pdf(pdf_doc, self._parse_pages, pdf_pwd,
#                              *tuple([images_folder]))

# tmp = P2T()
# #os.chdir('C:\Users\liwei\Desktop\python\scrapy\programs\自动下载数据')
# a = open('./data/result.txt', 'a')
# removeNoneLine = re.compile(r'\n[\s|]*\n')
# for i in tmp.get_pages('./data/simple2.pdf'):
#     i = re.sub(removeNoneLine, "\n", i)
#     a.write(i)
# a.close()


def extract_text(
        files=[],
        outfile='-',
        _py2_no_more_posargs=None,  # Bloody Python2 needs a shim
        no_laparams=False,
        all_texts=None,
        detect_vertical=None,  # LAParams
        word_margin=None,
        char_margin=None,
        line_margin=None,
        boxes_flow=None,  # LAParams
        output_type='text',
        codec='utf-8',
        strip_control=False,
        maxpages=0,
        page_numbers=None,
        password="",
        scale=1.0,
        rotation=0,
        layoutmode='normal',
        output_dir=None,
        debug=False,
        disable_caching=False,
        **other):
    if _py2_no_more_posargs is not None:
        raise ValueError("Too many positional arguments passed.")
    if not files:
        raise ValueError("Must provide files to work upon!")

    # If any LAParams group arguments were passed, create an LAParams object and
    # populate with given args. Otherwise, set it to None.
    if not no_laparams:
        laparams = pdfminer.layout.LAParams()
        for param in ("all_texts", "detect_vertical", "word_margin",
                      "char_margin", "line_margin", "boxes_flow"):
            paramv = locals().get(param, None)
            if paramv is not None:
                setattr(laparams, param, paramv)
    else:
        laparams = None

    imagewriter = None
    if output_dir:
        imagewriter = ImageWriter(output_dir)

    if output_type == "text" and outfile != "-":
        for override, alttype in ((".htm", "html"), (".html", "html"),
                                  (".xml", "xml"), (".tag", "tag")):
            if outfile.endswith(override):
                output_type = alttype

    if outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            codec = 'utf-8'
    else:
        outfp = open(outfile, "wb")

    for fname in files:
        with open(fname, "rb") as fp:
            pdfminer.high_level.extract_text_to_fp(fp, **locals())
    return outfp


# main
def main(args=None):
    import argparse
    P = argparse.ArgumentParser(description=__doc__)
    P.add_argument(
        "files", type=str, default=None, nargs="+", help="Files to process.")
    P.add_argument(
        "-d",
        "--debug",
        default=False,
        action="store_true",
        help="Debug output.")
    P.add_argument(
        "-p",
        "--pagenos",
        type=str,
        help=
        "Comma-separated list of page numbers to parse. Included for legacy applications, use -P/--page-numbers for more idiomatic argument entry."
    )
    P.add_argument(
        "--page-numbers",
        type=int,
        default=None,
        nargs="+",
        help=
        "Alternative to --pagenos with space-separated numbers; supercedes --pagenos where it is used."
    )
    P.add_argument(
        "-m", "--maxpages", type=int, default=0, help="Maximum pages to parse")
    P.add_argument(
        "-P",
        "--password",
        type=str,
        default="",
        help="Decryption password for PDF")
    P.add_argument(
        "-o",
        "--outfile",
        type=str,
        default="-",
        help="Output file (default/'-' is stdout)")
    P.add_argument(
        "-t",
        "--output_type",
        type=str,
        default="text",
        help="Output type: text|html|xml|tag (default is text)")
    P.add_argument(
        "-c", "--codec", type=str, default="utf-8", help="Text encoding")
    P.add_argument("-s", "--scale", type=float, default=1.0, help="Scale")
    P.add_argument(
        "-A",
        "--all-texts",
        default=None,
        action="store_true",
        help="LAParams all texts")
    P.add_argument(
        "-V",
        "--detect-vertical",
        default=None,
        action="store_true",
        help="LAParams detect vertical")
    P.add_argument(
        "-W",
        "--word-margin",
        type=float,
        default=None,
        help="LAParams word margin")
    P.add_argument(
        "-M",
        "--char-margin",
        type=float,
        default=None,
        help="LAParams char margin")
    P.add_argument(
        "-L",
        "--line-margin",
        type=float,
        default=None,
        help="LAParams line margin")
    P.add_argument(
        "-F",
        "--boxes-flow",
        type=float,
        default=None,
        help="LAParams boxes flow")
    P.add_argument(
        "-Y",
        "--layoutmode",
        default="normal",
        type=str,
        help="HTML Layout Mode")
    P.add_argument(
        "-n",
        "--no-laparams",
        default=False,
        action="store_true",
        help="Pass None as LAParams")
    P.add_argument("-R", "--rotation", default=0, type=int, help="Rotation")
    P.add_argument(
        "-O", "--output-dir", default=None, help="Output directory for images")
    P.add_argument(
        "-C",
        "--disable-caching",
        default=False,
        action="store_true",
        help="Disable caching")
    P.add_argument(
        "-S",
        "--strip-control",
        default=False,
        action="store_true",
        help="Strip control in XML mode")
    A = P.parse_args(args=args)

    if A.page_numbers:
        A.page_numbers = set([x - 1 for x in A.page_numbers])
    if A.pagenos:
        A.page_numbers = set([int(x) - 1 for x in A.pagenos.split(",")])

    imagewriter = None
    if A.output_dir:
        imagewriter = ImageWriter(A.output_dir)

    if six.PY2 and sys.stdin.encoding:
        A.password = A.password.decode(sys.stdin.encoding)

    if A.output_type == "text" and A.outfile != "-":
        for override, alttype in ((".htm", "html"), (".html", "html"),
                                  (".xml", "xml"), (".tag", "tag")):
            if A.outfile.endswith(override):
                A.output_type = alttype

    if A.outfile == "-":
        outfp = sys.stdout
        if outfp.encoding is not None:
            # Why ignore outfp.encoding? :-/ stupid cathal?
            A.codec = 'utf-8'
    else:
        outfp = open(A.outfile, "wb")

    ## Test Code
    outfp = extract_text(**vars(A))
    outfp.close()
    return 0


if __name__ == '__main__':
    sys.exit(main())
