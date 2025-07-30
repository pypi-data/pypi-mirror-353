import numpy as np

class ActivationFunctions:
    # Activation Functions and Derivatives
    @staticmethod
    def step(z): 
        return np.where(z >= 0, 1, 0)
    @staticmethod
    def d_step(z): 
        return np.zeros_like(z)

    @staticmethod
    def linear(z): 
        return z
    @staticmethod
    def d_linear(z): 
        return np.ones_like(z)
    
    @staticmethod
    def sigmoid(z): 
        z = np.clip(z, -500, 500)
        return 1 / (1 + np.exp(-z))
    @staticmethod
    def d_sigmoid(z): 
        return ActivationFunctions.sigmoid(z) * (1 - ActivationFunctions.sigmoid(z))

    @staticmethod
    def tanh(z): 
        z = np.clip(z, -500, 500)
        return np.tanh(z)
    @staticmethod
    def d_tanh(z): 
        return 1 - np.tanh(z) ** 2
    
    @staticmethod
    def relu(z): 
        return np.maximum(0, z)
    @staticmethod
    def d_relu(z): 
        return np.where(z > 0, 1, 0)
    
    @staticmethod
    def leaky_relu(z,alpha=0.01): 
        return np.where(z > 0, z, alpha * z)
    @staticmethod
    def d_leaky_relu(z,alpha=0.01): 
        return np.where(z > 0, 1, alpha)
    
    @staticmethod
    def elu(z,alpha=0.01): 
        return np.where(z >= 0, z, alpha * (np.exp(z) - 1))
    @staticmethod
    def d_elu(z,alpha=0.01): 
        return np.where(z >= 0, 1, alpha * np.exp(z))
    
    @staticmethod
    def selu(z,selu_lambda,selu_alpha): 
        return selu_lambda * np.where(z >= 0, z, selu_alpha * (np.exp(z) - 1))
    @staticmethod
    def d_selu(z,selu_lambda,selu_alpha): 
        return selu_lambda * np.where(z >= 0, 1, selu_alpha * np.exp(z))
    
    @staticmethod
    def gelu(z): 
        return 0.5 * z * (1 + np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z**3)))
    @staticmethod
    def d_gelu(z):
        tanh_term = np.tanh(np.sqrt(2 / np.pi) * (z + 0.044715 * z**3))
        left = 0.5 * (1 + tanh_term)
        sech2 = 1 - tanh_term**2
        right = 0.5 * z * sech2 * (np.sqrt(2 / np.pi) * (1 + 3 * 0.044715 * z**2))
        return left + right
    
    @staticmethod
    def swish(z):
        return z / (1 + np.exp(-z))
    @staticmethod
    def d_swish(z):
        sig = ActivationFunctions.sigmoid(z)
        return sig + z * sig * (1 - sig)
    
    @staticmethod
    def softmax(z):
        exp_z = np.exp(z - np.max(z, axis=0, keepdims=True))
        return exp_z / np.sum(exp_z, axis=0, keepdims=True)
    @staticmethod
    def d_softmax(z):
        # Derivative of softmax combined with cross-entropy is simplified in backprop
        # Usually handled in loss derivative, so just return 1 for chain rule
        return np.ones_like(z)

    # Get The Sellected Activation
    @staticmethod
    def get(name):
        activations = {
            "linear": (ActivationFunctions.linear, ActivationFunctions.d_linear),
            "step": (ActivationFunctions.step, ActivationFunctions.d_step),
            "sigmoid": (ActivationFunctions.sigmoid, ActivationFunctions.d_sigmoid),
            "relu": (ActivationFunctions.relu, ActivationFunctions.d_relu),
            "leaky_relu": (ActivationFunctions.leaky_relu, ActivationFunctions.d_leaky_relu),
            "tanh": (ActivationFunctions.tanh, ActivationFunctions.d_tanh),
            "elu": (ActivationFunctions.elu, ActivationFunctions.d_elu),
            "selu": (ActivationFunctions.selu, ActivationFunctions.d_selu),
            "gelu": (ActivationFunctions.gelu, ActivationFunctions.d_gelu),
            "swish": (ActivationFunctions.swish, ActivationFunctions.d_swish),
            "softmax": (ActivationFunctions.softmax, ActivationFunctions.d_softmax)
        }
        if name not in activations:
            raise ValueError(f"Unknown activation function: {name}")
        return activations[name]
 