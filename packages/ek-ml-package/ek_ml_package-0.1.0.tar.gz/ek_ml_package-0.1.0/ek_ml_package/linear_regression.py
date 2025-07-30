import numpy as np
import matplotlib.pyplot as plt

class LinearRegression:
    def __init__(self, lr=0.01, epochs=1000, method='gd', batch_size=None, momentum=0.0):
        """
        Initialize the Linear Regression model.

        Args:
            lr: Learning rate for gradient descent updates.
            epochs: Number of training iterations (epochs).
            method: Optimization method - 'gd' (batch), 'sgd' (stochastic), or 'minibatch'.
            batch_size: Batch size for mini-batch gradient descent.
            momentum: Momentum factor for SGD optimization.
        """
        self.weights = None              # Model weights (to be initialized later)
        self.lr = lr                     # Learning rate
        self.epochs = epochs             # Number of epochs
        self.method = method             # Optimization method
        self.batch_size = batch_size     # Batch size (used in 'minibatch' method)
        self.momentum = momentum         # Momentum factor (used in 'sgd' method)
        self.losses = []                 # Training loss history
        self.val_losses = []             # Validation loss history

    def predict(self, X):
        """
        Predict target values for input data.

        Args:
            X: Input features (N, D)

        Returns:
            Predicted values (N,)
        """
        return np.dot(self.add_ones(X), self.weights).flatten()

    def add_ones(self, X):
        """
        Add bias term (column of 1s) to input features.

        Args:
            X: Input data (N, D)

        Returns:
            Augmented data (N, D+1)
        """
        return np.hstack((X, np.ones((X.shape[0], 1))))

    def initialize_weights(self, n_features):
        """
        Initialize model weights to zeros.

        Args:
            n_features: Number of features (including bias)

        Returns:
            Weight matrix (D+1, 1)
        """
        return np.zeros((n_features, 1))

    def compute_loss(self, y_true, y_pred):
        """
        Compute Mean Squared Error (MSE) loss.

        Args:
            y_true: Actual values (N, 1)
            y_pred: Predicted values (N, 1)

        Returns:
            Scalar MSE loss
        """
        return np.mean((y_true - y_pred) ** 2)

    def compute_gradients(self, X, y_true, y_pred):
        """
        Compute gradient of MSE loss with respect to weights.

        Args:
            X: Input features (N, D)
            y_true: True labels (N, 1)
            y_pred: Predictions (N, 1)

        Returns:
            Gradient (D, 1)
        """
        return (2 / X.shape[0]) * (X.T @ y_pred - X.T @ y_true)

    def fit(self, X, y, validation_split=0.0):
        """
        Train the Linear Regression model using chosen optimization method.

        Args:
            X: Input features (N, D)
            y: Target values (N,)
            validation_split: Fraction of data to use for validation (0.0 to 1.0)
        """
        y = y.reshape(-1, 1)             # Ensure y is column vector
        X = self.add_ones(X)             # Add bias column

        # Create validation set if requested
        if 0.0 < validation_split < 1.0:
            indices = np.random.permutation(X.shape[0])
            val_size = int(X.shape[0] * validation_split)

            val_indices = indices[:val_size]
            train_indices = indices[val_size:]

            X_val = X[val_indices]
            y_val = y[val_indices]
            X_train = X[train_indices]
            y_train = y[train_indices]
        else:
            X_train, y_train = X, y
            X_val, y_val = None, None

        n_samples, n_features = X_train.shape
        self.weights = self.initialize_weights(n_features)  # Initialize weights

        # Training loop
        for i in range(self.epochs):
            if self.method == 'gd':
                # -------------------------------
                # Batch Gradient Descent
                # -------------------------------
                y_pred = np.dot(X_train, self.weights)
                loss = self.compute_loss(y_train, y_pred)
                grad = self.compute_gradients(X_train, y_train, y_pred)
                self.weights -= self.lr * grad  # Update weights

            elif self.method == 'sgd':
                # -------------------------------
                # Stochastic Gradient Descent
                # -------------------------------
                running_loss = 0.0
                velocity = np.zeros((n_features, 1))  # Momentum term
                idx = np.random.permutation(n_samples)
                X_shuffled_batch = X_train[idx]
                y_shuffled_batch = y_train[idx]

                for idx in range(X_shuffled_batch.shape[0]):
                    sample_x = X_shuffled_batch[idx].reshape(-1, n_features)
                    sample_y = y_shuffled_batch[idx].reshape(-1, 1)

                    y_pred = np.dot(sample_x, self.weights)
                    loss = self.compute_loss(sample_y, y_pred)
                    running_loss += loss

                    grad = self.compute_gradients(sample_x, sample_y, y_pred)

                    # Momentum update rule
                    velocity = self.momentum * velocity + (1 - self.momentum) * grad
                    self.weights -= self.lr * velocity

                loss = running_loss / n_samples

            elif self.method == 'minibatch':
                # -------------------------------
                # Mini-Batch Gradient Descent
                # -------------------------------
                batch_size = self.batch_size or 32  # Default batch size

                if not isinstance(batch_size, int) or batch_size < 1:
                    raise ValueError("batch_size must be a positive integer for mini-batch gradient descent.")

                running_loss = 0.0
                idx = np.random.permutation(n_samples)
                X_shuffled_batch = X_train[idx]
                y_shuffled_batch = y_train[idx]

                for batch_idx in range(0, n_samples, batch_size):
                    x_batch = X_shuffled_batch[batch_idx: batch_idx + batch_size]
                    y_batch = y_shuffled_batch[batch_idx: batch_idx + batch_size]

                    y_pred = np.dot(x_batch, self.weights)
                    loss = self.compute_loss(y_batch, y_pred)
                    running_loss += (loss * x_batch.shape[0])

                    grad = self.compute_gradients(x_batch, y_batch, y_pred)

                    # Update weights using mini-batch gradient
                    self.weights -= self.lr * grad

                loss = running_loss / n_samples

            else:
                raise ValueError("Method must be 'gd', 'sgd', or 'minibatch'")

            # Track training loss
            self.losses.append(loss)

            # Compute and track validation loss (if applicable)
            if X_val is not None:
                val_pred = np.dot(X_val, self.weights)
                val_loss = self.compute_loss(y_val, val_pred)
                self.val_losses.append(val_loss)
            else:
                self.val_losses.append(None)

            # Display progress every 100 epochs
            if i % 100 == 0:
                print(f"Epoch {i}, Loss: {loss:.4f}", end="")
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
