

import fitz # install using: pip install PyMuPDF
from nltk.tokenize import word_tokenize, sent_tokenize
from collections import Counter
import json 
from nltk.corpus import wordnet

def pdf_read_text(file):

    with fitz.open(file) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
    return text 


def pdf_text2words(text):
    def filter_punctuation(w):
        if "." in w: return True 
        if ":" in w: return True 
        return False 

    def filter_num(w):
        return False 
    
    def filter_shortword(w):
        if len(w) < 4: return True 

    def filter_isword(w):
        if not wordnet.synsets(w):
            return True 
    
    def filter(w):
        for func in [
            filter_punctuation,
            filter_num,
            filter_shortword,
            filter_isword,
            
        ]:
            if func(w):
                return True 
        return False 
    
    words = word_tokenize(text)

    # words = Counter(words)
    dic = dict() 
    for w in words:
        if len(w) > 1 and w[0].isupper() and w[1].islower():
            w = w.lower() 
        dic[w] = dic.get(w, 0) + 1 

    fwords = dict() 
    for word, n in dic.items():
        if filter(word): continue 

        fwords[word] = n 

    # sorted_dict = sorted(my_dict.items(), key=lambda x: x[1])
    fwords = sorted(fwords.items(), key=lambda x: x[1], reverse=True)
    fwords = dict(fwords)
    return fwords
    pass 



if __name__ == "__main__":
    file = "2203.16506v3.pdf"

    text = pdf_read_text(file)

    words = pdf_text2words(text)

    # print(words)
    data = json.dumps(words, indent=2)
    print(data)
    print(len(words))

