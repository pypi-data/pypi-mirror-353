import numpy as np

class KNNClassification:
    def __init__(self, k=3):
        """
        K-Nearest Neighbors Classifier.

        Args:
            k (int): Number of nearest neighbors to consider.
        """
        self.k = k
        self.X_train = None
        self.y_train = None
        self.dist = None

    def compute_euclidean_distance(self, X_test):
        """
        Compute pairwise Euclidean distances from test points to training points.
        """
        X_test_sq = np.sum(X_test ** 2, axis=1).reshape(-1, 1)
        X_train_sq = np.sum(self.X_train ** 2, axis=1).reshape(1, -1)
        cross_term = -2 * np.dot(X_test, self.X_train.T)
        self.dist = np.sqrt(X_test_sq + X_train_sq + cross_term)

    def fit(self, X_train, y_train):
        """
        Store training data.

        Args:
            X_train (np.ndarray): Training features.
            y_train (np.ndarray): Training labels.
        """
        self.X_train = X_train
        self.y_train = y_train

    def predict(self, X_test):
        """
        Predict class labels for test data.

        Args:
            X_test (np.ndarray): Test features.

        Returns:
            np.ndarray: Predicted class labels.
        """
        self.compute_euclidean_distance(X_test)
        n_test = X_test.shape[0]
        y_pred = np.zeros((n_test, 1), dtype=int)

        for i in range(n_test):
            neighbors_idx = np.argsort(self.dist[i])[:self.k]
            neighbor_labels = self.y_train[neighbors_idx]
            unique_labels, counts = np.unique(neighbor_labels, return_counts=True)
            y_pred[i] = unique_labels[np.argmax(counts)]

        return y_pred
    
    def loss(self,y_true, y_pred):
        """
        Compute misclassification rate (i.e., classification loss).

        Args:
            y_true (np.ndarray): True labels of shape (n_test,)
            y_pred (np.ndarray): Predicted labels of shape (n_test,)

        Returns:
            float: Misclassification rate (between 0 and 1)
        """
        incorrect = np.sum(y_true.flatten() != y_pred.flatten())
        total = len(y_true)
        return incorrect / total

    def accuracy(self, X_test, y_test):
        """
        Compute classification accuracy on test data.

        Returns:
            float: Accuracy score.
        """
        y_pred = self.predict(X_test)
        return np.mean(y_pred.flatten() == y_test.flatten())



class KNNRegression:
    def __init__(self, k=3):
        """
        K-Nearest Neighbors Regression.

        Args:
            k (int): Number of nearest neighbors to consider.
        """
        self.k = k
        self.X_train = None
        self.y_train = None
        self.dist = None

    def compute_euclidean_distance(self, X_test):
        """
        Compute pairwise Euclidean distances from test points to training points.
        """
        X_test_sq = np.sum(X_test ** 2, axis=1).reshape(-1, 1)
        X_train_sq = np.sum(self.X_train ** 2, axis=1).reshape(1, -1)
        cross_term = -2 * np.dot(X_test, self.X_train.T)
        self.dist = np.sqrt(X_test_sq + X_train_sq + cross_term)

    def fit(self, X_train, y_train):
        """
        Store training data.

        Args:
            X_train (np.ndarray): Training features.
            y_train (np.ndarray): Training targets.
        """
        self.X_train = X_train
        self.y_train = y_train

    def predict(self, X):
        """
        Predict continuous outputs for test data.

        Args:
            X_test (np.ndarray): Test features.

        Returns:
            np.ndarray: Predicted values.
        """
        self.compute_euclidean_distance(X)
        n = X.shape[0]
        y_pred = np.zeros((n, 1), dtype=float)

        for i in range(n):
            neighbors_idx = np.argsort(self.dist[i])[:self.k]
            neighbor_values = self.y_train[neighbors_idx]
            y_pred[i] = np.mean(neighbor_values)

        return y_pred

    def loss(self,y_true, y_pred ):
        """
        Compute Mean Squared Error on test data.

        Returns:
            float: MSE score.
        """
        return np.mean((y_true.flatten() - y_pred.flatten()) ** 2)
