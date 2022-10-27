#!/usr/bin/env python3

import os
import argparse
import deepl
import pysrt
from xpinyin import Pinyin
import configparser
import glob
from os import walk
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET

def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
                       os.path.relpath(os.path.join(root, file),
                                       os.path.join(path, '.')))


def hanzi_to_pinyin(my_input, my_output, my_format, my_tones, my_translator, extension):
    if extension == ".srt":
        hanzi_to_pinyin_srt(my_input, my_output, my_format, my_tones, my_translator)
    elif extension == ".txt":
        hanzi_to_pinyin_txt(my_input, my_output, my_format, my_tones, my_translator)
    elif extension == ".docx":
        hanzi_to_pinyin_docx(my_input, my_output, my_format, my_tones, my_translator)
    else:
        print("ERROR: unsupported file type.")
        print("Go to https://github.com/pgquiles/hanzitopinyin/issues and open an issue to"
              "request support for more file types.")
        exit(1)


def hanzi_to_pinyin_srt(my_input, my_output, my_format, my_tones, my_translator):
    # Use a breakpoint in the code line below to debug your script.
    subs = pysrt.open(my_input)
    p = Pinyin()
    for sub in subs:
        my_pinyin: str
        my_text: str

        if sub and sub.text:
            my_text = sub.text
            my_pinyin = p.get_pinyin(my_text, tone_marks=my_tones)

        if my_format == 1:
            sub.text = my_pinyin
        elif my_format == 2:
            sub.text = my_text + '\n' + my_pinyin
        elif my_format == 3:
            my_english = my_translator.translate_text(my_text, source_lang="ZH", target_lang="EN-US")
            sub.text = my_english.text + '\n' + my_text + '\n' + my_pinyin

    subs.save(my_output)


def hanzi_to_pinyin_txt(my_input, my_output, my_format, my_tones, my_translator):
    # Use a breakpoint in the code line below to debug your script.

    with open(my_input, 'r') as reader:
        p = Pinyin()
        output_text = []

        for my_text in reader.readlines():
            my_pinyin: str

            if my_text:
                my_pinyin = p.get_pinyin(my_text, tone_marks=my_tones)

            if my_format == 1:
                output_text.append(my_pinyin)
            elif my_format == 2:
                output_text.append(my_text + my_pinyin + '\n')
            elif my_format == 3:
                my_english = my_translator.translate_text(my_text, source_lang="ZH", target_lang="EN-US")
                output_text.append(my_english.text + my_text + my_pinyin + '\n')

        try:
            with open(my_output, 'w') as writer:
                writer.writelines(output_text)
        except OSError:
            print("ERROR: cannot open " + my_output + " to write in it. Check permissions.")
            exit(1)


def hanzi_to_pinyin_docx(my_input, my_output, my_format, my_tones, my_translator):
    tempdir = tempfile.TemporaryDirectory()

    with zipfile.ZipFile(my_input, 'r') as zip_ref:
        zip_ref.extractall(tempdir.name)
        res = []
        for (dir_path, dir_names, file_names) in walk(tempdir.name):
            res.extend(file_names)
        print(res)

        pinyinize_word_xml(tempdir.name, "document.xml", my_format, my_tones, my_translator)

        headers = glob.glob(os.path.join(tempdir.name, "word", "header*.xml"))
        for header in headers:
            pinyinize_word_xml(tempdir.name, header, my_format, my_tones, my_translator)

        footers = glob.glob(os.path.join(tempdir.name, "word", "footer*.xml"))
        for footer in footers:
            pinyinize_word_xml(tempdir.name, footer, my_format, my_tones, my_translator)

        with zipfile.ZipFile(my_output, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipdir(tempdir.name, zipf)

def pinyinize_word_xml(dir, file, my_format, my_tones, my_translator):
    tree = ET.parse(os.path.join(dir, "word", file))
    namespace = {'w': "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    texts = tree.findall('.//w:t', namespace)
    p = Pinyin()
    for text in texts:
        my_pinyin = p.get_pinyin(text.text, tone_marks=my_tones)
        text.text = my_pinyin
    tree.write(os.path.join(dir, "word", file))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", nargs='?', type=str, help="Output file", action="store", default="")
    parser.add_argument("-f", "--format", type=int,
                        help="Destination format. 1=Pinyin (default), 2=Hanzi+Pinyin, 3=English+Hanzi+Pinyin",
                        action="store", default=1)
    parser.add_argument("-t", "--tones", type=int, help="Tones: 1=marks (default), 2=numbers", action="store",
                        default=1)
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose output, showing intermediate steps")
    parser.add_argument("file", type=str, help="Input SRT file")
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print("ERROR: need file input")
        exit(1)

    extension = os.path.splitext(args.file)[1]

    output = ""
    translator = ""
    if args.output:
        output = args.output
    else:
        if args.format == 1:
            output = os.path.splitext(args.file)[0].replace('.zh_CN-hanzi', '') + '.zh_CN-pinyin' + extension
        elif args.format == 2:
            output = os.path.splitext(args.file)[0].replace('.zh_CN-hanzi', '') + '.zh_CN-hanzi+pinyin' + extension
        elif args.format == 3:
            output = os.path.splitext(args.file)[0].replace('.zh_CN-hanzi',
                                                            '') + '.zh_CN-english+hanzi+pinyin' + extension
            config = configparser.ConfigParser()
            config.read("hanzitopinyin.conf")
            auth_key = config['deepl']['auth_key']
            if auth_key == "":
                print("ERROR: Translation with DeepL requested but no authentication key provided. "
                      "Please edit hanzitopinyin.conf and add it.")
                exit(1)
            translator = deepl.Translator(auth_key)

    tones = ''
    if args.tones:
        if args.tones == 1:
            tones = 'marks'
        elif args.tones == 2:
            tones = 'numbers'
        else:
            print("Unknown tone format" + args.tones)
            exit(-1)
    else:
        tones = 'marks'

    hanzi_to_pinyin(args.file, output, args.format, tones, translator, extension)

    if args.format == 3 and args.verbose:
        usage = translator.get_usage()
        if usage.any_limit_reached:
            print('ERROR DeepL translation limit reached.')
            exit(1)
        if usage.character.valid:
            print(f"Character usage: {usage.character.count} of {usage.character.limit}")
        if usage.document.valid:
            print(f"Document usage: {usage.document.count} of {usage.document.limit}")
