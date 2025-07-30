from sklearn.datasets import load_breast_cancer
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt

def run_kmeans_on_breast_data():
    data = load_breast_cancer()
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(data.data)
    kmeans = KMeans(n_clusters=2, random_state=42)
    labels = kmeans.fit_predict(X_pca)
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, cmap='viridis')
    plt.title("KMeans on Breast Cancer PCA")
    plt.show()
