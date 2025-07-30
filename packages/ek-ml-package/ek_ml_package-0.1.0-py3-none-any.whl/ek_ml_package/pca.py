import numpy as np

class PCA:
    def __init__(self, n_component: int):
        """
        Initialize PCA with the number of principal components to retain.

        Parameters:
        - n_component: int
            The number of top principal components to keep.
        """
        self.n_component = n_component
        self.eigen_vectors_sorted: np.ndarray | None = None
        self.explained_variance: np.ndarray | None = None
        self.cum_explained_variance: np.ndarray | None = None
        self.mean_: np.ndarray | None = None  
        self.std_: np.ndarray | None = None 
        self.X_std: np.ndarray | None = None
        self.X_proj: np.ndarray | None = None

    def mean(self, X: np.ndarray) -> np.ndarray:
        """
        Compute the mean of each feature.

        Parameters:
        - X: np.ndarray, shape (n_samples, n_features)

        Returns:
        - mean: np.ndarray, shape (n_features,)
        """
        return np.mean(X, axis=0)

    def std(self, X: np.ndarray) -> np.ndarray:
        """
        Compute the standard deviation of each feature (with Bessel's correction).

        Parameters:
        - X: np.ndarray

        Returns:
        - std_dev: np.ndarray
        """
        return np.std(X, axis=0, ddof=1)

    def standardize_data(self, X: np.ndarray) -> np.ndarray:
        """
        Standardize the dataset to have zero mean and unit variance.

        Parameters:
        - X: np.ndarray

        Returns:
        - standardized_X: np.ndarray
        """
        self.mean_ = self.mean(X)
        self.std_ = self.std(X)
        return (X - self.mean_) / self.std_

    def covariance(self, X: np.ndarray) -> np.ndarray:
        """
        Compute the covariance matrix of the standardized data.

        Parameters:
        - X: np.ndarray, shape (n_samples, n_features)

        Returns:
        - covariance_matrix: np.ndarray, shape (n_features, n_features)
        """
        n, d = X.shape
        return (1 / (n - 1)) * (X.T @ X)

    def fit(self, X: np.ndarray) -> None:
        """
        Fit the PCA model by computing the eigenvalues and eigenvectors
        of the covariance matrix.

        Parameters:
        - X: np.ndarray, shape (n_samples, n_features)
        """
        # Step 1: Standardize the data
        self.X_std = self.standardize_data(X=X)

        # Step 2: Compute the covariance matrix
        Cov_mat = self.covariance(X=self.X_std)

        # Step 3: Compute eigenvalues and eigenvectors
        eigen_values, eigen_vectors = np.linalg.eig(Cov_mat)

        # Step 4: Sort eigenvectors by descending eigenvalue magnitude
        idx = np.array([np.abs(i) for i in eigen_values]).argsort()[::-1]
        eigen_values_sorted = eigen_values[idx]
        self.eigen_vectors_sorted = eigen_vectors.T[:, idx]

        # Step 5: Compute explained variance ratios
        total = np.sum(eigen_values)
        explained_variance = [(i / total) * 100 for i in eigen_values_sorted]
        self.explained_variance = np.round(explained_variance, 2)
        self.cum_explained_variance = np.cumsum(explained_variance)

    def transform(self) -> np.ndarray:
        """
        Project the standardized data onto the top-k principal components.

        Returns:
        - projected_data: np.ndarray, shape (n_samples, n_component)
        """
        if self.X_std is None or self.eigen_vectors_sorted is None:
            raise ValueError("Model must be fit before calling transform.")

        # Select top-k eigenvectors (principal components)
        V = self.eigen_vectors_sorted[:self.n_component, :]

        # Project standardized data onto the new subspace
        self.X_proj = self.X_std @ V.T
        return self.X_proj

    def inverse_transform(self) -> np.ndarray:
        """
        Reconstruct the standardized data from the projected data.

        Returns:
        - X_approx: np.ndarray, shape (n_samples, n_features)
        """
        if self.X_proj is None or self.eigen_vectors_sorted is None:
            raise ValueError("Must call transform() before inverse_transform().")

        # Use stored projection and components
        V = self.eigen_vectors_sorted[:self.n_component, :]
        X_std_approx = self.X_proj @ V
        return X_std_approx

    def unstandardize(self, X_std: np.ndarray) -> np.ndarray:
        """
        Unstandardize the data back to the original scale using stored mean and std.

        Parameters:
        - X_std: Standardized reconstructed data

        Returns:
        - X_approx: Reconstructed data on the original scale
        """
        if self.mean_ is None or self.std_ is None:
            raise ValueError("Standardization parameters not found.")

        return X_std * self.std_ + self.mean_

