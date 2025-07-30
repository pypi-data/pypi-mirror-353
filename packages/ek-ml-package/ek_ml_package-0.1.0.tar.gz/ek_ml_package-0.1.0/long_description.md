# Machine Learning Package


**ek_ml_package** is a collection of fundamental machine learning algorithms implemented fully from scratch using Python and NumPy only. Designed basically for learners, educators and researchers, this package emphasizes understanding the core mechanics behind popular machine learning techniques without relying on high-level frameworks like scikit-learn, Pytorch or TensorFlow.

## Key Features

* **Introduction to Machine Learning**
 
  * [Introduction](https://ekbarkacha.github.io/ek_ml_package/)
* **Supervised Learning Algorithms:**

  * [Linear Regression](https://ekbarkacha.github.io/ek_ml_package/linear_regression/)
  * [Logistic Regression](https://ekbarkacha.github.io/ek_ml_package/logistic_regression/)
  * [K-Nearest Neighbors (KNN)](https://ekbarkacha.github.io/ek_ml_package/knn/)
  * [Perceptron](https://ekbarkacha.github.io/ek_ml_package/perceptron/)
  * [Neural Network (from first principles)](https://ekbarkacha.github.io/ek_ml_package/neural_network/)
  * [Gaussian Discriminant Analysis (GDA)](https://ekbarkacha.github.io/ek_ml_package/gaussian_discriminant_analysis/)

* **Unsupervised Learning Algorithms:**

  * [Principal Component Analysis (PCA)](https://ekbarkacha.github.io/ek_ml_package/pca/)
  * [K-Means Clustering](https://ekbarkacha.github.io/ek_ml_package/kmeans/)

* **Utilities:**

  * [Common Activation Functions (ReLU, Sigmoid, Tanh, etc.)](https://ekbarkacha.github.io/ek_ml_package/activation_function/)
  * [Loss Functions (Mean Squared Error, Cross-Entropy, etc.)](https://ekbarkacha.github.io/ek_ml_package/loss_function/)

## Why Use ek_ml_package?

* **From Scratch Implementation:** Each algorithm is built with Python and NumPy only, offering transparent and educational insight into how machine learning models function internally.
* **No External Dependencies:** Avoids reliance on heavy machine learning libraries to maintain simplicity and promote hands-on experimentation.
* **Learning-Focused:** Perfect for students and practitioners wanting to deepen their understanding of machine learning algorithms beyond black-box usage.
* **Extensible & Customizable:** Easily adapt and extend the base code for research, projects or tailored applications.

## Installation

Install the latest stable version from PyPI using:

```bash
pip install ek_ml_package
```
For the latest development version, clone the repository and install manually:

```bash
git clone https://github.com/ekbarkacha/ek_ml_package.git
cd ek_ml_package
pip install -r requirements.txt
pip install -e .
```

## Usage Example: Supervised Learning

### Linear Regression
```python
from ek_ml_package.linear_regression import LinearRegression
import numpy as np

# Generate some toy data
X = np.random.rand(100, 3)
y = X @ np.array([1.5, -2.0, 1.0]) + 0.5 + np.random.randn(100) * 0.1

# Initialize and train model with minibatch gradient descent
model = LinearRegression(lr=0.01, epochs=500, method='minibatch', batch_size=16, momentum=0.9)
model.fit(X, y, validation_split=0.2)

# Predict and check MSE on training data
predictions = model.predict(X)
mse = np.mean((y - predictions) ** 2)
print(f"Train MSE: {mse:.4f}")

# Plot loss
model.plot_loss()
```
### Logistic Regression
```python
import numpy as np
from ek_ml_package.logistic_regression import LogisticRegression

# Generate some synthetic data
np.random.seed(0)
X = np.random.randn(100, 2)
y = (X[:, 0] + X[:, 1] > 0).astype(int)

# Train logistic regression
model = LogisticRegression(lr=0.1, epochs=500, batch_size=16, random_seed=42)
model.fit(X, y, validation_split=0.2)

# Predict probabilities
y_probs = model.predict(X)

# Convert probabilities to classes
y_pred = model.convert_probabilities_to_classes(y_probs)

# Compute accuracy
acc = model.accuracy(y, y_probs)
print(f"Training accuracy: {acc:.2f}")

# Plot loss curve
model.plot_loss()

```

### KNN Classification
```python
from ek_ml_package.knn import KNNClassification
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split

iris = load_iris()
X, y = iris.data, iris.target
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

knn = KNNClassification(k=5)
knn.fit(X_train, y_train)
print("Test accuracy:", knn.accuracy(X_test, y_test))

```

### Gaussian Discriminant Analysis (LDA and QDA)
```python
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from ek_ml_package.gaussian_discriminant_analysis import QDA, LDA

# Generate 2D data with 4 classes
X, y = make_classification(n_samples=500, n_features=2, n_redundant=0,
                           n_informative=2, n_clusters_per_class=1,
                           n_classes=4, random_state=42)

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Train and evaluate LDA
lda = LDA()
lda.fit(X_train, y_train)
y_pred_lda = lda.predict(X_test)
print(f"LDA Accuracy: {lda.accuracy(y_test, y_pred_lda):.4f}")

# Train and evaluate QDA
qda = QDA()
qda.fit(X_train, y_train)
y_pred_qda = qda.predict(X_test)
print(f"QDA Accuracy: {qda.accuracy(y_test, y_pred_qda):.4f}")

```
### Perceptron

```python
import numpy as np
from ek_ml_package.perceptron import Perceptron

# Generate some simple linearly separable data
X = np.array([
    [2, 3],
    [1, 1],
    [2, 1],
    [3, 2],
    [-1, -1],
    [-2, -3],
    [-3, -2],
    [-2, -1]
])

# Labels must be -1 or 1
y = np.array([1, 1, 1, 1, -1, -1, -1, -1])

# Initialize the Perceptron model
model = Perceptron(max_iter=100, tol=1e-5, random_state=42)

# Train the model
model.fit(X, y)

# Make predictions on training data
predictions = np.array([model.predict(x) for x in X])

# Calculate accuracy
acc = model.accuracy(y, predictions)
print(f"Training accuracy: {acc:.2f}%")

# Predict a new sample
new_sample = np.array([0.5, 1.5])
predicted_label = model.predict(new_sample)
print(f"Prediction for new sample {new_sample}: {predicted_label}")

```

### NeuralNetwork
```python
import numpy as np
from ek_ml_package.neural_network import NeuralNetwork, Layer

# Define the network architecture as a list of Layers
architecture = [
    Layer(units=4, activation=None),      # Input layer (4 features)
    Layer(units=10, activation='relu'),  # Hidden layer with 10 neurons and ReLU activation
    Layer(units=3, activation='softmax') # Output layer with 3 neurons (e.g. for 3-class classification)
]

# Initialize the Neural Network
nn = NeuralNetwork(architecture, criterion='ce', learning_rate=0.01, random_seed=42)

# Optional: View model summary
nn.summary()

# Generate dummy data: 100 samples, 4 features
X_train = np.random.randn(100, 4)
y_train = np.random.randint(0, 3, size=(100,))  # Multiclass labels 0,1,2

# Train the network for 50 epochs with batch size 16
history = nn.train(X_train, y_train, epochs=50, batch_size=16)

# Predict class labels on new data
X_test = np.random.randn(10, 4)
predictions = nn.predict(X_test)

print("Predictions:", predictions)

# Evaluate accuracy on training set
accuracy = nn.score(X_train, y_train)
print(f"Training Accuracy: {accuracy:.4f}")
```


## Usage Example: Unsupervised Learning

### PCA

```python
from ek_ml_package.pca import PCA
import numpy as np

# Sample data: 5 samples, 3 features
X = np.array([
    [2.5, 2.4, 0.5],
    [0.5, 0.7, 1.0],
    [2.2, 2.9, 0.3],
    [1.9, 2.2, 0.8],
    [3.1, 3.0, 0.4]
])

# Instantiate PCA to keep 2 principal components
pca = PCA(n_component=2)

# Fit PCA model
pca.fit(X)

# Transform data to lower dimension
X_proj = pca.transform()
print("Projected Data:\n", X_proj)

# Optionally reconstruct approximate original data
X_reconstructed_std = pca.inverse_transform()

# Convert back to original scale
X_reconstructed = pca.unstandardize(X_reconstructed_std)
print("Reconstructed Data (approx):\n", X_reconstructed)

# Reconstruction error
mse = np.mean((X - X_reconstructed)**2)
print(f"Reconstruction MSE: {mse:.4f}")

# Explained variance by each component
print("Explained Variance (%):", pca.explained_variance)
print("Cumulative Explained Variance (%):", pca.cum_explained_variance)

```

### Kmeans

```python
from ek_ml_package.kmeans import Kmeans
import numpy as np

# Create sample data
X = np.array([
    [1.0, 2.0],
    [1.5, 1.8],
    [5.0, 8.0],
    [8.0, 8.0],
    [1.0, 0.6],
    [9.0, 11.0]
])

# Initialize KMeans with 2 clusters, using kmeans++ initialization
kmeans = Kmeans(k=2, max_iters=100, initialization="kmean++", random_state=42)

# Fit model to data
kmeans.fit(X)

# Get cluster labels for input data
labels = kmeans.labels
print("Cluster labels:", labels)

# Access centroids
print("Centroids:\n", kmeans.centroids)

# Compute inertia (sum of squared distances)
print("Inertia:", kmeans.inertia)

# Predict cluster of new points
new_points = np.array([[0, 0], [10, 10]])
predicted_labels = kmeans.predict(new_points)
print("Predicted clusters for new points:", predicted_labels)
```

## Documentation

Extensive documentation and tutorials are available to guide you through the theory and practical implementations of each algorithm:

 [View Documentation](https://ekbarkacha.github.io/ek_ml_package/)

The documentation covers:

- Intuition and theory behind each algorithm  
- Step-by-step derivations and key concepts  

For full implementations, check out the Jupyter notebooks in the [notebooks](https://github.com/ekbarkacha/ek_ml_package/tree/main/notebooks) folder:
- Hands-on code from scratch using Python & NumPy
- Visualizations, training steps, and outputs
- Aligned with each theory doc (e.g., `linear_regression.md` &#8596;`linear_regression.ipynb`)


## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.