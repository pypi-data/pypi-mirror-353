from sklearn.datasets import load_breast_cancer
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import matplotlib.pyplot as plt

def classify_breast_cancer():
    data = load_breast_cancer()
    X_train, X_test, y_train, y_test = train_test_split(data.data, data.target)
    clf = DecisionTreeClassifier()
    clf.fit(X_train, y_train)
    plot_tree(clf, filled=True)
    plt.show()
    preds = clf.predict(X_test)
    return classification_report(y_test, preds)
