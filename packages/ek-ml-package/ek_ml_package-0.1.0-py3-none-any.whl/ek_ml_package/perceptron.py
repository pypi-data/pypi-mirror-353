import numpy as np

class Perceptron:
    def __init__(self, max_iter=100, tol=1e-5,random_state = None):
        """
        Initialize Perceptron model.
        Args:
          max_iter (int): Maximum number of training epochs.
          tol (float): Tolerance for weight updates to decide convergence.
          random_state: seed for reproducibility
        """
        self.max_iter = max_iter
        self.tol = tol
        self.random_state = random_state
        self.w = None  

    def initialize_weights(self, d):
        """
        Initialize weights with small random values.
        Args:
          d (int): Number of features (dimension of input).
        Returns:
          np.array: Weight vector of shape (d,).
        """
        w = np.random.rand(d) * 1e-4
        return w

    def shuffle_data(self, X, y):
        """
        Shuffle the training data and labels in unison.
        Args:
          X (np.array): Feature matrix.
          y (np.array): Labels vector.
        Returns:
          Shuffled X and y.
        """
        idx = np.random.permutation(X.shape[0])
        return X[idx], y[idx]

    def fit(self, X, y):
        """
        Train the Perceptron using the training data.
        Args:
          X (np.array): Training features of shape (n_samples, n_features).
          y (np.array): Labels (-1 or 1) of shape (n_samples,).
        """
        if self.random_state:
            np.random.seed(self.random_state)

        n, d = X.shape
        self.w = self.initialize_weights(d)

        for epoch in range(self.max_iter):
            X, y = self.shuffle_data(X, y)
            updated = False

            for i in range(n):
                y_pred = self.predict(X[i])
                if y_pred != y[i]:
                    w_new = self.w + y[i] * X[i]
                    # Check if update is significant enough
                    if np.linalg.norm(w_new - self.w) > self.tol:
                        self.w = w_new
                        updated = True
            
            # Stop early if no updates (converged)
            if not updated:
                # print(f"Converged at epoch {epoch + 1}")
                break

    def predict(self, x):
        """
        Predict the class label for a single input vector.
        Args:
          x (np.array): Input feature vector.
        Returns:
          int: Predicted label (-1 or 1).
        """
        result = np.dot(x, self.w)
        return np.where(result >= 0, 1, -1)

    def accuracy(self, y_true, y_pred):
        """
        Compute accuracy percentage.
        Args:
          y_true (np.array): True labels.
          y_pred (np.array): Predicted labels.
        Returns:
          float: Accuracy in percentage.
        """
        return np.mean(y_true.flatten() == y_pred.flatten()) * 100
