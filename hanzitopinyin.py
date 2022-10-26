#!/usr/bin/env python3

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import sys
import argparse

import deepl
import pysrt
from xpinyin import Pinyin
import configparser


def hanzi_to_pinyin(my_input, my_output, my_format, my_tones, my_translator, extension):
    if extension == ".srt":
        print("Using SRT handler")
        hanzi_to_pinyin_srt(my_input, my_output, my_format, my_tones, my_translator)
    elif extension == ".txt":
        print("Using TXT handler")
        hanzi_to_pinyin_txt(my_input, my_output, my_format, my_tones, my_translator)
    elif extension == ".docx":
        print("Using DOCX handler")
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
    print("TODO")


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
