import numpy as np
class Kmeans:
    def __init__(self,k,max_iters=100, initialization = "kmean++",random_state=None,tol=1e-4):
        """
        KMeans clustering class.

        Parameters:
        - k: number of clusters
        - max_iters: maximum iterations to run
        - initialization: 'kmean++' or 'random'
        - random_state: seed for reproducibility
        - tol: convergence tolerance
        """
        self.k = k
        self.centroids = None
        self.labels = None
        self.tol = tol
        self.max_iters = max_iters
        self.initialization = initialization
        self.random_state = random_state
    
    def distance(self,c, x):
        """Compute Euclidean distance between point c and x."""
        return np.sqrt(np.sum((c - x) ** 2))
    
    def random_centroids_initialzation(self,X):
        """Randomly initialize centroids from dataset X."""
        idx = np.random.choice(len(X),self.k,replace=False)
        return  X[idx]

    def softmax(self,x):
        """Apply softmax function to vector x."""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    def kmeans_plusplus_centroids_initialzation(self,X):
        """Initialize centroids using KMeans++ algorithm."""
        n_samples = X.shape[0]
        centroids = []
        first_centroids = X[np.random.choice(n_samples)]
        centroids.append(first_centroids)

        for i in range(self.k - 1):
            d = np.array([
                min(self.distance(c,x) for c in centroids)
                for x in X
            ])
            probabilities = self.softmax(d)
            new_centroids_index = np.random.choice(n_samples, p=probabilities)
            centroids.append(X[new_centroids_index])

        return np.array(centroids)

    def assign_clusters(self,X):
        """Assign each point in X to the nearest centroid."""
        labels = np.array([
            np.argmin([self.distance(c, x) for c in self.centroids])
            for x in X
        ])
        return labels

    def compute_centroids(self,X,labels):
        """Compute new centroids based on current labels."""
        centroids = []
        for i in range(self.k):
            cluster_points = X[labels == i]
            if len(cluster_points) > 0:
                centroid = np.mean(cluster_points, axis=0)
            else:
                centroid = X[np.random.randint(0, len(X))]
            centroids.append(centroid)
        return np.array(centroids)

    def is_converged(self,centroids, new_centroids):
        """Check if centroids have converged"""
        shift = np.linalg.norm(centroids - new_centroids)
        return shift < self.tol
    
    def compute_inertia(self,X, labels, centroids):
        """Compute inertia (sum of squared distances from points to their centroids)."""
        inertia = 0.0
        for x, label in zip(X, labels):
            inertia += np.sum((x - centroids[label]) ** 2)
        return inertia
    
    def predict(self,X):
        """Predict the cluster label for each point in X based on trained centroids."""
        labels = []
        for x in X:
            distances = [self.distance(c, x) for c in self.centroids]
            label = np.argmin(distances)
            labels.append(label)
        return np.array(labels)
    

    # Kmeans Function
    def fit(self,X):

        # Seed
        if self.random_state:
            np.random.seed(self.random_state)

        # Initialize Centroids
        if self.initialization == "kmean++":
            self.centroids = self.kmeans_plusplus_centroids_initialzation(X)
        elif  self.initialization == "random":
            self.centroids = self.random_centroids_initialzation(X)
        else:
            raise ValueError("Invalid initialization method. Use 'random' or 'kmean++'.")


        converged = False
        n_iter = 0
        for i in range(self.max_iters):

            # Assign each point to the nearest centroid
            labels = self.assign_clusters(X)

            # Group points by cluster
            clusters = [[] for _ in range(self.k)]
            for point, label in zip(X, labels):
                clusters[label].append(point)

            # Compute new centroids
            new_centroids = self.compute_centroids(X, labels)

            # Convergence check
            if self.is_converged(self.centroids,new_centroids):
                converged = True
                break

            self.centroids = new_centroids
            n_iter+=1
        self.inertia = self.compute_inertia(X, labels, self.centroids)
        self.n_iter = n_iter+1
        self.clusters = clusters
        self.labels = labels