import re
import numpy as np
from collections import Counter


PUNCT_POS = (
    'Pвнутр', 'Pгран', 'Pтире', 'Pкавычки', 'NL',
)


def dialog_fraction(parsed_json):
    frac = np.zeros(shape=(len(parsed_json), 1))
    for i, d in enumerate(parsed_json):
        frac[i] = d.count('NL Pтире') / d.count('NL')
    return frac


def avg_sent_len_one(parsed_json, punct_pos=PUNCT_POS):
    sentences = re.split('NL|Pгран', parsed_json)
    sentences = [[w for w in s.split() if w not in punct_pos]
                 for s
                 in sentences]
    sentences_len = [len(s) for s in sentences if len(s) > 0]
    return sum(sentences_len) / len(sentences_len)


def avg_sent_len_many(parsed_jsons):
    return np.array([avg_sent_len_one(json) for json in parsed_jsons])


def type_token_ratio(json):
    vocabulary = Counter()
    for line in json:
        if 'analysis' in line and line['analysis']:
            if 'lex' in line['analysis'][0]:
                word = line['analysis'][0]['lex']
                vocabulary[word] += 1
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
            if line['text'].lower() not in rare_words:
                n_rare += 1
            elif (line['analysis'] and
                  'lex' in line['analysis'][0] and
                  line['analysis'][0]['lex'] not in rare_words):
                n_rare += 1
    return n_rare / n_all
