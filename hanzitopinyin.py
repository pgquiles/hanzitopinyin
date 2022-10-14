#!/usr/bin/env python3

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import os
import argparse
import pysrt
from xpinyin import Pinyin


def hanzi_to_pinyin(input, output, format, tones):
    # Use a breakpoint in the code line below to debug your script.
    subs = pysrt.open(input)
    p = Pinyin()
    for sub in subs:
        my_pinyin: str
        my_text: str

        if sub and sub.text:
            my_text = sub.text
            my_pinyin = p.get_pinyin(my_text, tone_marks=tones)

        if format == 1:
            sub.text = my_pinyin
        elif format == 2:
            sub.text = my_text + '\n' +  my_pinyin

    subs.save(output)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", type=str, help="Output file", action="store")
    parser.add_argument("-f", "--format", type=int, help="Destination format. 1=pinyin (default), 2=hanzi+pinyin",
                        action="store", default=1)
    parser.add_argument("-t", "--tones", help="Tones: 1=marks (default), 2=numbers", action="store", default=1)
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Verbose output, showing intermediate steps")
    parser.add_argument("file", type=str, help="Input SRT file")
    args = parser.parse_args()

    output = ''
    if args.output:
        output = args.output
    else:
        output = os.path.splitext(args.input)[0] + '.zh_CN-pinyin.srt'

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

    hanzi_to_pinyin(args.file, args.output, args.format, args.tones)
