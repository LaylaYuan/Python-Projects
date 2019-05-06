
# coding: utf-8




import pandas as pd
import numpy as np 
import sys
import sqlite3




conn = sqlite3.connect('project.db') #connection
c = conn.cursor()  #get a cursor object, all SQL commands are processed by it
conn.commit()
df=pd.read_sql_query('select * from userT',conn)
conn.close()



df=df.set_index('id')


df_interest = pd.read_csv("interest1_matrix.csv")
df_follower = pd.read_csv("follower1_matrix.csv")


df_interest.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_interest=df_interest.set_index('user')


df_follower.rename(columns={'Unnamed: 0':'user'}, inplace = True)
df_follower=df_follower.set_index('user')



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



keep_cust_list = list(df.index)

len(keep_cust_list)


def find_followee(b,w1):
    c = text_convert(df.at[b,'target'])

    if c==None:
        return;
    followee=[]

    for a in c:
        a=int(a)
        if a in keep_cust_list:
            followee.append(a)
   
    scores=[]
    if len(followee)==0:
        return;
            
    for a in followee:
        for user in df_follower.columns.values.tolist():
            score=[user,w1*df_follower.at[int(a),user] + (1-w1)*df_interest.at[int(a),user]]
            scores.append(score)
    df_scores=pd.DataFrame(scores)
    
    df_scores=df_scores[df_scores[1]!=1]
    df_scores=df_scores[df_scores[0]!=str(b)]
    df_scores=df_scores.drop_duplicates(0, 'first')
    df_score=df_scores.nlargest(20, columns=1)
    return list(df_score[0])

# train different models with different weights
append_correct = []
w1 = [0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]
for j in range(len(w1)):
    correct = 0
    for i in df.index:
        if find_followee(i,w1[j]) != None:
            a = df.at[i,'test']    
            if a in find_followee(i,w1[j]):
                correct += 1
    accuracy = correct / len(keep_cust_list)
    append_correct.append(correct)
    print("the current w1 is:",w1[j]," the number of correct is ", correct, "the accuracy is ", accuracy)


# We use the best parameters got from previous step to make recommendations and calculate the average length
def recommend_followee(b):
    c = text_convert(df.at[b,'followee'])

    if c==None:
        return;
    followee=[]

    for a in c:
        a=int(a)
        if a in keep_cust_list:
            followee.append(a)
   
    scores=[]
    if len(followee)==0:
        return;
            
    for a in followee:
        for user in df_follower.columns.values.tolist():
            score=[user,0.9*df_follower.at[int(a),user] + 0.1*df_interest.at[int(a),user]]
            scores.append(score)
    df_scores=pd.DataFrame(scores)
    
    df_scores=df_scores[df_scores[1]!=1]
    df_scores=df_scores[df_scores[0]!=str(b)]
    df_scores=df_scores.drop_duplicates(0, 'first')
    df_score=df_scores.nlargest(20, columns=1)
    return list(df_score[0])
    
    
    
length = 0
for i in df.index:
    a = recommend_followee(i)
    if a != None:
        length += len(a)
avg_len = length / len(df.index)
print ("the average recommendation length is :", round(avg_len))
