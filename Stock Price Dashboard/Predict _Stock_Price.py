
# coding: utf-8

# In[3]:


import sqlite3
import pandas as pd
from datetime import date
import datetime
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn import preprocessing
import matplotlib.pyplot as plt
from sklearn import linear_model
from sklearn.svm import SVR
from math import isnan


# In[6]:


# Use Support Vector Regression to predict future price
def svr(x_train,y_train, x_test, y_test, time):
   svr_rbf = SVR(kernel='rbf', C=1e3, gamma=0.1)
   svr_lin = SVR(kernel='linear', C=1e3)
   svr_poly = SVR(kernel='poly', C=1e3, degree=2)
   y_rbf= svr_rbf.fit(x_train, y_train).predict(x_test)
   y_lin = svr_lin.fit(x_train, y_train).predict(x_test)
   y_poly= svr_poly.fit(x_train, y_train).predict(x_test)
   
   
   fig, ax = plt.subplots(1)
   ax.plot(time, y_test, color='darkorange', label='actual price')
   ax.plot(time, y_rbf, color='navy', label='RBF model')
   ax.plot(time, y_lin, color='c', label='Linear model')
   ax.plot(time, y_poly, color='cornflowerblue', label='Polynomial model')
   plt.xlabel('Date')
   plt.ylabel('Price')
   plt.title('Support Vector Regression')
   fig.autofmt_xdate()
   plt.legend()
   plt.show()


def get_predict_price (ticker):
   #step 1: read data from database
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
   
   conn = sqlite3.connect('stock.db')
   c = conn.cursor()
   df2 = pd.read_sql("SELECT * FROM historicaldata where stock = '%s' " %ticker, conn)
   df2["date"]= df2["date"].apply(lambda x: date.isoformat(datetime.datetime.fromtimestamp(x)))
   conn.commit()
   conn.close()
   
   df1 = df1.drop(['stock'],axis =1)
   df = pd.merge(df1, df2, on = 'date', how = 'inner')
   #df = df.dropna()
   df.set_index('date', inplace = True)
   df["change%"] = round((100* (df.iloc[:,-1] - df.iloc[:,-4])/df.iloc[:,-4]), 2)   
   
   # calculate positive/negative/neural percentage
   df.iloc[:,2] = df.iloc[:,2]/(df.iloc[:,2] + df.iloc[:,3] + df.iloc[:,4])
   df.iloc[:,3] = df.iloc[:,3]/(df.iloc[:,2] + df.iloc[:,3] + df.iloc[:,4])
   df.iloc[:,4] = df.iloc[:,4]/(df.iloc[:,2] + df.iloc[:,3] + df.iloc[:,4])
   
   
   train, test = train_test_split(df, test_size=0.4)
   numpy_df_train= np.asarray(train.iloc[:,0:4]).reshape(-1,4)
   numpy_df_test = np.asarray(test.iloc[:,0:4]).reshape(-1,4)
   time = test.index.tolist()
   
   # get the plot from the SVR models
   svr(numpy_df_train, train["close"], numpy_df_test, test["close"], time)

   
   #linear regression model
   clf1 = linear_model.LinearRegression()
   clf1.fit(numpy_df_train, train["close"])

   # Naive Bayes Gaussian
   clf2 = linear_model.BayesianRidge()
   clf2.fit(numpy_df_train, train["close"])

   predict1 = clf1.predict(numpy_df_test)
   predict2 = clf2.predict(numpy_df_test)

   actual = test['close'].tolist()

   fig, ax = plt.subplots(1)
   ax.plot(time, actual, color='darkorange', label='actual price')
   ax.plot(time, predict1, color='navy', label='LinearRegression model')
   ax.plot(time, predict2, color='green', label='GaussianNB model')
   plt.xlabel('Date')
   plt.ylabel('Price')
   plt.title('Price Predict Linear Regression VS Naive Bayes')
   fig.autofmt_xdate()
   fig.legend()
   plt.show()


# In[7]:


get_predict_price('GOOG')


# In[8]:


get_predict_price("TSLA")


# In[9]:


get_predict_price("MSFT")

