
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np 
import sys
import sqlite3
import matplotlib
import matplotlib.pyplot as plt
import networkx as nx


# In[2]:


conn = sqlite3.connect('project.db') #connection
c = conn.cursor()  #get a cursor object, all SQL commands are processed by it
conn.commit()
df=pd.read_sql_query('select * from user',conn)
df_i = pd.read_sql_query('select * from interest',conn)
conn.close()


# # Part A - Understand the data
# ## How many users are there?

# In[3]:


total_cust_count = df.shape[0]
print("There are %d users in the social networking site." %total_cust_count)


# ## How many interest categories were created by users?

# In[4]:


total_interest_count = df_i.shape[0]
print("There are %d interest categories were created by users." % total_interest_count)


# ## What is the distribution of interests in the entire population of individuals?
# 
# * Top 10 interests

# In[5]:


ax = df_i['user_count'][:10].plot(kind='barh', width = 0.75, legend=False,figsize=(15,10), color='lightsteelblue')
ax.invert_yaxis()
plt.title('Total 10 interests in the entire population of individuals')
for i in range(10):
    ax.text(df_i.iloc[i,1], i, '{:.0f}%'.format(df_i.iloc[i,1]*100 /total_cust_count), color='black', weight='bold')
    ax.set_yticklabels(df_i['category'][:10])


# ## How many declared interests do individual users have (histogram)?

# In[36]:


plt.title('Interests Quantity Distribution')
bins = np.linspace(0, df['interest_count'].max(), 100)
plt.hist(list(df['interest_count']),bins,color="green",normed = True)
plt.ylabel('Probability')
plt.xticks(np.arange(df['interest_count'].min(), df['interest_count'].max(), 100))
plt.xlabel('Number of interests')
plt.show()


# # connection degree distribution.

# In[47]:



df_f = pd.read_csv("follows.csv")
G= nx.Graph()
for i in range(len(df_f)):
    G.add_edge(df_f.iloc[i][0],df_f.iloc[i][1])
print(nx.info(G))


# In[48]:


plt.figure(figsize=(8,8))
nx.draw(G,node_size=20,alpha=0.6,node_color="c", with_labels=False)
plt.axis('equal')
plt.show()


# # Part B

# In[62]:


conn = sqlite3.connect('project.db') #connection
c = conn.cursor()  #get a cursor object, all SQL commands are processed by it
conn.commit()
df1=pd.read_sql_query('select * from userT',conn)
conn.close()


# In[63]:


df1.set_index('id', inplace = True)
keep_cust_list = list(df1.index)
df_ee = pd.DataFrame(columns= keep_cust_list, index=keep_cust_list)  # followee similarity matrix
df_in = pd.DataFrame(columns=keep_cust_list, index=keep_cust_list) # interest similarity matrix
df_er = pd.DataFrame(columns=keep_cust_list, index = keep_cust_list) # follower similarity matrix


# ## calculate similarity score for interest  --Jaccard Index

# In[ ]:


def interest_convert(text):
    for ch in ['[',']']:
        text = text.replace(ch,'')
    if len(text) != 0:
        text = text.replace(" '",'')
        text = text.replace("'",'')
        text = text.split(",")
    else:
        text = None
    return text


# In[ ]:


for id1 in keep_cust_list:    
	f1 = interest_convert(df1.at[id1,'interest'])    
	c_f1 = len(f1)    
	for id2 in keep_cust_list:        
		f2 = interest_convert(df1.at[id2,'interest'])      
		c = len(set(f1).intersection(f2))       
		c_f2 = len(f2)        
		total =  c_f1 + c_f2 - c       
		similarity = c / total       
		df_in.at[id1,id2] = similarity


# In[74]:


#df1


# In[ ]:


df_in.to_csv("interest1_matrix.csv", index = True)


# ## calculate similarity score for folllower --Jaccard Index¶

# In[76]:


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


# In[ ]:


for id1 in keep_cust_list:   
	f1 = text_convert(df1.at[id1,'target'])    
	c_f1 = len(f1)  
	for id2 in keep_cust_list:       
		f2 = text_convert(df1.at[id2,'target'])        
		c_f2 = len(f2)        
		c = len(set(f1).intersection(f2))        
		total = c_f1 + c_f2 - c        
		similarity = c /total        
		df_er.at[id1,id2] = similarity


# In[ ]:


df_er.to_csv("follower1_matrix.csv", index = True)


# ## calculate similarity score for followee--Jaccard Index

# In[77]:


for id1 in keep_cust_list:   
	f1 = text_convert(df1.at[id1,'follower'])    
	c_f1 = len(f1)  
	for id2 in keep_cust_list:      
		f2 = text_convert(df1.at[id2,'follower'])        
		c_f2 = len(f2)        
		c = len(set(f1).intersection(f2))        
		total = c_f1 + c_f2 - c        
		similarity = c /total        
		df_er.at[id1,id2] = similarity


# In[80]:


df_ee.to_csv("followee1_matrix.csv", index = True)

