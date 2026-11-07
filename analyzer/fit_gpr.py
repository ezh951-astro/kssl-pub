from pathlib import Path

import numpy as np
from scipy.stats.qmc import LatinHypercube
from sklearn.gaussian_process import kernels, GaussianProcessRegressor

from util.ndbin import project_and_marginalize

from analyzer.analyzer_helper import get_input_output_space

class FittedRegressor():

    def __init__(self, cfg, input_train_arr, output_train_arr):

        self.train_xs = input_train_arr
        self.train_ys = output_train_arr

        self.xmins = [ feat['min'] for feat in cfg.inputs.continuous_features ]
        self.xmaxs = [ feat['max'] for feat in cfg.inputs.continuous_features ]

        self.nfeats = len(self.xmins)

        self.ymins = np.min(output_train_arr)
        self.ymaxs = np.max(output_train_arr)

        # assert shape

        kernel = kernels.RBF(length_scale=1.0) + kernels.WhiteKernel(noise_level=1.0, noise_level_bounds=(1e-3, 1e2))
        self.regressor = GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=10, random_state = cfg.seed)
        self.fitted = False

        self.kernel_val = None # TODO: extract kernel values.

    def split(self, holdout):

        nruns = np.shape(self.train_xs)[0]

        kktest = np.array([ (k in holdout) for k in range(nruns) ])
        kktrain = np.logical_not(kktest)

        return kktrain, kktest

    def fit_gpr(self, holdout_idxs=[], mode='all'):

        if mode not in ['all', 'train_only']:
            raise ValueError("mode must be all or train_only")

        input_normed = np.ones_like(self.train_xs)
        # Normalize X-data
        for i in range(self.nfeats):
            input_normed[:,i] = (self.train_xs[:,i] - self.xmins[i]) / (self.xmaxs[i] - self.xmins[i])

        output_normed = self.train_ys.copy()
        # Normalize Y-data
        output_normed -= self.ymins
        output_normed /= (self.ymaxs - self.ymins)

        # Split
        kkt, kkd = self.split(holdout_idxs)

        x_train = input_normed if mode=='all' else input_normed[kkt]
        y_train = output_normed if mode=='all' else output_normed[kkt]
        x_test = input_normed[kkd]
        y_test = output_normed[kkd]

        self.regressor.fit(x_train, y_train)
        self.kernel_val = self.regressor.kernel_
        self.fitted = True

    def predict_gpr(self, input_predict):
        '''Takes unnormalized (N,nfeats), returns unnormalized (N,)'''

        assert self.fitted, "Must fit regressor before predicting."

        input_predict = input_predict.copy()

        for i in range(self.nfeats):
            input_predict[:,i] = (input_predict[:,i] - self.xmins[i]) / (self.xmaxs[i] - self.xmins[i])
        gp_output_mean, gp_output_std = self.regressor.predict(input_predict, return_std=True)
        output_mean = gp_output_mean * (self.ymaxs - self.ymins) + self.ymins
        output_std = gp_output_std * (self.ymaxs - self.ymins)

        return output_mean, output_std

    # TODO: automatic leave-one-out for each holdout idx

### ### ###

def interpolate_via_gpr(cfg,
                        input_interp, input_train, output_train,
                        holdout_idxs=[]):

    gp = FittedRegressor(cfg, input_train, output_train)
    if holdout_idxs:
        gp.fit_gpr(mode='train_only', holdout_idxs=holdout_idxs)
    else:
        gp.fit_gpr(mode='all')

    # TODO: obtain all kernel lengths, since we're combining two different kernels
    kernel_length = gp.kernel_val
    y_means, y_sigmas = gp.predict_gpr(input_interp)

    return y_means, y_sigmas, kernel_length

### ### ###

def produce_projection(cfg, output_tag, discrete_id, n_samples):



    # Perform Fit and Sample

    input_train_global, output_train = get_input_output_space(cfg, output_tag, discrete_id)

    def _sample_input_space(cfg, nsamples): # this is for producing a projection
        '''
        For producing the projection, not to be confused with the simulation input params.
        '''

        mins = [ feat['min'] for feat in cfg.inputs.continuous_features ]
        maxs = [ feat['max'] for feat in cfg.inputs.continuous_features ]

        n_cts_feats = len(mins)

        lhs_sampler = LatinHypercube(d=n_cts_feats, seed = cfg.seed)
        sampled_values = lhs_sampler.random(nsamples)

        for i in range(n_cts_feats):
            sampled_values[:,i] *= (maxs[i] - mins[i])
            sampled_values[:,i] += mins[i]

        return sampled_values

    sampled_inputs = _sample_input_space(cfg, n_samples)
    pred, err, kernel_value = interpolate_via_gpr(cfg, sampled_inputs, input_train_global, output_train)



    # Get 1D and 2D Projections

    mins = [ feat['min'] for feat in cfg.inputs.continuous_features ]
    maxs = [ feat['max'] for feat in cfg.inputs.continuous_features ]

    n_cts_fts = len(mins)

    gridlocs_1d = {}
    means_1d = {}
    stds_1d = {}
    for dim1 in range(n_cts_fts):
        grid_means, centers = project_and_marginalize(
            sampled_inputs, pred, [dim1], mins, maxs, stat='mean'
        )
        grid_stds, _ = project_and_marginalize(
            sampled_inputs, pred, [dim1], mins, maxs, stat='std'
        ) # this is the spread across marginalized dimensions, not the GPR's own uncertainty.
        key = str(dim1)
        gridlocs_1d[key] = { "x": centers[0] }
        means_1d[key] = grid_means
        stds_1d[key] = grid_stds

    data_1d = { 'gridlocs':gridlocs_1d, 'means':means_1d, 'stds':stds_1d }

    gridlocs_2d = {}
    means_2d = {}
    stds_2d = {}
    for dim1 in range(n_cts_fts):
        for dim2 in range(dim1+1, n_cts_fts):
            grid_means, centers = project_and_marginalize(
                sampled_inputs, pred, [dim1, dim2], mins, maxs, stat='mean'
            )
            grid_stds, _ = project_and_marginalize(
                sampled_inputs, pred, [dim1, dim2], mins, maxs, stat='std'
            )

            key = f"{dim1},{dim2}"
            gridlocs_2d[key] = { "x": centers[0], "y": centers[1] }
            means_2d[key] = grid_means
            stds_2d[key] = grid_stds

    data_2d = { 'gridlocs':gridlocs_2d, 'means':means_2d, 'stds':stds_2d }

    data = { 'trained':output_train, '1D':data_1d, '2D':data_2d } #, 'kernel_length':kernel_length }

    return data