
# coding: utf-8




import pandas as pd
import numpy as np 
import sys
import sqlite3
import matplotlib.pyplot as plt
import networkx as nx




conn = sqlite3.connect('project.db') #connection
c = conn.cursor()  #get a cursor object, all SQL commands are processed by it
conn.commit()
df=pd.read_sql_query('select * from userT',conn)
conn.close()



df_interest = pd.read_csv("interest1_matrix.csv")

df_follower = pd.read_csv("follower1_matrix.csv")
df_follower.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_follower=df_follower.set_index('user')

df.set_index('id',inplace = True)


df_followee = pd.read_csv("followee1_matrix.csv")
df_followee.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_followee=df_followee.set_index('user')



df_interest.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_interest=df_interest.set_index('user')



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




#%%timeit
def find_follower(a):
    scores=[]
    for user in df_followee.columns.values.tolist():
        score=[user,0.9*df_followee.at[a,user] + 0.1*df_interest.at[a,user]] 
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


user = int(input("Please input a user id "))

if user not in list(df.index):
	print ("Please input a valid user id ")
	user = int(input("Please input a user id "))
	if user in list(df.index):
		print (find_follower(user))
else: 
	print ("the user that we recommend are: ", find_follower(user))
