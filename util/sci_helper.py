import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA

def moving_average(t,x,n=10):

    t_aug = np.concatenate(( np.zeros(n-1), np.array(t) ))
    x_aug = np.concatenate(( np.zeros(n-1), np.array(x) ))

    ret = np.cumsum( x_aug, dtype='float')
    ret[n:] = ret[n:] - ret[:-n]
    return t_aug[n-1:], ret[n-1:]/n

def clustering(x, y, z, t,
               linking_length = 1.0, linking_time = 1.0,
               min_samples = 2):
    
    time_to_length_factor = linking_length / linking_time
    time_converted_to_space = t * time_to_length_factor

    positions = np.transpose(np.array([ x, y, z, time_converted_to_space ]))

    dbscan_results = DBSCAN( eps=linking_length, min_samples=min_samples ).fit(positions)
    
    clusterid_of_point = dbscan_results.labels_

    no_of_clusters = max(clusterid_of_point) + 1
    clustersize_of_cluster = [ np.sum(clusterid_of_point==nClus) for nClus in range(no_of_clusters) ]
    clustersize_of_cluster.append(1) # want size of cluster [-1] (last index, unclustered) to be 1

    return clusterid_of_point, clustersize_of_cluster, no_of_clusters

def fit_pca(X, n_components=None):

    pipe = Pipeline([
        ("scaler", StandardScaler()),
        ("pca",    PCA(n_components=n_components)),
    ])
    pipe.fit(X)
    pca = pipe.named_steps["pca"]
    
    return pca.components_, pca.explained_variance_ratio_