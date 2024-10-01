#2 data preprocessing

import pandas as pd
import string

df = pd.read_csv('messages.csv')

#2.1 remove punctuations
def remove_punctuation(str_input):
    str_input = str_input.replace('\n', ' ')
    return str_input.translate(str.maketrans('', '', string.punctuation))

#test_str = '''{};:'Test!()-[] string./$%^ is?@# correct"\,<>&*_~'''
#print(remove_punctuation(test_str))

df['message'] = df['message'].apply(remove_punctuation)

#2.2 tokenization
