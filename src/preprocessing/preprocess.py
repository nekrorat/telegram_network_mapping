#2 data preprocessing

import string
from token import tok_name

import pandas as pd
import spacy
from spacy import displacy

df = pd.read_csv('messages.csv')

#2.1 remove punctuations
def remove_punctuation(str_input):
    str_input = str_input.replace('\n', ' ')
    return str_input.translate(str.maketrans('', '', string.punctuation))

#test_str = '''{};:'Test!()-[] string./$%^ is?@# correct"\,<>&*_~'''
#print(remove_punctuation(test_str))

df['message'] = df['message'].apply(remove_punctuation)
#print(df['message'])

#2.2 tokenization

#en_core_web_sm
#ru_core_news_sm
#ru_core_news_lg
#uk_core_news_sm
#uk_core_news_lg

# nlp = spacy.blank('ru')
nlp = spacy.load('ru_core_news_sm')

doc = nlp(df['message'][3])
print(doc)
print('####################')

displacy.serve(doc, style="ent")