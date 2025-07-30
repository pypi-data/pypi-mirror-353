import numpy as np
from .activation_functions import ActivationFunctions
from .loss_functions import LossFunctions
from typing import Optional

class Layer:
    """
    Represents a single layer in the neural network.

    Args:
        units (int): Number of neurons in the layer.
        activation (Optional[str]): Activation function name (e.g., 'relu', 'sigmoid').
    """
    def __init__(self, units: int, activation: Optional[str] = None):
        self.units = units
        self.activation = activation

    def __repr__(self):
        return f"Layer(units={self.units}, activation={self.activation})"


class NeuralNetwork:
    """
    Fully connected feedforward neural network.

    Args:
        architecture (list): List of Layer objects defining the network structure.
        criterion (str): Loss function name ('mse', 'bce', etc.).
        learning_rate (float): Learning rate for gradient descent.
        random_seed (int, optional): Random seed for reproducibility.
    """
    def __init__(self, architecture, criterion="mse", learning_rate=0.01, random_seed=None):
        if random_seed is not None:
            np.random.seed(random_seed)

        self.architecture = architecture
        self.criterion = criterion
        self.lr = learning_rate
        self.num_features = None
        self.L, self.params = self.initialize()
        self.loss_fn, self.d_loss_fn = LossFunctions.get(criterion)

    def initialize(self):
        """
        Initializes weights and biases for all layers using He or Xavier initialization.

        Returns:
            tuple: 
                - int: Number of layers excluding input.
                - dict: Dictionary containing initialized parameters.
        """
        layers_neuron = [layer.units for layer in self.architecture]
        layers_activation = [layer.activation for layer in self.architecture]

        L = len(layers_neuron) - 1
        params = {"A0": None}

        for i in range(1, L + 1):
            fan_in = layers_neuron[i - 1]
            if self.num_features is None:
                self.num_features = fan_in

            if layers_activation[i] in ["relu","leaky_relu"]:
                params[f"W{i}"] = np.random.randn(layers_neuron[i], fan_in) * np.sqrt(2 / fan_in)
            else:
                params[f"W{i}"] = np.random.randn(layers_neuron[i], fan_in) * np.sqrt(1 / fan_in)

            params[f"b{i}"] = np.zeros((layers_neuron[i], 1))
            params[f"activation{i}"] = layers_activation[i] or "linear"

        return L, params

    def summary(self):
        """
        Prints a summary of the model architecture, including layer types,
        output shapes, number of parameters, and activation functions.
        """
        print("\n-------------------- Model Summary ---------------------")
        print(f"{'Layer':<9}{'Type':<10}{'Output Shape':<20}{'Params':<10}{'Activation'}")
        print("------------------------------------------------------------")

        total_params = 0
        print(f"{0:<9}{'Input':<10}{str((self.num_features,)):<20}{0:<10}{'None'}")

        for i in range(1, self.L + 1):
            output_dim = self.params[f"W{i}"].shape[0]
            weight_shape = self.params[f"W{i}"].shape
            bias_shape = self.params[f"b{i}"].shape

            param_count = np.prod(weight_shape) + np.prod(bias_shape)
            total_params += param_count

            activation = self.params[f"activation{i}"] or "linear"
            print(f"{i:<9}{'Dense':<10}{str((output_dim,)):<20}{param_count:<10}{activation}")

        print("------------------------------------------------------------")
        print(f"Total parameters: {total_params}")
        print("------------------------------------------------------------\n")

    def feedforward(self, X):
        """
        Performs the forward pass of the neural network.

        Args:
            X (ndarray): Input data of shape (features, samples).

        Returns:
            ndarray: Output of the final layer (predictions).
        """
        self.params["A0"] = X
        for i in range(1, self.L + 1):
            self.params[f"Z{i}"] = self.params[f"W{i}"] @ self.params[f"A{i - 1}"] + self.params[f"b{i}"]
            act_fn, _ = ActivationFunctions.get(self.params[f"activation{i}"])
            self.params[f"A{i}"] = act_fn(self.params[f"Z{i}"])
        return self.params[f"A{self.L}"]

    def backprop(self, y):
        """
        Performs the backward pass (backpropagation) and computes gradients.

        Args:
            y (ndarray): Ground truth labels of shape (1, samples) or (classes, samples).

        Returns:
            tuple:
                - dict: Gradients of loss with respect to parameters.
                - float: Loss value.
                - float: Accuracy score.
        """
        loss = self.loss_fn(y, self.params[f"A{self.L}"])
        accu = self.accuracy(y, self.params[f"A{self.L}"])

        grads = {}
        grads[f"dL/dA{self.L}"] = self.d_loss_fn(y, self.params[f"A{self.L}"])

        for i in reversed(range(1, self.L + 1)):
            _, d_act = ActivationFunctions.get(self.params[f"activation{i}"])
            if self.params[f"activation{i}"] == "softmax":
                grads[f"dL/dZ{i}"] = grads[f"dL/dA{i}"]
            else:
                grads[f"dL/dZ{i}"] = grads[f"dL/dA{i}"] * d_act(self.params[f"Z{i}"])
            grads[f"dL/dW{i}"] = grads[f"dL/dZ{i}"] @ self.params[f"A{i - 1}"].T
            grads[f"dL/db{i}"] = np.sum(grads[f"dL/dZ{i}"], axis=1, keepdims=True)
            if i > 1:
                grads[f"dL/dA{i - 1}"] = self.params[f"W{i}"].T @ grads[f"dL/dZ{i}"]

        return grads, loss, accu

    def accuracy(self, y_true, y_pred):
        """
        Computes a performance metric based on the task type:
        
        - For binary classification: returns accuracy.
        - For multi-class classification: returns accuracy.
        - For regression: returns R² score.

        The method automatically infers the task type from the prediction shape 
        and the loss function used.

        Args:
            y_true (ndarray): Ground truth labels. Shape (1, N) or (N,) for classification.
            y_pred (ndarray): Predictions from the model. Shape (1, N) for binary/regression,
                            (C, N) for multi-class classification.

        Returns:
            float: Accuracy (for classification) or R² score (for regression).
        """

        y_true = y_true.reshape(1, -1)
        if y_pred.shape[0] == 1:
            if self.criterion == "bce":
                preds = (y_pred > 0.5).astype(int)
                return np.mean(preds.flatten() == y_true.flatten())
            else:
                ss_res = np.sum((y_true - y_pred) ** 2)
                ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
                return 1 - ss_res / ss_tot
        else:
            y_pred_classes = np.argmax(y_pred, axis=0)
            y_true_classes = y_true.flatten()
            return np.mean(y_pred_classes == y_true_classes)

    def train(self, X, y, epochs=100, batch_size=32, val_split=0.3,log_every=None):
        """
        Trains the neural network using mini-batch gradient descent.

        Args:
            X (ndarray): Input data of shape (samples, features).
            y (ndarray): Target labels of shape (samples,) or (samples, 1).
            epochs (int): Number of training epochs.
            batch_size (int): Mini-batch size.
            val_split (float): Proportion of data to use for validation.
            log_every (int, optional): Logging interval in epochs; if None, logs adaptively.

        Returns:
            dict: Training history with loss and accuracy for both training and validation sets.
        """
        if log_every is not None:
            # Fixed interval logging
            log_points = set(range(1, epochs + 1, log_every))
            log_points.add(epochs)  # always log last epoch
        else:
            # Adaptive logging: all epochs if <=10, else 10 logs evenly spaced
            if epochs <= 10:
                log_points = set(range(1, epochs + 1))
            else:
                log_points = set(np.linspace(1, epochs, num=10, dtype=int))

        n, d = X.shape
        y = y.reshape(-1, 1)
        train_size = int(n * (1 - val_split))
        idx = np.random.permutation(n)
        train_idx, val_idx = idx[:train_size], idx[train_size:]

        x_train, x_val = X[train_idx].T, X[val_idx].T
        y_train, y_val = y[train_idx].reshape(1, -1), y[val_idx].reshape(1, -1)

        history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

        for epoch in range(epochs):
            running_loss = 0.0
            running_accu = 0.0
            n_train = x_train.shape[1]

            indices = np.random.permutation(n_train)
            shuffled_x = x_train[:, indices]
            shuffled_y = y_train[:, indices]

            for start in range(0, n_train, batch_size):
                end = start + batch_size
                batch_x = shuffled_x[:, start:end]
                batch_y = shuffled_y[:, start:end]

                y_pred = self.feedforward(batch_x)
                grads, loss, accu = self.backprop(batch_y)

                running_loss += loss * batch_x.shape[1]
                running_accu += accu * batch_x.shape[1]

                for i in range(1, self.L + 1):
                    self.params[f"W{i}"] -= self.lr * grads[f"dL/dW{i}"]
                    self.params[f"b{i}"] -= self.lr * grads[f"dL/db{i}"]

            avg_train_loss = running_loss / n_train
            avg_train_accu = running_accu / n_train

            history["train_loss"].append(avg_train_loss)
            history["train_acc"].append(avg_train_accu)

            y_val_pred = self.predict_proba(x_val.T)
            val_loss = self.loss_fn(y_val, y_val_pred)
            val_accu = self.accuracy(y_val, y_val_pred)

            history["val_loss"].append(val_loss)
            history["val_acc"].append(val_accu)

            if (epoch + 1) in log_points:
                print(f"Epoch [{epoch + 1:>{len(str(epochs))}}/{epochs}] | "
                    f"Train Loss: {avg_train_loss:.4f}, Train Acc: {avg_train_accu:.4f} | "
                    f"Val Loss: {val_loss:.4f}, Val Acc: {val_accu:.4f}")


        return history

    def predict_proba(self, X):
        """
        Makes predictions on new data.

        Args:
            X (ndarray): Input data of shape (samples, features).

        Returns:
            ndarray: Model predictions.
        """
        A = X.T
        for i in range(1, self.L + 1):
            Z = self.params[f"W{i}"] @ A + self.params[f"b{i}"]
            act_fn, _ = ActivationFunctions.get(self.params[f"activation{i}"])
            A = act_fn(Z)
        return A
    def predict(self, X):
        """
        Makes final predictions on new data.

        - For binary classification: returns class labels (0 or 1).
        - For multi-class classification: returns class indices.
        - For regression: returns continuous outputs.

        Args:
            X (ndarray): Input data of shape (samples, features).

        Returns:
            ndarray: Predicted values or class labels.
        """
        proba = self.predict_proba(X)

        if proba.shape[0] == 1:
            if self.criterion == "bce":
                return (proba > 0.5).astype(int).flatten()
            else:
                return proba.flatten()
        else:
            return np.argmax(proba, axis=0)

    def score(self, X, y, return_loss=False):
        """
        Computes the accuracy or R² score and optionally returns the loss.

        Args:
            X (ndarray): Input data of shape (samples, features).
            y (ndarray): Ground truth labels or targets.
            return_loss (bool): Whether to also return the loss.

        Returns:
            float or tuple: Accuracy or (accuracy, loss) if return_loss is True.
        """
        y_pred = self.predict_proba(X)
        y_true = y.reshape(1, -1)
        acc = self.accuracy(y_true, y_pred)
        if return_loss:
            loss = self.loss_fn(y_true, y_pred)
            return acc, loss
        return acc
