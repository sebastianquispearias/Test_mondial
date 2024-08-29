import numpy as np

'''
É uma classe que operacionaliza uma estrutura baseada na arquitetura da biblioteca scikit-learn.
Este ensemble foi o método escolhido para fazer a deteção de anomalias em nossos dados.
Contém as funções fit, predict e fit_predict.
'''

class Model():
    def __init__(self):
        pass

    def fit(self, x):
        pass

    def predict(self, x):
        pass

    def fit_predict(self, x):
        pass

class ZSCORE(Model):
    def __init__(self, thres = 3):
        self.thres = 3
        self.mean = None
        self.std = None

    def fit(self, x):
        self.mean = np.mean(x)
        self.std = np.std(x)

    def predict(self, x):
        z_score = (x-self.mean)/self.std 
        return np.abs(z_score) > self.thres

    def fit_predict(self, x):
        self.fit(x)
        return self.predict(x)

class IQR(Model):
    def __init__(self):
        self.q1 = None
        self.q3 = None

    def fit(self, x):
        self.q1 = x.quantile(0.25)
        self.q3 = x.quantile(0.75)

    def predict(self, x):
        IQR = self.q1 - self.q3
        delta_iqr = 1.5 * IQR
        left = x < (self.q1 - delta_iqr)
        right = x > (self.q3 + delta_iqr)
        return left | right

    def fit_predict(self, x):
        self.fit(x)
        return self.predict(x)

class VoteEnsemble(Model):
    def __init__(self, thres=0):
        self.thres = thres
        self.models = [IQR(), ZSCORE()]

    def fit(self, x):
        for model in self.models:
            model.fit(x)

    def predict(self, x):
        outputs = np.empty(shape=len(x))
        for model in self.models:
            y_ = model.predict(x)
            outputs += y_
        return y_ > self.thres

    def fit_predict(self, x):
        self.fit(x)
        return self.predict(x)
