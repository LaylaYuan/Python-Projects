
# coding: utf-8

# In[13]:


import sqlite3
import pandas as pd
from datetime import date
import datetime
import numpy as np
from math import isnan
import matplotlib.pyplot as plt

from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp
from sklearn.model_selection import train_test_split


# In[14]:


def rating(x):
    if x >= 5.0: 
        x = 1  #strong buy
    elif 2.5 < x < 5.0:
        x =2    # buy
    elif -2.5 <= x <= 2.5:
        x = 3    #hold   
    elif -5.0 < x < -2.5:
        x = 4   # Underperform
    elif x <=-5.0:
        x = 5    #sell
    return x


def get_recommend_score(ticker):
    
    ################################
    # Connect data from database###
    ###############################
    conn = sqlite3.connect('new_stock3.db')
    c = conn.cursor()
    if ticker == "GOOG":
        df1 = pd.read_sql('SELECT * FROM GOOG',conn)
    elif ticker == "TSLA":
        df1 = pd.read_sql('SELECT * FROM TSLA',conn)
    elif ticker == "MSFT":
        df1 = pd.read_sql('SELECT * FROM  MSFT',conn)
    conn.commit()
    conn.close()
    
    #return df1
    conn = sqlite3.connect('stock.db')
    c = conn.cursor()
    df2 = pd.read_sql("SELECT * FROM historicaldata where stock = '%s' " %ticker, conn)
    df2["date"]= df2["date"].apply(lambda x: date.isoformat(datetime.datetime.fromtimestamp(x)))
    conn.commit()
    conn.close()
                          
    #merge two dataset
    df = pd.merge(df1, df2, on = 'date', how = 'inner')
    #df = df.dropna()
    df.set_index('date', inplace = True)
    df["change%"] = round((100* (df.iloc[:,-1] - df.iloc[:,-4])/df.iloc[:,-4]), 2)   
    
    # calculate positive/negative/neural percentage
    df.iloc[:,2] = df.iloc[:,2]/(df.iloc[:,2] + df.iloc[:,3] + df.iloc[:,4])
    df.iloc[:,3] = df.iloc[:,3]/(df.iloc[:,2] + df.iloc[:,3] + df.iloc[:,4])
    df.iloc[:,4] = df.iloc[:,4]/(df.iloc[:,2] + df.iloc[:,3] + df.iloc[:,4])
    
    df["rating"] = df["change%"].map(rating)
    
    ##################################################################
    #use Support Vector Classification to predict recommending score## 
    ##################################################################
    
    x = np.asarray(df.iloc[:,1:5]).reshape(-1,4)
    y = np.asarray(df['rating'])
     #Binarize the output
    y = label_binarize(y, classes=[1,2,3,4,5])
    n_classes = y.shape[1]

    # Add noisy features to make the problem harder
    random_state = np.random.RandomState(0)
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=.4)

    classifier = OneVsRestClassifier(svm.SVC(kernel='linear', probability=True, random_state=random_state))
    y_score = classifier.fit(x_train, y_train).decision_function(x_test)
    
    
    #################################################
    #Compute ROC curve and ROC area for each class###
    #################################################
    
    fpr = dict()
    tpr = dict()
    roc_auc = dict()

    for i in range(n_classes):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
        roc_auc[i] = auc(fpr[i], tpr[i])

    # Compute micro-average ROC curve and ROC area
    fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
    roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])
    all_fpr = np.unique(np.concatenate([fpr[i] for i in range(n_classes)]))

    # Then interpolate all ROC curves at this points
    mean_tpr = np.zeros_like(all_fpr)
    for i in range(n_classes):
        mean_tpr += interp(all_fpr, fpr[i], tpr[i])

    # Finally average it and compute AUC
    mean_tpr /= n_classes

    fpr["macro"] = all_fpr
    tpr["macro"] = mean_tpr
    roc_auc["macro"] = auc(fpr["macro"], tpr["macro"])
    
    # Plot all ROC curves
    lw=2
    plt.figure()
    plt.plot(fpr["micro"], tpr["micro"],
             label='micro-average ROC curve (area = {0:0.2f})'
                   ''.format(roc_auc["micro"]),
             color='deeppink', linestyle=':', linewidth=4)

    plt.plot(fpr["macro"], tpr["macro"],
             label='macro-average ROC curve (area = {0:0.2f})'
                   ''.format(roc_auc["macro"]),
             color='navy', linestyle=':', linewidth=4)

    colors = cycle(['aqua', 'darkorange', 'cornflowerblue'])
    for i, color in zip(range(n_classes), colors):
        plt.plot(fpr[i], tpr[i], color=color, lw=lw,
                 label='ROC curve of Score {0} (area = {1:0.2f})'
                 ''.format(i+1, roc_auc[i]))

    plt.plot([0, 1], [0, 1], 'k--', lw=lw)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve for Different Recommending Score')
    plt.legend(loc="lower right")
    #plt.show()

    ##############################################
    #get maximum ROC area and recommending score## 
    ##############################################
    X = {key: roc_auc[key] for key in roc_auc if not isnan(roc_auc[key]) and key not in ['micro', 'macro']}
    recommend_score = max(X, key=X.get) + 1
    return recommend_score


# In[15]:


get_recommend_score("GOOG")


# In[22]:


def store_to_bd():
    conn = sqlite3.connect('recommend.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS scoretable(date INT, stock TEXT, score INT)')
    stocklist=['MSFT','GOOG','TSLA']
    for ticker in stocklist:
        date = datetime.datetime.today().strftime('%y-%m-%d')
        score = get_recommend_score(ticker)
        c.execute('''INSERT INTO scoretable VALUES(?,?,?)''', (date, ticker, score))
    conn.commit()
    conn.close()


# In[23]:


store_to_bd()


# In[25]:


conn = sqlite3.connect('recommend.db')
c = conn.cursor()
c.execute('SELECT * from scoretable')
print(c.fetchall())


# In[ ]:




