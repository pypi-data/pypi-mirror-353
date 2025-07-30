import numpy as np
import matplotlib.pyplot as plt

class LogisticRegression:
    def __init__(self, lr=0.01, epochs=1000, batch_size=None,random_seed=None):
        """
        Initialize the logistic regression model.

        Args:
            lr: Learning rate for gradient descent.
            epochs: Number of iterations over the entire training dataset.
            batch_size: Number of samples per gradient update (mini-batch size).
        """
        self.beta = None  # Model weights (to be initialized later)
        self.lr = lr
        self.epochs = epochs
        self.batch_size = batch_size
        self.losses = []       # Track training loss
        self.val_losses = []   # Track validation loss
        if random_seed is not None:
            np.random.seed(random_seed)


    def sigmoid(self, z):
        """
        Apply the sigmoid function with clipping for numerical stability.
        
        Args:
            z: Linear combination of weights and inputs.

        Returns:
            Sigmoid of input.
        """
        z = np.clip(z, -500, 500)  # Avoid overflow
        return 1 / (1 + np.exp(-z))

    def predict(self, X):
        """
        Predict probabilities for input features.

        Args:
            X: Input features of shape (N, D)

        Returns:
            Predicted probabilities (N, 1)
        """
        X = self.add_ones(X)
        z = X.dot(self.beta)
        y_hat = self.sigmoid(z)
        return y_hat

    def add_ones(self, X):
        """
        Add a column of ones to input for bias term.

        Args:
            X: Input features (N, D)

        Returns:
            Input features with bias term (N, D+1)
        """
        return np.hstack((X, np.ones((X.shape[0], 1))))

    def initialize_weights(self, n_features):
        """
        Initialize weights with small random values.

        Args:
            n_features: Number of input features (including bias)

        Returns:
            Weight matrix of shape (n_features, 1)
        """
        return np.random.randn(n_features, 1) * 0.01

    def convert_probabilities_to_classes(self, y_probs, threshold=0.5):
        """
        Convert probabilities to binary class predictions.

        Args:
            y_probs: Predicted probabilities (N, 1)
            threshold: Threshold for classification (default 0.5)

        Returns:
            Binary class labels (0 or 1)
        """
        return np.where(y_probs >= threshold, 1, 0)

    def accuracy(self, y_true, y_pred_probs, threshold=0.5):
        """
        Compute classification accuracy.

        Args:
            y_true: True binary labels (N,)
            y_pred_probs: Predicted probabilities (N,)

        Returns:
            Accuracy as a float.
        """
        y_pred = self.convert_probabilities_to_classes(y_pred_probs, threshold)
        return np.mean(y_pred.flatten() == y_true.flatten())

    def binary_cross_entropy(self, y_true, y_pred, eps=1e-15):
        """
        Compute binary cross-entropy loss.

        Args:
            y_true: True binary labels (N, 1)
            y_pred: Predicted probabilities (N, 1)

        Returns:
            Binary cross-entropy loss.
        """
        y_pred = np.clip(y_pred, eps, 1 - eps)
        loss = -np.mean(y_true * np.log(y_pred) + (1 - y_true) * np.log(1 - y_pred))
        return loss

    def gradient_function(self, X, y, y_pred):
        """
        Compute the gradient of the binary cross-entropy loss.

        Args:
            X: Input data (N, D)
            y: True labels (N, 1)
            y_pred: Predicted probabilities (N, 1)

        Returns:
            Gradient vector (D, 1)
        """
        grad = X.T @ (y_pred - y)
        return grad

    def fit(self, X, y, validation_split=0.0):
        """
        Train the logistic regression model using (mini-batch) gradient descent.

        Args:
            X: Input features (N, D)
            y: True binary labels (N,)
            validation_split: Fraction of data to be used for validation.
        """
        y = y.reshape(-1, 1)
        X = self.add_ones(X)

        # Create validation split if requested
        if 0.0 < validation_split < 1.0:
            indices = np.random.permutation(X.shape[0])
            val_size = int(X.shape[0] * validation_split)

            val_indices = indices[:val_size]
            train_indices = indices[val_size:]

            X_val, y_val = X[val_indices], y[val_indices]
            X_train, y_train = X[train_indices], y[train_indices]
        else:
            X_train, y_train = X, y
            X_val, y_val = None, None

        n_samples, n_features = X_train.shape
        self.beta = self.initialize_weights(n_features)

        # Training loop
        for epoch in range(self.epochs):
            batch_size = self.batch_size or 32
            if not isinstance(batch_size, int) or batch_size < 1:
                raise ValueError("batch_size must be a positive integer")

            running_loss = 0.0
            idx = np.random.permutation(n_samples)
            X_shuffled = X_train[idx]
            y_shuffled = y_train[idx]

            for start in range(0, n_samples, batch_size):
                x_batch = X_shuffled[start:start + batch_size]
                y_batch = y_shuffled[start:start + batch_size]

                y_pred = self.sigmoid(np.dot(x_batch, self.beta))
                loss = self.binary_cross_entropy(y_batch, y_pred)
                running_loss += loss * x_batch.shape[0]

                grad = self.gradient_function(x_batch, y_batch, y_pred)
                self.beta -= self.lr * grad  # Update weights

            avg_loss = running_loss / n_samples
            self.losses.append(avg_loss)

            # Validation loss (optional)
            if X_val is not None:
                val_pred = self.sigmoid(np.dot(X_val, self.beta)) 
                val_loss = self.binary_cross_entropy(y_val, val_pred)
                self.val_losses.append(val_loss)
            else:
                self.val_losses.append(None)

            # Print progress
            if epoch % 100 == 0 or epoch == self.epochs - 1:
                print(f"Epoch {epoch+1}, Loss: {avg_loss:.4f}", end="")
                if X_val is not None:
                    print(f", Val Loss: {val_loss:.4f}")
                else:
                    print()

    def plot_loss(self):
        """
        Plot the training and validation loss over epochs.
        """
        plt.plot(self.losses, label="Train Loss")
        if any(v is not None for v in self.val_losses):
            plt.plot([v if v is not None else np.nan for v in self.val_losses], label="Validation Loss")
        plt.xlabel("Epoch")
        plt.ylabel("Loss")
        plt.title("Training and Validation Loss")
        plt.legend()
        plt.grid(True)
        plt.show()
