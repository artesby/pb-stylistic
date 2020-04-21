from zipfile import ZipFile
from bounter import bounter
from tqdm import tqdm
from nltk import word_tokenize
from collections import Counter
import re
import multiprocessing as mp


def process_wrapper(t):
    name = ''.join(t)
    with ZipFile('plain_texts.zip') as z:
        with z.open(name, 'r') as f:
            x = [w.lower() for w in word_tokenize(f.read().decode('utf8')) if re.match('[а-яА-Я]', w)]
    return x

def run():
    gc = bounter(size_mb=2048)
    pool = mp.Pool(6)
    # jobs = []
    with ZipFile('plain_texts.zip') as z:
        names = z.namelist()
        size = 100
        chunks = (names[i::size] for i in range(size))
        i = 0
        for chunk in chunks:
            i += 1
            print(f'chunk {i}')
            jobs = []
            for name in chunk:
                jobs.append(pool.apply_async(process_wrapper, (name,)))

            for job in tqdm(jobs):
                gc.update(job.get())

    pool.close()
    
    with open('mfw.txt', 'w') as f:
        for tag, count in list(sorted(gc.iteritems(), key=lambda x: x[1], reverse=True)[:2000]):  
            f.write(f'{tag} {count} \n')  

if __name__ == "__main__":
    run()
    # gc = Counter()
    # with ZipFile('plain_texts.zip') as z:
    #     names = z.namelist()[:100]
    #     for n in names:
    #         with z.open(n, 'r') as f:
    #             gc.update(
    #                 [w.lower() for w in word_tokenize(f.read().decode('utf8')) if re.match('[а-яА-Я]', w)])
    # with open('mfw.txt2', 'w') as f:
    #     for tag, count in gc.most_common(2000):  
    #         f.write(f'{tag} {count} \n')


