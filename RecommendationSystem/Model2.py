
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np 
import sys
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx


# In[2]:


conn = sqlite3.connect('project.db') #connection
c = conn.cursor()  #get a cursor object, all SQL commands are processed by it
conn.commit()
df=pd.read_sql_query('select * from userT',conn)
conn.close()


# In[3]:


df_interest = pd.read_csv("interest1_matrix.csv")
df_followee = pd.read_csv("followee_matrix.csv")


# In[4]:


df_follower = pd.read_csv("follower1_matrix.csv")
df_follower.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_follower=df_follower.set_index('user')


# In[5]:


df.set_index('id',inplace = True)


# In[6]:


df_followee = pd.read_csv("followee1_matrix.csv")
df_followee.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_followee=df_followee.set_index('user')


# In[7]:


df_interest.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_interest=df_interest.set_index('user')


# In[15]:


len(df.index)


# In[9]:


def text_convert(text):
    for ch in ['[',']']:
        text = text.replace(ch,'')
    if len(text) != 0:
        text = text.replace(',','')
        text = text.replace("'",'')
        text = text.split(" ")
    else:
        text = None
    return text


# # Final Model

# In[17]:


#%%timeit
def find_follower(w1,a):
    scores=[]
    for user in df_followee.columns.values.tolist():
        score=[user,w1*df_followee.at[a,user] + (1-w1)*df_interest.at[a,user]] 
        scores.append(score)
    df_scores=pd.DataFrame(scores)
    df_scores=df_scores[df_scores[1]!=1]
    df_score=df_scores.nlargest(2, columns=1)
    c=text_convert(df.at[a,'target'])
    recommend=[]
    for user in df_score[0]:
        d=text_convert(df.at[int(user),'followee'])
        diff=list(set(d).difference(set(c)))
        recommend=recommend+diff
    return list(set(recommend))


# In[21]:


correct_dict = {}
w1 = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
total = len(df.index)
for j in range(len(w1)):
    correct = 0
    for i in df.index:
        if df.at[i,'test']  in find_follower(w1[j],i):  
            correct += 1
    correct_dict[w1[j]] = correct/ total
    print("current weight for follower similiarity is:",w1[j]," model accuracy is ", correct_dict[w1[j]])


# In[28]:


length = 0
for i in df.index:
    a = find_follower(0.9, i)
    if a != None:
        length += len(a)
avg_len = length / len(df.index)
print ("the average recommendation people is: ", round(avg_len))

