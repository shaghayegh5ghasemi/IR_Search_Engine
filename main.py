import openpyxl
from pathlib import Path
from hazm import *
import json
from datetime import datetime
import sys


class Document():
    def __init__(self, id, content, title):
        self.id = id
        self.content = content
        self.title = title


# this function collects the documents info from the excel file
def getDocuments():
    raw_doc_path = Path('IR1_7k_news.xlsx')
    raw_doc = openpyxl.load_workbook(raw_doc_path)
    doc_sheet = raw_doc.active
    content = doc_sheet['A']
    title = doc_sheet['C']
    documents = []  # extract contents and their title from .xlsx file
    for i in range(1, len(content)):
        documents.append(Document(i, content[i].value, title[i].value))
    return documents


# this function prepossesses the document: tokenize, normalize, stemming, delete stop words
def preprocess(raw_document):
    normalizer = Normalizer()
    stemmer = Stemmer()
    lemmatizer = Lemmatizer()
    stopwordslist = set(stopwords_list())
    tokens = []
    words = []
    words_temp = word_tokenize(normalizer.normalize(raw_document.content))
    for word in words_temp:
        if word not in stopwordslist:
            temp = lemmatizer.lemmatize(word)
            temp = stemmer.stem(temp)
            words.append(temp)
    for word in set(words):
        # my tokens consists of: term, positions in the document
        positions = [i + 1 for i, x in enumerate(words) if x == word]
        tokens.append([word, positions, len(positions)])
    return tokens

def positionalIndex(pos_idx, id, tokens):
    # t[0] = word, t[1] = list of position, t[2] = number of repeatitions
    for t in tokens:
        if t[0] not in pos_idx.keys():
            pos_idx[t[0]] = [t[2], [(id, t[1], t[2])]]
        else:
            pos_idx[t[0]][0] += t[2]
            pos_idx[t[0]][1].append((id, t[1], t[2]))


# check if the index is constructed before or not
def isConstructed():
    path_to_file = 'Positional_Index.json'
    path = Path(path_to_file)
    if path.is_file():
        return True
    return False

def retrievDoc(word, pos_idx):
    docIDs = []
    if word in pos_idx.keys():
        postings_list = pos_idx[word][1]
        for i in range(len(postings_list)):
            docIDs.append(postings_list[i][0])
    else:
        return None
    return docIDs, postings_list

def postingIntersect(p1, p2, k):
    answer = []
    len1 = len(p1)
    len2 = len(p2)
    i = j = 0
    while i != len1 and j != len2:
        if p1[i][0] == p2[j][0]:
            l = []
            pp1 = p1[i][1]  # pp1 <- positions(p1)
            pp2 = p2[j][1] # pp2 <- positions(p2)

            plen1 = len(pp1)
            plen2 = len(pp2)
            ii = jj = 0
            while ii != plen1:
                while jj != plen2:
                    if abs(pp1[ii] - pp2[jj]) <= k:  # if (|pos(pp1) - pos(pp2)| <= k)
                        l.append(pp2[jj])  # l.add(pos(pp2))
                    elif pp2[jj] > pp1[ii]:  # else if (pos(pp2) > pos(pp1))
                        break
                    jj += 1  # pp2 <- next(pp2)
                while l != [] and abs(l[0] - pp1[ii]) > k:  # while (l != () and |l(0) - pos(pp1)| > k)
                    l.remove(l[0])  # delete(l[0])
                for ps in l:  # for each ps in l
                    answer.append([p1[i][0], [pp1[ii], ps]])  # add answer(docID(p1), pos(pp1), ps)
                ii += 1  # pp1 <- next(pp1)
            i += 1  # p1 <- next(p1)
            j += 1  # p2 <- next(p2)
        elif p1[i][0] < p2[j][0]:  # else if (docID(p1) < docID(p2))
            i += 1  # p1 <- next(p1)
        else:
            j += 1  # p2 <- next(p2)
    return answer

if __name__ == '__main__':

    documentCollection = getDocuments()

    if isConstructed():
        # load positional index
        with open('Positional_Index.json') as json_file:
            pos_index = json.load(json_file)
    else: # constuct the index
        pos_idx = {}  # our positional index
        for document in documentCollection:
            tokens = preprocess(document)
            positionalIndex(pos_idx, document.id, tokens)
        with open('Positional_Index.json', 'w') as convert_file:
            convert_file.write(json.dumps(pos_idx))  # save the index to a file

    # respond to query
    normalizer = Normalizer()
    stemmer = Stemmer()
    lemmatizer = Lemmatizer()
    stopwordslist = set(stopwords_list())
    while (True):
        query = input("Query/Enter F to finish: ")
        start_time = datetime.now()
        if(query == 'f' or query == 'F'):
            sys.exit()
        # query preprocessing
        query_words_temp = word_tokenize(normalizer.normalize(query))
        query_words = []
        for word in query_words_temp:
            if word not in stopwordslist:
                temp = lemmatizer.lemmatize(word)
                temp = stemmer.stem(temp)
                query_words.append(temp)
        # single word query
        if (len(query_words) == 1):
            if retrievDoc(query_words[0], pos_index) == None:
                print("No answer")
                continue
            docIDs, _ = retrievDoc(query_words[0], pos_index)
            print("")
            print("Title of one related news: ")
            print(documentCollection[docIDs[0] - 1].title)
            sections = sent_tokenize(documentCollection[docIDs[0] - 1].content)
            for i in sections:
                if query in i:
                    print(i)
            print("")
        # multiple word query
        if (len(query_words) > 1):
            postings_lists = []
            for word in query_words:
                _ , posting = retrievDoc(word, pos_index)
                postings_lists.append(posting)
            w = 0
            binary_response = []
            while (w < len(postings_lists) - 1):
                binary_response.append(postingIntersect(postings_lists[w], postings_lists[w+1], 1))
                w += 1

            IDs = []
            for i in  range(len(binary_response)):
                temp = []
                for j in binary_response[i]:
                    temp.append(j[0])
                IDs.append(temp)
            response = list(set.intersection(*map(set, IDs)))
            print("")
            print("Title of one related news: ")
            print(documentCollection[response[0] - 1].title)
            sections = sent_tokenize(documentCollection[response[0] - 1].content)
            for i in sections:
                if query in i:
                    print(i)
        end_time = datetime.now()
        print('Duration: {}'.format(end_time - start_time))






