import openpyxl
from pathlib import Path
from hazm import *
import json

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
    documents = [] #extract contents and their title from .xlsx file
    for i in range(1, 4):
        documents.append(Document(i, content[i].value, title[i].value))
    return documents

# this function prepossesses the document: tokenize, normalize, stemming, delete stop words
def preprocess(raw_document):
    normalizer = Normalizer()
    stemmer = Stemmer()
    lemmatizer = Lemmatizer()
    stopwordslist = set(stopwords_list())
    tokens = []
    words = word_tokenize(normalizer.normalize(raw_document.content))
    for j in range(len(words)):
        if (words[j] not in stopwordslist):
            lemmatizer.lemmatize(words[j])
            stemmer.stem(words[j])
            # my tokens consists of: term, docID, position in the document
            tokens.append([words[j], raw_document.id, [j + 1]])
    return tokens

def positionalIndex(pos_idx, tokens):
    # t[0] = word, t[1] = docID, t[2] = list of position
    for t in tokens:
        if t[0] not in pos_idx.keys():
            pos_idx[t[0]] = [(t[1], t[2])]
        else:
            temp = pos_idx[t[0]]
            flag = 0
            for element in temp:
                if element[0] == t[1]: # if the word occurs multiple times in a document append the next position
                    element[1].append(t[2][0])
                    flag = 1
                    break
            if flag == 0: # the repeated word occured in a new document
                temp.append((t[1], t[2]))
            pos_idx[t[0]] = temp
    return pos_idx

def isConstructed():
    pass

if __name__ == '__main__':
    if isConstructed():
        pass
    else:
        documentCollection = getDocuments()
        pos_idx = {} # our positional index
        for document in documentCollection:
            tokens = preprocess(document)
            pos_idx = positionalIndex(pos_idx, tokens)
        with open('Positional_Index.json', 'w') as convert_file:
            convert_file.write(json.dumps(pos_idx)) #save the index to a file
    #Opening JSON file
    # with open('Positional_Index.json') as json_file:
    #     data = json.load(json_file)
    #
    #     # Print the type of data variable
    #     print("Type:", type(data))
    #
    #     # Print the data of dictionary
    #     print(data["اظهار"])



