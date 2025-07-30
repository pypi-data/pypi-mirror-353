from sklearn.datasets import fetch_olivetti_faces
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report

def classify_faces():
    data = fetch_olivetti_faces()
    X_train, X_test, y_train, y_test = train_test_split(data.data, data.target)
    clf = GaussianNB()
    clf.fit(X_train, y_train)
    preds = clf.predict(X_test)
    return classification_report(y_test, preds)
