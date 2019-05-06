
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np 
import sys
import sqlite3
import random


# # Load Data

# In[2]:


df_f = pd.read_csv("follows.csv")
df_f.columns = ['follower_id','followee_id']
df_i = pd.read_csv("interests.csv")#applymap(str)
df_i.columns = ['user_id','category']


# In[3]:


interest = interest = df_i.groupby('category').count()
interest.columns = ['user_count']
interest = interest.sort_values(['user_count'],ascending=False)
follower = df_f.groupby('follower_id').count()
follower.columns = ['followee_count']
followee = df_f.groupby('followee_id').count()
followee.columns = ['follower_count']


# In[4]:


id_i=list(df_i['user_id'].unique())
id_follower=list(df_f['follower_id'].unique())
id_followee=list(df_f['followee_id'].unique())
print(len(id_i),len(id_follower),len(id_followee))
id=[]
id=id_i+id_follower+id_followee
print(len(id))
id=list(set(id))
print(len(id))
df_id= pd.DataFrame(columns=['id', 'follower_count', 'follower', 'followee_count', 'followee','interest_count', 'interest','target'])


# In[5]:


df_id['id']=id
df_id=df_id.fillna(value=0)


# # Following step may takes 5~8 mins to process

# In[6]:



for i in range(len(id)):
    followee_list= list(df_f.loc[df_f["follower_id"] == id[i]]["followee_id"])
    followee_lista= list(df_f.loc[df_f["follower_id"] == id[i]]["followee_id"])
    random.shuffle(followee_lista)
    followee_lista = followee_lista [:-1]
    follower_list = list(df_f.loc[df_f["followee_id"] == id[i]]["follower_id"])
    interest_list = list(df_i.loc[df_i["user_id"] == id[i]]["category"])
    df_id["follower_count"][i] = len(follower_list)
    df_id["follower"][i] = str(follower_list)
    df_id["followee_count"][i] = len(followee_list)                   
    df_id["followee"][i] = str(followee_list)
    df_id["interest_count"][i] = len(interest_list)                
    df_id["interest"][i] = str(interest_list)
    df_id["target"][i] = str(followee_lista)


# In[17]:


conn = sqlite3.connect('project.db') #connection
c = conn.cursor()  #get a cursor object, all SQL commands are processed by it
c.execute('DROP TABLE if exists user')
c.execute('CREATE TABLE user(id INTEGER, follower_count INTEGER,  follower TEXT, followee_count INTEGER ,followee TEXT ,interest_count INTEGER, interest TEXT, target TEXT)')
df_id.to_sql('user', conn, index=False, if_exists='append')
c.execute('DROP TABLE if exists interest')
c.execute('CREATE TABLE interest(category text, user_count INTEGER)')
interest.to_sql('interest', conn, index=True, if_exists='append')
c.close


#  # Trim the dataset size
# -  remove users who do not claim interests
# - remove users who have less than two people to followe and those who have too many people to followe (followee > 104)

# In[18]:


followee_benchmark = round(df_id.followee_count.quantile(0.99),0)
df_trimed = df_id[df_id.followee_count.between(2, followee_benchmark) & (df_id.interest_count !=0)]
len(df_trimed)
keep_cust_list = list(df_trimed.id)
drop_cust_list = list(df_id[~df_id["id"].isin(keep_cust_list)].id)
df_trimed.set_index('id', inplace = True)


# In[19]:


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


# In[20]:


for i in keep_cust_list:  
	i = int(i)   
	x1 = text_convert(df_trimed.at[i,'followee'])   
	x2 = text_convert(df_trimed.at[i,'target'])   
	tar = list(set(x1) - set(x2))[0]   
	df_trimed.at[i,'test'] = tar


# In[21]:


len(df_trimed)


# In[22]:


conn = sqlite3.connect('project.db') 
c.execute('DROP TABLE if exists userT')
c.execute('CREATE TABLE userT(id INTEGER, follower_count INTEGER,  follower TEXT, followee_count INTEGER ,followee TEXT ,interest_count INTEGER, interest TEXT, target TEXT，test TEXT)')
df_trimed.to_sql('userT', conn, index=True, if_exists ='replace')
c.close

