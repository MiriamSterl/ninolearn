import numpy as np
from collections import defaultdict
import pandas as pd

class baseModel(object):
    """
    The class from which each new model should inherit. Because of the
    inheritance, standardized training and testing will be possible.

    Errors will be raised if mandotory functions are not overwritten
    by the child model. Mandetory functions are:

        1. fit
        2. predict
        3. save
        4. load
    """
    def __init__(self):
        raise NameError("Function '__init__' is not defined")

    def set_hyperparameters(self, **kwargs):
        """
        Set the hyperparameters for the model that are provided as keyword
        arguments.

        :param kwargs: The hyperparameters that are used in the child model.
        """

        # hyperparameters
        self.hyperparameters = kwargs

        # hyperparameters for randomized search
        self.hyperparameters_search = {}

        for key in self.hyperparameters.keys():
            if type(self.hyperparameters[key]) is list:
                if len(self.hyperparameters[key])>0:
                    self.hyperparameters_search[key] = self.hyperparameters[key].copy()


    def fit_RandomizedSearch(self, trainX, trainy, timey, n_iter=10, **kwargs):
        """
        This method performs a random search in the hyperparamter space.

        :param trainX: The feature set.

        :param trainy: The label set.

        :param n_iter: The number of iterations for the random search.

        :param kwargs: Keyword arguments that are passed to the fit method.
        """

        self.history_hyp = defaultdict(list)

        # check if hyperparameters where provided in lists for randomized search
        if len(self.hyperparameters_search) == 0:
            print("WARNING: No variable indicated for hyperparameter search!")

        #iterate with randomized hyperparameters
        best_loss = np.inf
        for i in range(n_iter):
            print(f"Search iteration Nr {i+1}/{n_iter}")

            # random selection of hyperparameters
            for key in self.hyperparameters_search.keys():
                search_type = self.hyperparameters_search[key][2]
                if search_type=='linear':
                    low = self.hyperparameters_search[key][0]
                    high = self.hyperparameters_search[key][1]

                    if type(low) is float or type(high) is float:
                        self.hyperparameters[key] = np.random.uniform(low, high)

                    elif type(low) is int and type(high) is int:
                        self.hyperparameters[key] = np.random.randint(low, high+1)

                    elif type(low) is tuple and type(high) is tuple:
                        hyp_list = []
                        for i in range(len(low)):
                            hyp_list.append(np.random.randint(low[i], high[i]+1))
                        self.hyperparameters[key] = tuple(hyp_list)

                elif search_type=='log':
                    low = self.hyperparameters_search[key][0]
                    high = self.hyperparameters_search[key][1]

                    choice_values = np.logspace(np.log10(low), np.log10(high), 100)
                    self.hyperparameters[key] = np.random.choice(choice_values)

                elif search_type=='exp':
                     base = self.hyperparameters_search[key][0]
                     low_exp = self.hyperparameters_search[key][1][0]
                     high_exp = self.hyperparameters_search[key][1][1]

                     exponents = np.arange(low_exp, high_exp+1)
                     choice_values = base**exponents

                     self.hyperparameters[key] = np.random.choice(choice_values)


            self.fit(trainX, trainy, timey, **kwargs)
            self.history_hyp['loss'].append(self.mean_val_loss)
            for key in self.hyperparameters_search.keys():
                self.history_hyp[key].append(self.hyperparameters[key])

            self.df_history_hyp = pd.DataFrame(dict(self.history_hyp))
            #self.df_history_hyp.to_csv('hyperparameter_history.csv')

            # check if validation score was enhanced
            if self.mean_val_loss<best_loss:
                best_loss = self.mean_val_loss
                self.best_hyperparameters = self.hyperparameters.copy()

                print("New best hyperparameters")
                print(f"Mean loss: {best_loss}")
                print(self.best_hyperparameters)

        # refit the model with optimized hyperparameter
        # AND to have the weights of the DE for the best hyperparameters again
        if n_iter!=1:
            print("Refit the model with best hyperparamters")

            self.hyperparameters = self.best_hyperparameters.copy()
            print(self.hyperparameters)
            self.fit(trainX, trainy, timey, **kwargs)

            print(f"best loss search: {best_loss}")
            print(f"loss refitting : {self.mean_val_loss}")


    def fit(self):
        raise NameError("Function 'fit' is not defined!")


    def predict(self):
        raise NameError("Function 'fit' is not defined!")


    def save(self):
        raise NameError("Function 'save' is not defined!")


    def load(self):
        raise NameError("Function 'load' is not defined!")

