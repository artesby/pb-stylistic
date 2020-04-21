import re
import numpy as np
from collections import Counter

mystem_pos = [
    'A', 'ADV', 'ADVPRO', 'APRO', 'ANUM',
    'COM', 'CONJ', 'INTJ', 'NUM',
    'PART', 'PR', 'S', 'SPRO',
    'V', 'Vприч', 'Vинф', 'Vдеепр', 'UNK'
]

punct_pos= [
    'Pвнутр', 'Pгран', 'Pтире', 'Pкавычки', 'NL',
]

tire = ['–', '—', '-']
newline = '\n'
Pborders = ['.', '!', '?', "…"]
Pquotes = ['"', "'", '«', '»', '<', '>']
nl = 'NL'
digit = 'Digit'
pgran = 'Pгран'
pvnutr = 'Pвнутр'
lat = 'LAT'

ALL_POS = [*mystem_pos, *punct_pos, digit, lat]


def pos_tagger(parsed_text):
    """ parsed_text = mystem output in [{},]"""
    pos_tags = []
    for line in parsed_text:
        pos = 'IDK'
        end_nl = False
        if 'analysis' in line:
# могут быть пустыми {... 'analysis': [] ...}
            if not line['analysis']:
                if re.match('[а-яА-Я]', line['text']):
                    pos = 'UNK'
                    pos_tags.append(pos)
                elif any(c.isalpha() for c in line['text']):
                    pos = 'LAT'
                    pos_tags.append(pos)
                else:
                    print('else', line)
                continue

            tags = re.split('[,=()"]',  line['analysis'][0]['gr'])
            pos = tags[0]
            if 'деепр' in tags:
                pos = 'Vдеепр'
            elif 'прич' in tags:
                pos = 'Vприч'
            elif 'инф' in tags:
                pos = 'Vинф'
            pos_tags.append(pos)

        else:
#значит знаки препинания либо числа.
            text = line['text']
            text = text.strip(' ')
            if text.endswith('\n'):
                end_nl = True
                text = text.rstrip('\n')
            if not text:
                if end_nl:
                    pos_tags.append('NL')
                continue

            elif re.match('[а-яА-Я]', text):
                pos = 'UNK'
                pos_tags.append(pos)
            elif any(c.isalpha() for c in line['text']):
                pos = 'LAT'
                pos_tags.append(pos)
            elif any(c.isdigit() for c in text):
                pos = 'Digit'
                pos_tags.append(pos)
            else:
                text = [c for l in text.split() for c in l]
                if not text:
                    print(line, 'whaa?')
                else:
                    for p in text:
                        if p in Pborders:
                            pos = 'Pгран'
                            pos_tags.append(pos)
                        elif p in Pquotes:
                            pos = 'Pкавычки'
                            pos_tags.append(pos)
                        elif p in tire:
                            pos = 'Pтире'
                            pos_tags.append(pos)
                        else:
                            pos = 'Pвнутр'
                            pos_tags.append(pos)
        if pos == 'IDK':
            print('idk', line)
        if end_nl:
            pos_tags.append('NL')
    return pos_tags


def dialog_fraction(pos_text):
    return pos_text.count('NL Pтире') / pos_text.count('NL')


def avg_sent_len(pos_text, punct_pos=punct_pos):
    sentences = [[w for w in s.split() if w not in punct_pos]
                 for s
                 in re.split('NL|Pгран', pos_text)]
    sentences_len = [len(s) for s in sentences if len(s) > 0]
    return sum(sentences_len) / len(sentences_len)


def type_token_ratio(parsed_text):
    vocabulary = Counter()
    for line in parsed_text:
        try:
            word = line['analysis'][0]['lex']
            vocabulary[word] += 1
        except:
            continue
    return len(vocabulary) / sum(vocabulary.values())


def is_russian_alpha(word):
    return re.match('[а-яА-Я]', str(word))


def rare_words_fraction(json, rare_words=None):
    rare_words = rare_words or set()
    n_rare = 0
    n_all = 0
    for line in json:
        if 'analysis' in line:
            n_all += 1
            if line['analysis']:
                if line['analysis'][0]['lex'] not in rare_words:
                    n_rare += 1
            elif line['text'].lower() not in rare_words:
                n_rare += 1
    return n_rare / n_all


def pos_fraction(pos_tags, keys=mystem_pos):
    c = Counter(pos_tags)
    p = sum(c.values())
    return [c[k] / p for k in keys]