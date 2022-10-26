#!/usr/bin/env python3

# Converts SRT to TXT

import sys
import pysrt


if __name__ == '__main__':
    subs = pysrt.open(sys.argv[1])
    hanzi = []
    for sub in subs:
        if sub and sub.text:
            print(sub.text)
            hanzi.append(sub.text + '\n')

    with open(sys.argv[2], 'w+') as writer:
        writer.writelines(hanzi)
