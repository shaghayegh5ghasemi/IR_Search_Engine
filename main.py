import openpyxl
from pathlib import Path
from hazm import *

class Document():
    def __init__(self, id, content, title):
        self.id = id
        self.content = content
        self.title = title
    

# this function collects the documents info from the excel file
def get_documents():
    raw_doc_path = Path('IR1_7k_news.xlsx')
    raw_doc = openpyxl.load_workbook(raw_doc_path)
    doc_sheet = raw_doc.active
    content = doc_sheet['A']
    title = doc_sheet['C']
    documents = [] #extract contents and their title from .xlsx file
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
    words = word_tokenize(normalizer.normalize(raw_document.content))
    for j in range(len(words)):
        if (words[j] not in stopwordslist):
            lemmatizer.lemmatize(words[j])
            stemmer.stem(words[j])
            # my tokens consists of: term, docID, position in the document
            tokens.append([words[j], raw_document.id])
    return tokens

def positional_index(doc_collection):
    pass

if __name__ == '__main__':
    docs = get_documents()
    tokens = preprocess(docs[10])
    

