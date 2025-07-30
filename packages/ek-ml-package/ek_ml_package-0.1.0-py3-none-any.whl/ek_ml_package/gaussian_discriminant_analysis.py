import numpy as np

class LDA:
    def __init__(self):
        """
        Initializes LDA model with placeholders for priors, means, 
        shared covariance matrix, and class labels.
        """
        self.priors = None
        self.means = None
        self.Sigma = None
        self.classes_ = None
        self.is_fitted = False

    def compute_class_priors(self, y, K):
        """
        Computes class prior probabilities P(y=k).

        Args:
            y (np.ndarray): Array of class labels of shape (n_samples,)
            K (int): Number of unique classes

        Returns:
            np.ndarray: Prior probabilities of shape (K,)
        """
        n = len(y)
        priors = np.array([np.sum(y == k) for k in range(K)]) / n
        return priors

    def compute_class_means(self, X, y, K):
        """
        Computes mean vectors for each class.

        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features)
            y (np.ndarray): Class labels of shape (n_samples,)
            K (int): Number of classes

        Returns:
            np.ndarray: Mean vectors of shape (K, n_features)
        """
        d = X.shape[1]
        means = np.zeros((K, d))
        for k in range(K):
            X_k = X[y == k]
            means[k] = np.mean(X_k, axis=0)
        return means

    def fit(self, X, y):
        """
        Fits the LDA model by computing priors, means, and shared covariance.

        Args:
            X (np.ndarray): Feature matrix of shape (n_samples, n_features)
            y (np.ndarray): Class labels of shape (n_samples,)
        """
        n, d = X.shape
        self.classes_ = np.unique(y)
        K = len(self.classes_)

        self.priors = self.compute_class_priors(y, K)
        self.means = self.compute_class_means(X, y, K)

        self.Sigma = np.zeros((d, d))
        for k in range(K):
            X_k = X[y == k]
            centered = X_k - self.means[k]
            self.Sigma += centered.T @ centered
        self.Sigma /= n 
        self.is_fitted = True

    def predict(self, X):
        """
        Predicts class labels for input data using LDA decision rule.

        Args:
            X (np.ndarray): Input features of shape (n_samples, n_features)

        Returns:
            np.ndarray: Predicted class labels of shape (n_samples,)
        """
        if not self.is_fitted:
            raise RuntimeError("LDA model must be fitted before calling predict().")
        Sigma_inv = np.linalg.pinv(self.Sigma)
        scores = []
        for k in range(len(self.priors)):
            w_k = Sigma_inv @ self.means[k]
            b_k = -0.5 * self.means[k].T @ Sigma_inv @ self.means[k] + np.log(self.priors[k])
            g_k = X @ w_k + b_k
            scores.append(g_k)
        scores = np.array(scores) 
        return self.classes_[np.argmax(scores, axis=0)]

    def accuracy(self, y_true, y_pred):
        """
        Computes classification accuracy.

        Args:
            y_true (np.ndarray): True class labels
            y_pred (np.ndarray): Predicted class labels

        Returns:
            float: Accuracy score in [0, 1]
        """
        return np.mean(y_pred == y_true)


class QDA:
    def __init__(self):
        """
        Initializes QDA model with placeholders for priors, means, 
        class-specific covariances, and class labels.
        """
        self.priors = None
        self.means = None
        self.covariances = None
        self.classes_ = None
        self.is_fitted = False

    def compute_class_priors(self, y, K):
        """
        Computes class prior probabilities P(y=k).

        Args:
            y (np.ndarray): Array of class labels
            K (int): Number of classes

        Returns:
            np.ndarray: Prior probabilities of shape (K,)
        """
        n = len(y)
        priors = np.array([np.sum(y == k) for k in range(K)]) / n
        return priors

    def compute_class_means(self, X, y, K):
        """
        Computes mean vectors for each class.

        Args:
            X (np.ndarray): Feature matrix
            y (np.ndarray): Class labels
            K (int): Number of classes

        Returns:
            np.ndarray: Class means of shape (K, n_features)
        """
        d = X.shape[1]
        means = np.zeros((K, d))
        for k in range(K):
            X_k = X[y == k]
            means[k] = np.mean(X_k, axis=0)
        return means

    def fit(self, X, y):
        """
        Fits the QDA model by computing priors, means, and 
        class-specific covariance matrices.

        Args:
            X (np.ndarray): Feature matrix
            y (np.ndarray): Class labels
        """
        n, d = X.shape
        self.classes_ = np.unique(y)
        K = len(self.classes_)

        self.priors = self.compute_class_priors(y, K)
        self.means = self.compute_class_means(X, y, K)

        self.covariances = []
        for k in range(K):
            X_k = X[y == k]
            centered = X_k - self.means[k]
            cov_k = (centered.T @ centered) / len(X_k)
            self.covariances.append(cov_k)
        self.is_fitted = True

    def predict(self, X):
        """
        Predicts class labels for input data using QDA decision rule.

        Args:
            X (np.ndarray): Input features of shape (n_samples, n_features)

        Returns:
            np.ndarray: Predicted class labels of shape (n_samples,)
        """
        if not self.is_fitted:
            raise RuntimeError("QDA model must be fitted before calling predict().")

        n = X.shape[0]
        K = len(self.priors)
        scores = np.zeros((K, n))

        for k in range(K):
            mean = self.means[k]
            cov = self.covariances[k]
            cov_inv = np.linalg.pinv(cov)
            diff = X - mean
            term1 = -0.5 * np.sum(diff @ cov_inv * diff, axis=1)
            term2 = -0.5 * np.log(np.linalg.det(cov) + 1e-10)  # numerical stability
            term3 = np.log(self.priors[k])
            scores[k] = term1 + term2 + term3

        return self.classes_[np.argmax(scores, axis=0)]

    def accuracy(self, y_true, y_pred):
        """
        Computes classification accuracy.

        Args:
            y_true (np.ndarray): True labels
            y_pred (np.ndarray): Predicted labels

        Returns:
            float: Accuracy score in [0, 1]
        """
        return np.mean(y_pred == y_true)
