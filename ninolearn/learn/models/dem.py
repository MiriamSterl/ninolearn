import numpy as np

import tensorflow.keras.backend as K
from tensorflow.keras.activations import elu
from tensorflow.keras.models import Model, save_model, load_model
from tensorflow.keras.layers import Dense, Input, concatenate
from tensorflow.keras.layers import Dropout, GaussianNoise
from tensorflow.keras.optimizers import Adam, RMSprop
from tensorflow.keras.callbacks import EarlyStopping
from tensorflow.keras import regularizers

from os.path import join, exists
from os import mkdir, listdir, getcwd
from shutil import rmtree
import glob

from ninolearn.learn.models.baseModel import baseModel
from ninolearn.learn.losses import nll_gaussian, nll_skewed_gaussian
from ninolearn.learn.skillMeasures import rmse
from ninolearn.utils import small_print_header
from ninolearn.exceptions import MissingArgumentError

import warnings

import time

class DEM(baseModel):
    """
    A deep ensemble model (DEM) predicting  either mean or mean and standard
    deviation with one hidden layer having the ReLU function as activation for
    the hidden layer. It is trained using the MSE or negative-log-likelihood of
    a gaussian distribution, respectively.

    :type layers: int
    :param layers: Number of hidden layers.

    :type neurons: int
    :param neurons: Number of neurons in a hidden layers.

    :type dropout: float
    :param dropout: Dropout rate for the hidden layer neurons.

    :type noise: float
    :param noise: Standard deviation of the gaussian noise that is added to\
    the input

    :type l1_hidden: float
    :param l1_hidden: Coefficent for the L1 penalty term for the hidden layer.

    :type l2_hidden: float
    :param l2_hidden: Coefficent for the L2 penalty term for the hidden layer.

    :type l1_mu: float
    :param l1_mu: Coefficent for the L1 penalty term in the mean-output neuron.

    :type l2_mu: float
    :param l2_mu: Coefficent for the L2 penalty term in the mean-output neuron.

    :type l1_sigma: float
    :param l1_sigma: Coefficent for the L1 penalty term in the\
    standard-deviation-output neuron.

    :type l2_mu: float
    :param l2_mu: Coefficent for the L2 penalty term in the standard-deviation \
    output neuron.

    :param batch_size: Batch size for the training.

    :param n_segments: Number of segments for the generation of members.

    :param n_members_segment: number of members that are generated per\
    segment.

    :param lr: the learning rate during training

    :param patience: Number of epochs to wait until training is stopped if\
    score was not improved.

    :param epochs: The maximum numberof epochs for the training.

    :param verbose: Option to print scores during training to the screen. \
    Here, 0 means silent.

    :type pdf: str
    :param pdf: The distribution which shell be predicted. Either 'simple'\
    (just one value), 'normal' (Gaussian) or 'skewed' (skewed Gaussian).

    :type name: str
    :param name: The name of the model.
    """
    def __del__(self):
        K.clear_session()

    def __init__(self, layers=1, neurons=16, dropout=0.2, noise_in=0.0,
                       noise_mu=0.0, noise_sigma=0.0, noise_alpha=0.0,
                       l1_hidden=0.0, l2_hidden=0.0,
                       l1_mu=0.0, l2_mu=0.0,
                       l1_sigma=0.0, l2_sigma=0.0,
                       l1_alpha=0.0, l2_alpha=0.0,
                       batch_size=10, n_segments=5, n_members_segment=1,
                       lr=0.001, patience = 10, epochs=100, verbose=0, pdf='normal',
                       activation='relu',
                       name='dem'):

        self.set_hyperparameters(layers=layers, neurons=neurons, dropout=dropout,
                                 noise_in=noise_in, noise_mu=noise_mu,
                                 noise_sigma=noise_sigma, noise_alpha=noise_alpha,
                                 l1_hidden=l1_hidden, l2_hidden=l2_hidden, l1_mu=l1_mu, l2_mu=l2_mu,
                                 l1_sigma=l1_sigma, l2_sigma=l2_sigma,
                                 l1_alpha=l1_alpha, l2_alpha=l2_alpha,
                                 batch_size=batch_size, n_segments=n_segments, n_members_segment=n_members_segment,
                                 lr=lr, patience=patience, epochs=epochs, verbose=verbose, pdf=pdf,
                                 activation=activation,
                                 name=name)
        self.get_model_desc(self.hyperparameters['pdf'])

    def get_model_desc(self, pdf):
        """
        Assignes sum weights description to the model depending on which
        predicted distribution is selected.
        """
        if pdf=="normal":
            self.loss = nll_gaussian
            self.loss_name = 'nll_gaussian'
            self.n_outputs = 2
            self.output_names =  ['mean', 'std']

        elif pdf=="skewed":
            self.loss = nll_skewed_gaussian
            self.loss_name = 'nll_skewed_gaussian'
            self.n_outputs = 3
            self.output_names =  ['location', 'scale', 'shape']

        elif pdf is None:
            self.loss = 'mse'
            self.loss_name = 'mean_squared_error'
            self.n_outputs = 1
            self.output_names =  ['mean']

    def build_model(self, n_features):
        """
        The method builds a new member of the ensemble and returns it.
        """
        # derived parameters
        self.hyperparameters['n_members'] = self.hyperparameters['n_segments'] * self.hyperparameters['n_members_segment']

        # initialize optimizer and early stopping
        self.optimizer =  Adam(lr=self.hyperparameters['lr'], beta_1=0.9, beta_2=0.999, epsilon=None, decay=0., amsgrad=False)


        self.es = EarlyStopping(monitor=f'val_{self.loss_name}', min_delta=0.0, patience=self.hyperparameters['patience'], verbose=1,
                   mode='min', restore_best_weights=True)

        inputs = Input(shape=(n_features,))
        h = GaussianNoise(self.hyperparameters['noise_in'],
                          name='noise_input')(inputs)

        for i in range(self.hyperparameters['layers']):
            h = Dense(self.hyperparameters['neurons'], activation=self.hyperparameters['activation'],
                      kernel_regularizer=regularizers.l1_l2(self.hyperparameters['l1_hidden'],
                                                            self.hyperparameters['l2_hidden']),
                      kernel_initializer='random_uniform',
                      bias_initializer='zeros',
                      name=f'hidden_{i}')(h)

            h = Dropout(self.hyperparameters['dropout'],
                        name=f'hidden_dropout_{i}')(h)

        mu = Dense(1, activation='linear',
                   kernel_regularizer=regularizers.l1_l2(self.hyperparameters['l1_mu'],
                                                         self.hyperparameters['l2_mu']),
                   kernel_initializer='random_uniform',
                   bias_initializer='zeros',
                   name='mu_output')(h)

        mu = GaussianNoise(self.hyperparameters['noise_mu'],
                           name='noise_mu')(mu)


        if self.hyperparameters['pdf']=='normal' or self.hyperparameters['pdf']=='skewed':
            sigma = Dense(1, activation='softplus',
                          kernel_regularizer=regularizers.l1_l2(self.hyperparameters['l1_sigma'],
                                                                self.hyperparameters['l2_sigma']),
                          kernel_initializer='random_uniform',
                          bias_initializer='zeros',
                          name='sigma_output')(h)

            sigma = GaussianNoise(self.hyperparameters['noise_sigma'],
                                  name='noise_sigma')(sigma)

        if self.hyperparameters['pdf']=='skewed':
            alpha = Dense(1, activation='linear',
                       kernel_regularizer=regularizers.l1_l2(self.hyperparameters['l1_alpha'],
                                                             self.hyperparameters['l2_alpha']),
                       kernel_initializer='random_uniform',
                       bias_initializer='zeros',
                       name='alpha_output')(h)

            alpha = GaussianNoise(self.hyperparameters['noise_alpha'],
                           name='noise_alpha')(alpha)

        if self.hyperparameters['pdf'] is None:
            outputs = mu
        elif self.hyperparameters['pdf']=='normal':
            outputs = concatenate([mu, sigma])
        elif self.hyperparameters['pdf']=='skewed':
            outputs = concatenate([mu, sigma, alpha])

        model = Model(inputs=inputs, outputs=outputs)
        return model


    def fit(self, trainX, trainy, timey, valX=None, valy=None, use_pretrained=False):
        """
        Fit the model to training data
        """

        start_time = time.time()
        # clear memory
        K.clear_session()

        # allocate lists for the ensemble
        self.ensemble = []
        self.history = []
        self.val_loss = []

        self.segment_len = trainX.shape[0]//self.hyperparameters['n_segments']

        if self.hyperparameters['n_segments']==1 and (valX is not None or valy is not None):
             warnings.warn("Validation and test data set are the same if n_segements is 1!")

        i = 0
        while i<self.hyperparameters['n_members_segment']:
            j = 0
            while j<self.hyperparameters['n_segments']:
                print("build")
                ensemble_member = self.build_model(trainX.shape[1])

                n_ens_sel = len(self.ensemble)
                small_print_header(f"Train member Nr {n_ens_sel+1}/{self.hyperparameters['n_members']}")

                if use_pretrained:
                    ensemble_member.load_weights(self.pretrained_weights)

                print("compile")
                ensemble_member.compile(loss=self.loss, optimizer=self.optimizer, metrics=[self.loss])

                # validate on the spare segment
                if self.hyperparameters['n_segments']!=1:
                    if valX is not None or valy is not None:
                        warnings.warn("Validation data set will be one of the segments. The provided validation data set is not used!")

                    start_ind = j * self.segment_len
                    end_ind = (j+1) *  self.segment_len

                    trainXens = np.delete(trainX, np.s_[start_ind:end_ind], axis=0)
                    trainyens = np.delete(trainy, np.s_[start_ind:end_ind])

                    # upsample el nino like periods
                    if False:
                        timeyens = np.delete(timey, np.s_[start_ind:end_ind])

                        elninolike = (timeyens>=f'1982-01-01') & (timeyens<=f'2001-12-01')
                        laninalike = np.invert(elninolike)


                        trainXens_nino, trainyens_nino = trainXens[elninolike], trainyens[elninolike]
                        trainXens_nina, trainyens_nina = trainXens[laninalike], trainyens[laninalike]

                        nino_choices = np.random.choice(np.arange(len(trainyens_nino)), size=1000)
                        nina_choices = np.random.choice(np.arange(len(trainyens_nina)), size=1000)


                        trainXens = np.concatenate((trainXens_nino[nino_choices],
                                                    trainXens_nina[nina_choices]))

                        trainyens = np.concatenate((trainyens_nino[nino_choices],
                                                    trainyens_nina[nina_choices]))


                    valXens = trainX[start_ind:end_ind]
                    valyens = trainy[start_ind:end_ind]

                    if False:
                        valXens, trainXens = trainXens, valXens
                        valyens, trainyens = trainyens, valyens

                # validate on test data set
                elif self.hyperparameters['n_segments']==1:
                    if valX is None or valy is None:
                        raise MissingArgumentError("When segments length is 1, a validation data set must be provided.")
                    trainXens = trainX
                    trainyens = trainy
                    valXens = valX
                    valyens = valy

                history = ensemble_member.fit(trainXens, trainyens,
                                            epochs=self.hyperparameters['epochs'], batch_size=self.hyperparameters['batch_size'],
                                            verbose=self.hyperparameters['verbose'],
                                            shuffle=True, callbacks=[self.es],
                                            validation_data=(valXens, valyens))

                self.history.append(history)
                self.val_loss.append(ensemble_member.evaluate(valXens, valyens)[1])
                self.ensemble.append(ensemble_member)
                j+=1
            i+=1
        self.mean_val_loss = np.mean(self.val_loss)

        print(f'Loss: {self.mean_val_loss}')
        # print computation time
        end_time = time.time()
        passed_time = np.round(end_time-start_time, decimals=1)
        print(f'Computation time: {passed_time}s')
#

    def predict(self, X):
        """
        Generates the ensemble prediction of a model ensemble

        :param model_ens: list of ensemble models
        :param X: The features

        """
        if self.hyperparameters['pdf']=='normal':
            pred_ens = np.zeros((X.shape[0], 2, self.hyperparameters['n_members']))

        elif self.hyperparameters['pdf']=='skewed':
            pred_ens = np.zeros((X.shape[0], 3, self.hyperparameters['n_members']))

        elif self.hyperparameters['pdf'] is None:
            pred_ens = np.zeros((X.shape[0], 1, self.hyperparameters['n_members']))

        for i in range(self.hyperparameters['n_members']):
            pred_ens[:,:,i] = self.ensemble[i].predict(X)
        return self._mixture(pred_ens)


    def _mixture(self, pred):
        """
        returns the ensemble mixture results
        """
        mix_mean = pred[:,0,:].mean(axis=1)

        if self.hyperparameters['pdf']=='normal':
            mix_var = np.mean(pred[:,0,:]**2 + pred[:,1,:]**2, axis=1)  - mix_mean**2
            mix_std = np.sqrt(mix_var)
            return [mix_mean, mix_std]

        elif self.hyperparameters['pdf']=='skewed':
            mix_var = np.mean(pred[:,0,:]**2 + pred[:,1,:]**2, axis=1)  - mix_mean**2
            mix_std = np.sqrt(mix_var)
            print("Mixture prediction for skewed distribution is not ready!")
            return mix_mean, mix_std, None

        elif self.hyperparameters['pdf'] is None:
            return mix_mean


    def evaluate(self, ytrue, mean_pred, std_pred=False):
        """
        Negative - log -likelihood for the prediction of a gaussian probability
        """
        if std_pred is None:
            return rmse(ytrue, mean_pred)

        else:
            mean = mean_pred
            sigma = std_pred + 1e-6 # adding 1-e6 for numerical stability reasons

            first  =  0.5 * np.log(np.square(sigma))
            second =  np.square(mean - ytrue) / (2  * np.square(sigma))
            summed = first + second

            loss =  np.mean(summed, axis=-1)
            return loss


    def save(self, location='', dir_name='ensemble'):
        """
        Save the ensemble
        """
        path = join(location, dir_name)
        if not exists(path):
            mkdir(path)
        else:
            rmtree(path)
            mkdir(path)

        self.df_history_hyp.to_csv(join(path, 'hyperparameters_history.csv'))

        for i in range(self.hyperparameters['n_members']):
            path_h5 = join(path, f"member{i}.h5")
            save_model(self.ensemble[i], path_h5, include_optimizer=False)


    def load(self, location=None,  dir_name='dem'):
        """
        Load the ensemble
        """
        if location is None:
            location = getcwd()

        path = join(location, dir_name, '*.h5')
        files = glob.glob(path)
        self.hyperparameters = {}
        self.hyperparameters['n_members'] = len(files)
        self.ensemble = []

        for file in files:
            file_path = join(path, file)
            self.ensemble.append(load_model(file_path, compile=False))

        output_neurons = self.ensemble[0].get_output_shape_at(0)[1]

        if output_neurons==2:
            self.hyperparameters['pdf'] = 'normal'

        elif output_neurons==3:
            self.hyperparameters['pdf'] = 'skewed'
        else:
            self.hyperparameters['pdf'] = None

        self.get_model_desc(self.hyperparameters['pdf'])


