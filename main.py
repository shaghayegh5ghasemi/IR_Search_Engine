import openpyxl
from pathlib import Path
from parsivar import Normalizer
from parsivar import Tokenizer

# this function collects the documents info from the excel file
def get_documents():
    raw_doc_path = Path('IR1_7k_news.xlsx')
    raw_doc = openpyxl.load_workbook(raw_doc_path)
    doc_sheet = raw_doc.active
    content = doc_sheet['A']
    title = doc_sheet['C']
    documents = [] #extract contents and their title from .xlsx file
    for i in range(1, len(content)):
        documents.append([content[i].value, title[i].value])
    return documents

# this function prepossesses the documents: tokenize, normalize, stemming, delete stop words
def preprocess():
    normalizer = Normalizer()
    tokenizer = Tokenizer()

def positional_index():
    pass

if __name__ == '__main__':
    docs = get_documents()
    print(docs[0][1])