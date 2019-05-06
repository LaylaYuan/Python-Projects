
# coding: utf-8

# In[1]:


import requests
import re
from bs4 import BeautifulSoup
import datetime as dt
from datetime import timedelta, time
from time import sleep
import sqlite3
import time
import json
import requests
import json
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
import nltk
import string
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import feature_extraction  
from sklearn.feature_extraction.text import TfidfTransformer  
from sklearn.feature_extraction.text import CountVectorizer  
import pprint
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import numpy as np
from datetime import *
from datetime import timedelta
from newsplease import NewsPlease
from pandas import Series, DataFrame
import pandas as pd


# In[2]:


conn = sqlite3.connect('new_stock3.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS TSLA( stock TEXT, date INT, compound_score FLOAT, positive_counts INT, negative_counts INT, neural_counts INT, p_sentiment FLOAT, n_sentiment FLOAT, total_sentiment FLOAT) ''')
c.execute('delete from TSLA')
conn.commit()


# In[3]:


sid = SentimentIntensityAnalyzer()
ps = PorterStemmer()
def tokenize(text):
    tokens = nltk.word_tokenize(text)
    stems = []
    for item in tokens:
        stems.append(ps.stem(item))
    return stems



append_text = []

#publish_time = []
time_list = []
end = datetime.today()
begin = end - timedelta(days=30, hours=24)
d = begin
delta = timedelta(days=1)
while d <= end:
    time = d.strftime("%Y-%m-%d")
    time_list.append(time)
    d += delta 
    
stock_sql = ["TSLA"]*len(time_list)    
date_sql = time_list
compound_sql = []
positive_counts_sql = []
negative_counts_sql = []
neural_counts_sql = []
p_sentimentscore_sql = []
n_sentimentscore_sql = []
t_sentimentscore_sql = []

for date in time_list:
    url = 'https://newsapi.org/v2/everything?q=tsla&from=%s&to=%s&language=en&apiKey=d74cd7c10e6145be8527a8b18cbaff60'%(date,date)
    response = requests.get(url)
    r = response.json()
    try:
        article = r['articles'] 
    except:
        pass
    total_text = []
    for i in range(5):
        try:
            publish = article[i]['publishedAt']
            #publish_time.append(publish)
            url = article[i]['url']
            _text = NewsPlease.from_url(url).text
            total_text.append(_text)
        except:
            pass
    append_text.append(total_text)
#print(append_text)
    
for i in range(len(time_list)):
    sentences = []
    sentence = sent_tokenize(str(append_text[i]))
    sentences.extend(sentence)
    summary = {"positive":0,"neutral":0,"negative":0}
    #print(summary)
    p_sentimentscore = []
    n_sentimentscore = []
    compound = []
    for sentence in sentences:
        ss = sid.polarity_scores(sentence)
        compound.append(ss["compound"])
        p_sentimentscore.append(ss["pos"])
        n_sentimentscore.append(ss["neg"])    
        if ss["compound"] == 0.0: 
            summary["neutral"] +=1
        elif ss["compound"] > 0.0:
            summary["positive"] +=1
        else:
            summary["negative"] +=1 
    #print("p_sentimentscore",len(p_sentimentscore))
    #print("n_sentimentscore",len(n_sentimentscore))
    t_score = 0
    p_score = 0
    n_score = 0
    c_score = 0
#     if len(p_sentimentscore) == 0:
#         p_avgscore = 0
#     else:
    for j in range(len(p_sentimentscore)):
        p_score += p_sentimentscore[j]
    p_avgscore = p_score / len(p_sentimentscore)
    p_sentimentscore_sql.append(p_avgscore)
#         if len(n_sentimentscore) == 0:
#             n_avgscore = 0
#         else:
    for k in range(len(n_sentimentscore)):
        n_score += n_sentimentscore[k]
    n_avgscore = n_score / len(n_sentimentscore)
    n_sentimentscore_sql.append(n_avgscore)
    for m in range(len(compound)):
        c_score += compound[m]
    c_avgscore = c_score / len(compound)
    compound_sql.append(c_avgscore)
    neural_counts_sql.append(summary['neutral'])
    positive_counts_sql.append(summary['positive'])
    negative_counts_sql.append(summary['negative'])
    t_score = p_avgscore - n_avgscore
    t_sentimentscore_sql.append(t_score) 

#delete the stopwords of articles

#append_data = []
for i in range(len(stock_sql)):
    collect_data = []
    collect_data.append(stock_sql[i])
    collect_data.append(date_sql[i])
    collect_data.append(compound_sql[i])
    collect_data.append(positive_counts_sql[i])
    collect_data.append(negative_counts_sql[i])
    collect_data.append(neural_counts_sql[i])
    collect_data.append(p_sentimentscore_sql[i])
    collect_data.append(n_sentimentscore_sql[i])
    collect_data.append(t_sentimentscore_sql[i])
    collect_data = tuple(collect_data)
    #append_data.append(collect_data)
    c.execute('''INSERT INTO TSLA(stock, date, compound_score, positive_counts, negative_counts, neural_counts, p_sentiment, n_sentiment, total_sentiment) values(?,?,?,?,?,?,?,?,?)''', collect_data)
    #print (collect_data)
#c.execute('DELETE from microsoft')
conn.commit()
#     #print(stock_sql, date_sql, positive_sql, negative_sql, neural_sql, sentimentscore_sql, wordlist_sql)
#     #print (len(stock_sql),len(date_sql),len(positive_sql),len(negative_sql),len(neural_sql),len(sentimentscore_sql),len(wordlist_sql))


# In[4]:


c.execute('select * from TSLA')
print(*c.fetchall(),sep='\n')


# In[ ]:


#c.execute('delete from google')


# In[ ]:


#nlprocess()
#print (len(stock_sql),len(date_sql),len(positive_sql),len(negative_sql),len(neural_sql),len(sentimentscore_sql),len(wordlist_sql))
#print(stock_sql, date_sql, positive_sql, negative_sql, neural_sql, sentimentscore_sql, wordlist_sql)
# c.execute('select count(*) from microsoft')
# print(*c.fetchall(),sep='\n')


# In[9]:


c.execute('SELECT sql FROM sqlite_master WHERE type="table"')
print(c.fetchall())


# In[7]:


c.executescript('drop table if exists MSFT;')


# In[5]:


conn = sqlite3.connect('new_stock3.db')
c = conn.cursor()
df1 = pd.read_sql('SELECT * FROM TSLA', conn)
df1 = df1.drop(['stock'], axis = 1)
conn.commit()
df1

