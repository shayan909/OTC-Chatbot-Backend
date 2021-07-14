# This file saves the disease prediction model, one hot transformer(for converting predictions to actual labels)
# and dataset as pickle files

import numpy as np
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer
import pickle

df = pd.read_csv('Disease Dataset Multilabel.csv')
df.dropna(inplace=True)
# Store as pickle to later access quickly for transforming user input from integer to name
df.to_pickle('Disease_Dataset_Multilabel.pickle')
X = df.loc[:, :'TARGET']  # Set columns from starting till TARGET Column as X
X = X.drop('TARGET', axis='columns')
X = np.array(X.values)

y = df['TARGET'].values.tolist()  # convert TARGET Column to list
# newlist = [expression for item in iterable if condition == True]
y = [x.split(',') for x in y]  # convert TARGET to list of lists
one_hot = MultiLabelBinarizer()
y = one_hot.fit_transform(y)
print(one_hot.classes_)

from sklearn.multioutput import MultiOutputClassifier
from sklearn.tree import DecisionTreeClassifier

model = DecisionTreeClassifier(random_state=1)
multi_target_model = MultiOutputClassifier(model, n_jobs=-1)
# train
multi_target_model.fit(X, y)

# pickling the classifier
with open('DiseaseClassifier.pickle', 'wb') as f:
    pickle.dump(multi_target_model, f)
    pickle.dump(one_hot, f)