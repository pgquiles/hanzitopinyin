# hanzitopinyin

Hanzi to pinyin converter for Simplified Chinese documents.

Currently supported:
* Text files (.txt)
* Microsoft Word 2007 and later documents (DOCX, i. e. OOXML format)
* Subtitles in SubRip (SRT) format

Makes use of a dictionary with the 25,500 most common hanzis.

Since I wrote this tool to study Chinese, it's possible to output the subtitles in 3 formats:
* 1: only pinyin
* 2: hanzi + pinyin
* 3: English + Hanzi + Pinyin

Option 3 uses DeepL to translate, which requires an API key. DeepL provides free API keys with some limitations but they should be enough for this tool. You must write the DeepL API key to the `hanzitopinyin.conf` file!!!
