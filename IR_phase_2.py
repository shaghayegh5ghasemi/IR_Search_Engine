from __future__ import unicode_literals
from hazm import *
import pandas
from pathlib import Path
from datetime import datetime
import math
import json

def isConstructed():
    path_to_file = 'Positional_Index.json'
    path = Path(path_to_file)
    if path.is_file():
        return True
    return False

class PositionalIndex:
    def __init__(self):
        self.pos_idx = {}

    def add_doc(self, id, tokens):
        words = []
        for w in set(tokens):
            positions = [i + 1 for i, x in enumerate(tokens) if x == w]
            words.append([w, positions])

        for w in words:
            if w[0] not in self.pos_idx.keys():
                # w[0] --> token, w[1] --> positions, tf = len(w[1])
                # each posting = [ id, positions, tf, tf-idf ], tf-idf will be appended after the total construction
                postings = [[id, w[1], 1 + math.log10(len(w[1]))]]
                self.pos_idx[w[0]] = postings
            else:
                self.pos_idx[w[0]].append([id, w[1], 1 + math.log10(len(w[1]))])

    def calculate_tfidf(self):
        pass

    def save_index(self):
        with open('Positional_Index.json', 'w') as convert_file:
            convert_file.write(json.dumps(self.pos_idx))  # save the index to a file


if __name__ == '__main__':
    start_time = datetime.now()
    # get docs
    excel_data_df = pandas.read_excel('IR1_7k_news.xlsx', sheet_name='Sheet1')
    docs = excel_data_df['content'].tolist()
    docs_titles = excel_data_df['title'].tolist()

    if isConstructed():
        # load positional index
        with open('Positional_Index.json') as json_file:
            positional_index = json.load(json_file)
    else:
        positional_index = PositionalIndex()
        normalizer = Normalizer()
        stopwordslist = set(stopwords_list())
        stopwordslist.update(
            ['.', ':', '?', '!', '/', '//', '*', '[', ']', '{', '}', ';', '\'', '\"', '(', ')', '', '،', '؛'])
        lemmatizer = Lemmatizer()
        stemmer = Stemmer()
        for i in range(len(docs)):
            normalized_doc = normalizer.normalize(docs[i])
            temp_token = word_tokenize(normalized_doc)
            tokens = [token for token in temp_token if token not in stopwordslist]
            for i in range(len(tokens)):
                tokens[i] = lemmatizer.lemmatize(tokens[i])
                tokens[i] = stemmer.stem(tokens[i])
            positional_index.add_doc(i, tokens)
        positional_index.save_index()

    end_time = datetime.now()
    print('Duration: {}'.format(end_time - start_time))

