import pandas as pd
import numpy as np

from sklearn.feature_extraction.text import CountVectorizer


def get_author_id(fbusta_id, catalog):
    return catalog.loc[catalog['fbusta_id'] == fbusta_id]['author_id'].item()


def get_author_name(fbusta_id, catalog):
    # return catalog.loc[catalog['fbusta_id'] == book_id]['author_name'].item() + \
    return catalog.loc[catalog['fbusta_id'] == fbusta_id]['author_surname'].item()


def get_book_name(fbusta_id, catalog):
    return catalog.loc[catalog['fbusta_id'] == fbusta_id]['book_title'].item()


def get_book_id(fbusta_id, catalog):
    return catalog.loc[catalog['fbusta_id'] == fbusta_id]['book_id'].item()


def train_test_split(data, authors, test_size=.2, mod='grouped',
                     random_state=17, return_idx=False):
    np.random.seed(random_state)
    uniques = np.unique(authors)
    if mod == 'grouped':
        test_authors = np.random.choice(
                uniques, int(len(uniques)*test_size), replace=False
        )
        test_idx = np.hstack(
                [np.where(authors == a)[0] for a in test_authors]
        )
        train_idx = np.array(
                [i for i in range(len(authors)) if i not in test_idx]
        )
    elif mod == 'stratified' or mod == 's':
        dropped = []
        test_idx = []
        train_idx = []
        for author in uniques:
            a_idx = np.where(authors == author)[0]
            if len(a_idx) < 3:
                dropped.append(a_idx)
                continue
            if len(a_idx) % 2 != 0:
                bi = a_idx[0]
                train_idx.append(bi)
                test_idx.append(bi)
                a_idx = a_idx[1:]
            a_idx_train = np.random.choice(a_idx, len(a_idx) // 2,
                                           replace=False)
            a_idx_test = np.array([i for i in a_idx if i not in a_idx_train])
            train_idx.extend(a_idx_train)
            test_idx.extend(a_idx_test)
        test_idx = np.array(test_idx)
        train_idx = np.array(train_idx)
    fraction = len(test_idx) / len(authors)
    print("test_fraction:", fraction)
    if return_idx:
        return train_idx, test_idx
    return data[train_idx], authors[train_idx], \
        data[test_idx], authors[test_idx]


def count_n_grams(texts, n=3, stopgrams=[], max_features=None):
    cv = CountVectorizer(
        ngram_range=(n, n),
        token_pattern=u"(?u)\\b\\w+\\b",
        max_features=max_features
    )
    cv.fit(texts)
    for s in stopgrams:
        if s in cv.vocabulary_:
            del cv.vocabulary_[s]
    for i, s in enumerate(sorted(cv.vocabulary_)):
        cv.vocabulary_[s] = i
    transformed = cv.transform(texts)
    return transformed, cv


def metric(M):
    return lambda x, y: (x-y).dot(M).dot(x-y)


def r_precision_m(matrix, authors, verbose=False):
    result = []
    for col in matrix:
        true_R = sum(authors == authors[col]) - 1
        closest = authors[matrix[col].argsort()][1:true_R+1]
        rp = sum(closest == authors[col]) / true_R
        if verbose:
            print(authors[col], closest, true_R, rp)
        result.append(rp)
    return result


def r_precision10_m(matrix, authors, verbose=False):
    result = []
    for col in matrix:
        true_R = sum(authors == authors[col]) - 1
        closest = authors[matrix[col].argsort()][1:11]
        rp = sum(closest == authors[col]) / true_R
        if verbose:
            print(authors[col], closest, true_R, rp)
        result.append(rp)
    return result
