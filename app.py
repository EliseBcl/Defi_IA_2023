# -*- coding: utf-8 -*-
"""Gradio_defiIA.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19K_jeM6rthjcfwIEdJWf6unQnBw-5DeU

# Gradio
"""

# !git clone https://github.com/EliseBcl/Defi_IA_2023.git

"""## Imports"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from math import sqrt, log
import seaborn as sns
from sklearn.preprocessing import scale
from pandas.plotting import scatter_matrix
from sklearn.decomposition import PCA
from sklearn.model_selection import train_test_split  
from sklearn.preprocessing import StandardScaler  
from collections import Counter
from sklearn.datasets import make_classification
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import roc_curve
from sklearn import linear_model
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.ensemble import RandomForestRegressor
from sklearn.datasets import load_iris
#from factor_analyzer import FactorAnalyzer
from sklearn.feature_extraction import DictVectorizer

plt.rcParams.update({'font.size': 12})

#gradio 
import gradio as gr

import random
from datasets import load_dataset
import shap

#save params
import pickle

"""## Fonction de formatage des données

#### Dummies
"""

def to_dummies(data_test):
  # merge on hotel id
  hotels = pd.read_csv('data/features_hotels.csv',index_col=0)
  hotels = hotels.drop(['city'], axis = 1)
  data_test = data_test.join(hotels, on = 'hotel_id')
  
  # to categorical
  data_test['city'] = pd.Categorical(data_test.city)
  data_test['language'] = pd.Categorical(data_test.language)
  data_test['mobile'] = pd.Categorical(data_test.mobile)
  # data_test['avatar_id'] = pd.Categorical(data_test.avatar_id)
  data_test['group'] = pd.Categorical(data_test.group)
  data_test['brand'] = pd.Categorical(data_test.brand)
  data_test['parking'] = pd.Categorical(data_test.parking)
  data_test['pool'] = pd.Categorical(data_test.pool)
  data_test['children_policy'] = pd.Categorical(data_test.children_policy)

  # dummies
  liste= ['stock', 'date','order_request', 'mobile', 'parking', 'pool']

  X_testDum = pd.get_dummies(data_test[["city","language","group","brand","children_policy"]])
  X_testQuant = data_test[liste]
  X_test_dum = pd.concat([X_testDum,X_testQuant],axis=1)

  return X_test_dum

"""### Nom des colonnes des train/test sets"""

col = ['city_amsterdam', 'city_copenhagen', 'city_madrid', 'city_paris',
       'city_rome', 'city_sofia', 'city_valletta', 'city_vienna',
       'city_vilnius', 'language_austrian', 'language_belgian',
       'language_bulgarian', 'language_croatian', 'language_cypriot',
       'language_czech', 'language_danish', 'language_dutch',
       'language_estonian', 'language_finnish', 'language_french',
       'language_german', 'language_greek', 'language_hungarian',
       'language_irish', 'language_italian', 'language_latvian',
       'language_lithuanian', 'language_luxembourgish', 'language_maltese',
       'language_polish', 'language_portuguese', 'language_romanian',
       'language_slovakian', 'language_slovene', 'language_spanish',
       'language_swedish', 'group_Accar Hotels', 'group_Boss Western',
       'group_Chillton Worldwide', 'group_Independant',
       'group_Morriott International', 'group_Yin Yang', 'brand_8 Premium',
       'brand_Ardisson', 'brand_Boss Western', 'brand_Chill Garden Inn',
       'brand_Corlton', 'brand_CourtYord', 'brand_Ibas', 'brand_Independant',
       'brand_J.Halliday Inn', 'brand_Marcure', 'brand_Morriot',
       'brand_Navatel', 'brand_Quadrupletree', 'brand_Royal Lotus',
       'brand_Safitel', 'brand_Tripletree', 'children_policy_0',
       'children_policy_1', 'children_policy_2', 'stock', 'date',
       'order_request', 'mobile', 'parking', 'pool']

"""## Chargement du model pré-entrainé"""

hotels = pd.read_csv('data/features_hotels.csv',index_col=0)

# load the model
xgb_model_loaded = pickle.load(open('data/model_gbmOpt_mat4.pkl', "rb"))

"""## Fonction de prédiction du nouvelle individu"""



def predict_new_indiv(language,city,date,mobile,order_requests,stock,hotel_id):
    avatar_id = 1
    test = pd.DataFrame(np.array([language,city,date,mobile,order_requests,avatar_id,stock,hotel_id])).T
    test.columns = ['language','city','date','mobile','order_request','stock','avatar_id','hotel_id']

    if hotel_id not in np.unique(hotels[hotels.city == city].index):
      return "choose an hotel_id in the following list : " + str(np.unique(hotels[hotels.city == city].index))

    else:
      test.date = test.date.astype('int64')
      test.mobile = test.mobile.astype('int64')
      test.order_request = test.order_request.astype('int64')
      test.stock = test.stock.astype('int64')
      test.hotel_id = test.hotel_id.astype('int64')

      individu = to_dummies(test)
      #convert the stock
      Xtest = pd.read_csv('data/test_set.csv',index_col=0)
      X = Xtest.stock
      mean_stock = np.mean(np.array(np.log(X+0.001)))
      std_stock = np.std(np.array(np.log(X+0.001)))
      individu.stock = (np.array(np.sqrt(individu.stock+0.001))- mean_stock)/std_stock

      #same format as train/test sets
      testset = pd.read_csv('data/testset.csv',index_col=0)
      all = pd.DataFrame([np.zeros(67, dtype=float)], columns=testset.columns)
      all[individu.columns] = individu.values

      pred = xgb_model_loaded.predict(all)
      result = np.exp(pred) - 0.001
      return "price per nigth " + str(np.round(result[0],0)) + " euros"

"""## Gradio interface"""

in1 = gr.inputs.Dropdown(choices=['romanian', 'swedish', 'maltese', 'belgian', 'luxembourgish',
       'dutch', 'french', 'finnish', 'austrian', 'slovakian', 'hungarian',
       'bulgarian', 'danish', 'greek', 'croatian', 'polish', 'german',
       'spanish', 'estonian', 'lithuanian', 'cypriot', 'latvian', 'irish',
       'italian', 'slovene', 'czech', 'portuguese'])
in2 = gr.inputs.Dropdown(choices=['paris', 'copenhagen', 'madrid', 'rome', 'sofia', 'vilnius', 'vienna', 'amsterdam', 'valletta'])
in3 = gr.Slider(minimum=0, maximum=40, step=1) #date
in4 = gr.Slider(minimum=0, maximum=1, step=1) #mobile
in5 = gr.Slider(minimum=0, maximum=10, step=1) #order_request
in6 = gr.Slider(minimum=0, maximum=199, step=1) #stock
in7 = gr.Slider(minimum=0, maximum=999, step=1) #hotel_id

app = gr.Interface(fn=predict_new_indiv, inputs=[in1, in2, in3, in4, in5, in6, in7], outputs="text")

app.launch(share=True)

