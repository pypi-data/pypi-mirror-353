import numpy as np   
class LossFunctions:
    @staticmethod
    def bce(y, y_pred):
        y = y.reshape(1, -1)
        y_pred = np.clip(y_pred, 1e-9, 1 - 1e-9)
        return -np.mean(y * np.log(y_pred) + (1 - y) * np.log(1 - y_pred))

    @staticmethod
    def d_bce(y, y_pred):
        y = y.reshape(1, -1)
        y_pred = np.clip(y_pred, 1e-9, 1 - 1e-9)
        m = y.shape[1]
        return (y_pred - y) / (y_pred * (1 - y_pred)) / m

    @staticmethod
    def cross_entropy(y, y_pred):
        y = y.reshape(1, -1)
        m = y.shape[1]
        num_classes = y_pred.shape[0]
        y_one_hot = np.eye(num_classes)[y.astype(int).flatten()].T
        y_pred = np.clip(y_pred, 1e-9, 1 - 1e-9)
        return -np.sum(np.log(y_pred) * y_one_hot) / m

    @staticmethod
    def d_cross_entropy(y, y_pred):
        y = y.reshape(1, -1)
        m = y.shape[1]
        num_classes = y_pred.shape[0]
        y_one_hot = np.eye(num_classes)[y.astype(int).flatten()].T
        return (y_pred - y_one_hot) / m

    @staticmethod
    def mse(y, y_pred):
        y = y.reshape(1, -1)
        return np.mean((y - y_pred) ** 2)

    @staticmethod
    def d_mse(y, y_pred):
        y = y.reshape(1, -1)
        m = y.shape[1]
        return 2 * (y_pred - y) / m

    @staticmethod
    def mae(y, y_pred):
        y = y.reshape(1, -1)
        return np.mean(np.abs(y - y_pred))

    @staticmethod
    def d_mae(y, y_pred):
        y = y.reshape(1, -1)
        m = y.shape[1]
        return np.sign(y_pred - y) / m

    @staticmethod
    def get(name):
        if name == "mse":
            return LossFunctions.mse, LossFunctions.d_mse
        elif name == "bce":
            return LossFunctions.bce, LossFunctions.d_bce
        elif name == "mae":
            return LossFunctions.mae, LossFunctions.d_mae
        elif name == "ce":
            return LossFunctions.cross_entropy, LossFunctions.d_cross_entropy
        else:
            raise ValueError(f"Unsupported loss function: {name}")

