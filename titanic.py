# -*- coding: utf-8 -*-
"""Titanic

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1tqoWm4KWHYc5Ei-3l7_I7mC6mvxn2kPY
"""

import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score
from sklearn.metrics import precision_score, recall_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import confusion_matrix
from joblib import dump
from github import Github

#Import the dataset
test_df=pd.read_csv("/content/test.csv")
train_df=pd.read_csv("/content/train.csv")
Y_test=pd.read_csv("/content/gender_submission.csv")

train_df.info()

test_df.describe()

train_df.describe()

train_df.head(10)

Y_test=Y_test.drop(['PassengerId'], axis=1)
Y_test.head(10)

#Show if value are missing
train_df.isnull().sum()

#Show the number of missing value and the percentage
total = train_df.isnull().sum().sort_values(ascending=False)
percent_1 = train_df.isnull().sum()/train_df.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total, percent_2], axis=1, keys=['Total', '%'])
missing_data.head(5)

#Show the repartition of people survived by age
fig, axes = plt.subplots(nrows=1, ncols=2,figsize=(10, 4))
women = train_df[train_df['Sex']=='female']
men = train_df[train_df['Sex']=='male']
ax = sns.distplot(women[women['Survived']==1].Age.dropna(), bins=40, label = 'survived', ax = axes[0], kde =False)
ax = sns.distplot(women[women['Survived']==0].Age.dropna(), bins=40, label = 'not survived', ax = axes[0], kde =False)
ax.legend()
ax.set_title('Female')
ax = sns.distplot(men[men['Survived']==1].Age.dropna(), bins=40, label = 'survived', ax = axes[1], kde = False)
ax = sns.distplot(men[men['Survived']==0].Age.dropna(), bins=40, label = 'not_survived', ax = axes[1], kde = False)
ax.legend()
_ = ax.set_title('Male')

#Show the percentage of survivant male and female by class and Embarked
EmbarkSurvie = sns.FacetGrid(train_df, row='Embarked', aspect=1.5)
EmbarkSurvie.map(sns.pointplot, 'Pclass', 'Survived', 'Sex',palette=None,  order=None, hue_order=None )
EmbarkSurvie.add_legend()

#Show the percentage of male and female by class
ClassSurvie = sns.FacetGrid(train_df, row='Pclass', aspect=1.5)
ClassSurvie.map(sns.barplot, 'Pclass', 'Survived', 'Sex',palette=None,  order=None, hue_order=None )
ClassSurvie.add_legend()

#Show the number of people survived or not by class and age
grid = sns.FacetGrid(train_df, col='Survived', row='Pclass', aspect=1.6)
grid.map(plt.hist, 'Age', alpha=.5, bins=20)
grid.add_legend()

#The number of people who are alone or not
data = [train_df, test_df]
for dataset in data:
    dataset['relatives'] = dataset['SibSp'] + dataset['Parch']
    dataset.loc[dataset['relatives'] > 0, 'not_alone'] = 0
    dataset.loc[dataset['relatives'] == 0, 'not_alone'] = 1
    dataset['not_alone'] = dataset['not_alone'].astype(int)
train_df['not_alone'].value_counts()

#Remove the part 'Cabin' of the dataset
train_df = train_df.drop(['Cabin'], axis=1)
test_df = test_df.drop(['Cabin'], axis=1)
train_df.head(20)

#Fill the part age of the dataset
data = [train_df, test_df]

for dataset in data:
    mean = train_df["Age"].mean()
    std = test_df["Age"].std()
    is_null = dataset["Age"].isnull().sum()

    aleatoire_age = np.random.randint(mean - std, mean + std, size = is_null)

    age_copy = dataset["Age"].copy()
    age_copy[np.isnan(age_copy)] = aleatoire_age
    dataset["Age"] = age_copy
    dataset["Age"] = train_df["Age"].astype(int)
train_df["Age"].isnull().sum()

train_df['Embarked'].describe()

#Fill the dataset 'Embarked' by the main value
mostcommon_value = 'S'
data = [train_df, test_df]

for dataset in data:
    dataset['Embarked'] = dataset['Embarked'].fillna(mostcommon_value)

#Convert the dataset 'Fare' into int
data = [train_df, test_df]

for dataset in data:
    dataset['Fare'] = dataset['Fare'].fillna(0)
    dataset['Fare'] = dataset['Fare'].astype(int)

#Convert the dataset 'Title' into numbers
data = [train_df, test_df]
titles = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}

for dataset in data:
    # extract titles
    dataset['Title'] = dataset.Name.str.extract(' ([A-Za-z]+)\.', expand=False)
    # replace titles with a more common title or as Rare
    dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col','Don', 'Dr',\
                                            'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
    dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')
    # convert titles into numbers
    dataset['Title'] = dataset['Title'].map(titles)
    # filling NaN with 0, to get safe
    dataset['Title'] = dataset['Title'].fillna(0)
train_df = train_df.drop(['Name'], axis=1)
test_df = test_df.drop(['Name'], axis=1)

#Convert sex to binary
genders = {"male": 0, "female": 1}
data = [train_df, test_df]

for dataset in data:
    dataset['Sex'] = dataset['Sex'].map(genders)

#Remove the part 'Ticket' of the dataset
train_df = train_df.drop(['Ticket'], axis=1)
test_df = test_df.drop(['Ticket'], axis=1)

#Convert the boarding gate into integers
ports = {"S": 0, "C": 1, "Q": 2}
data = [train_df, test_df]

for dataset in data:
    dataset['Embarked'] = dataset['Embarked'].map(ports)

# Create age categories
data = [train_df, test_df]
for dataset in data:
    dataset['Age'] = dataset['Age'].astype(int)
    dataset.loc[ dataset['Age'] <= 11, 'Age'] = 0
    dataset.loc[(dataset['Age'] > 11) & (dataset['Age'] <= 18), 'Age'] = 1
    dataset.loc[(dataset['Age'] > 18) & (dataset['Age'] <= 22), 'Age'] = 2
    dataset.loc[(dataset['Age'] > 22) & (dataset['Age'] <= 27), 'Age'] = 3
    dataset.loc[(dataset['Age'] > 27) & (dataset['Age'] <= 33), 'Age'] = 4
    dataset.loc[(dataset['Age'] > 33) & (dataset['Age'] <= 40), 'Age'] = 5
    dataset.loc[dataset['Age'] > 40, 'Age'] = 6

train_df['Age'].value_counts()

#Create Age categories
data = [train_df, test_df]

for dataset in data:
    dataset.loc[ dataset['Fare'] <= 7.5, 'Fare'] = 0
    dataset.loc[(dataset['Fare'] > 7.5) & (dataset['Fare'] <= 15), 'Fare'] = 1
    dataset.loc[(dataset['Fare'] > 15) & (dataset['Fare'] <= 31), 'Fare']   = 2
    dataset.loc[(dataset['Fare'] > 31) & (dataset['Fare'] <= 99), 'Fare']   = 3
    dataset.loc[(dataset['Fare'] > 99) & (dataset['Fare'] <= 250), 'Fare']   = 4
    dataset.loc[ dataset['Fare'] > 250, 'Fare'] = 5
    dataset['Fare'] = dataset['Fare'].astype(int)

train_df['Fare'].value_counts()

#Create the datasets
X_train = train_df.drop(["Survived", "PassengerId"], axis=1)
Y_train = train_df["Survived"]
X_test= test_df.drop(["PassengerId"], axis=1)
#Create the model
logreg = LogisticRegression(max_iter=1000)
#Train the model
logreg.fit(X_train, Y_train)
# Prediction
Y_pred = logreg.predict(X_test)

# Evaluate the model
acc_log = round(logreg.score(X_train, Y_train) * 100, 2)

#Create the model
random_forest = RandomForestClassifier(n_estimators=100)
#Train the model
random_forest.fit(X_train, Y_train)
#Prediction of the model
Y_prediction = random_forest.predict(X_test)
#Evaluate
random_forest.score(X_train, Y_train)
acc_random_forest = round(random_forest.score(X_train, Y_train) * 100, 2)

#Create the model
linear_svc = LinearSVC()
#Train the model
linear_svc.fit(X_train, Y_train)
#Prediction of the model
Y_pred = linear_svc.predict(X_test)
#Evaluate the model
acc_linear_svc = round(linear_svc.score(X_train, Y_train) * 100, 2)

print(acc_log)
print(acc_random_forest)
print(acc_linear_svc)

rf = RandomForestClassifier(n_estimators=100)
scores_rf = cross_val_score(rf, X_train, Y_train, cv=10, scoring = "accuracy")
print("Scores:", scores_rf)
print("Mean:", scores_rf.mean())
print("Standard Deviation:", scores_rf.std())

scores_logreg = cross_val_score(logreg, X_train, Y_train, cv=10, scoring="accuracy")
print("Scores:", scores_logreg)
print("Mean:", scores_logreg.mean())
print("Standard Deviation:", scores_logreg.std())

svc = SVC()
scores_svc = cross_val_score(svc, X_train, Y_train, cv=10, scoring="accuracy")
print("Scores:", scores_svc)
print("Mean:", scores_svc.mean())
print("Standard Deviation:", scores_svc.std())

importances = pd.DataFrame({'feature':X_train.columns,'importance':np.round(random_forest.feature_importances_,3)})
importances = importances.sort_values('importance',ascending=False).set_index('feature')
importances.head(10)
importances.plot.bar()

#Delete the 2 features
train_df  = train_df.drop("not_alone", axis=1)
test_df  = test_df.drop("not_alone", axis=1)
train_df  = train_df.drop("Parch", axis=1)
test_df  = test_df.drop("Parch", axis=1)

random_forest = RandomForestClassifier(n_estimators=100, oob_score = True)
random_forest.fit(X_train, Y_train)
Y_prediction = random_forest.predict(X_test)

random_forest.score(X_train, Y_train)

acc_random_forest = round(random_forest.score(X_train, Y_train) * 100, 2)
print(round(acc_random_forest,2,), "%")

#Create a dictionnary with hyperparameters to test
param_grid = {
    "criterion": ["gini", "entropy"],
    "min_samples_leaf": [1, 5, 10, 25, 50, 70],
    "min_samples_split": [2, 4, 10, 12, 16, 18, 25, 35],
    "n_estimators": [100,400,700,1000,1500]
}
#Create a starting modele
rf = RandomForestClassifier(n_estimators=100, max_features='auto', oob_score=True, random_state=1, n_jobs=-1)
#Search the best hyperparameters
clf = GridSearchCV(estimator=rf, param_grid=param_grid, n_jobs=-1)
#Testing the hyperparameters
clf.fit(X_train, Y_train)

print("Meilleurs hyperparamètres:", clf.best_params_)

random_forest = RandomForestClassifier(criterion = "gini",
                                       min_samples_leaf = 1,
                                       min_samples_split = 10,
                                       n_estimators=100,
                                       max_features='auto',
                                       oob_score=True,
                                       random_state=1,
                                       n_jobs=-1)

random_forest.fit(X_train, Y_train)
Y_prediction = random_forest.predict(X_test)

random_forest.score(X_train, Y_train)

print("oob score:", round(random_forest.oob_score_, 4)*100, "%")

predictions = cross_val_predict(random_forest, X_train, Y_train, cv=3)

# Calculation of the confusion matrix
conf_matrix = confusion_matrix(Y_train, predictions)

# Create the heatmap
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', xticklabels=train_df['Survived'].unique(), yticklabels=train_df['Survived'].unique())
plt.title('Confusion Matrix')
plt.xlabel('Predictions')
plt.ylabel('True Values')
plt.show()

print("Precision:", precision_score(Y_train, predictions))
print("Recall:",recall_score(Y_train, predictions))

y_scores = random_forest.predict_proba(X_train)
y_scores = y_scores[:,1]
r_a_score = roc_auc_score(Y_train, y_scores)
print("ROC-AUC-Score:", r_a_score)

#Save the model
dump(random_forest, 'modele_random_forest.joblib')

