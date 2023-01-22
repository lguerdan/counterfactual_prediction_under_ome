import numpy as np
import pandas as pd
from numpy.random import permutation


def generate_jobs_data(benchmark_config, error_params, train_ratio=.75, shuffle=True):

    with np.load(benchmark_config.train_path) as f:
        train_data = {key:f[key] for key in f}

    with np.load(benchmark_config.test_path) as f:
        test_data = {key:f[key] for key in f}

    X = np.concatenate((train_data['x'][:,:,0],  test_data['x'][:,:,0]), axis=0)
    YS = 1-np.concatenate((train_data['yf'][:,0], test_data['yf'][:,0]), axis=0) # Positve outcome: unemployment (15%)
    D = np.concatenate((train_data['t'][:,0], test_data['t'][:,0]), axis=0)
    E = np.concatenate((train_data['e'][:,0], test_data['e'][:,0]), axis=0)
    pD = np.ones_like(D) * D.mean()

    YS_0 = np.zeros_like(YS)
    YS_1 = np.zeros_like(YS)
    YS_0[D==0] = YS[D==0]
    YS_1[D==1] = YS[D==1]

    Y_0 = YS_0.copy()
    Y_1 = YS_1.copy()
    Y = np.zeros_like(YS)

    alpha_0_errors = np.random.binomial(1, error_params['alpha_0'], size=YS.shape[0])
    alpha_1_errors = np.random.binomial(1, error_params['alpha_1'], size=YS.shape[0])
    beta_0_errors = np.random.binomial(1, error_params['beta_0'], size=YS.shape[0])
    beta_1_errors = np.random.binomial(1, error_params['beta_1'], size=YS.shape[0])

    Y_0[(Y_0 == 0) & (alpha_0_errors == 1)] = 1
    Y_0[(Y_0 == 1) & (beta_0_errors == 1)] = 0
    Y_1[(Y_1 == 0) & (alpha_1_errors == 1)] = 1
    Y_1[(Y_1 == 1) & (beta_1_errors == 1)] = 0

    Y[D==0] = Y_0[D==0]
    Y[D==1] = Y_1[D==1]

    dataset_y = {
        'YS': YS,
        'YS_0': YS_0,
        'YS_1': YS_1,
        'Y_0': Y_0,
        'Y_1': Y_1,
        'Y': Y,
        'pD': np.ones_like(D) * D.mean(),
        'pD_hat': np.ones_like(D) * D[E==1].mean(),
        'D': D,
        'E': E # Include for computign the ATT on JOBS test data
    }
    X, Y = pd.DataFrame(X), pd.DataFrame(dataset_y)
    
    # Normalize data
    X = (X - X.mean(axis=0))/X.std(axis=0)

    if shuffle: 
        suffle_ix = permutation(X.index)
        X = X.iloc[suffle_ix]
        Y = Y.iloc[suffle_ix]

    # Always use the same held-out test split
    split_ix = int(X.shape[0]*train_ratio)
    X_train = X[:split_ix]
    X_test = X[split_ix:]
    Y_train = Y[:split_ix]
    Y_test = Y[split_ix:]
        
    return X_train, X_test, Y_train, Y_test
