import igraph
import numpy as np
import pandas as pd
from os.path import join
from scipy.special import binom
import logging
from timeit import default_timer as timer

from ninolearn.IO.read_processed import data_reader
from ninolearn.pathes import processeddir
from ninolearn.utils import largest_indices, generateFileName


logging.basicConfig(format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)


class climateNetwork(igraph.Graph):
    """
    Child object of the igraph.Graph class for the construction of a complex
    climate network.
    """
    @classmethod
    def from_adjacency(cls, adjacency):
        """
        Generate an igraph network form a adjacency matrix.

        :type adjacency: np.ndarray
        :param adjacency: The NxN adjacency array.
        """
        np.fill_diagonal(adjacency, 0)
        cls.adjacency_array = adjacency
        cls.N = adjacency.shape[0]

        A = (adjacency > 0).tolist()

        # mode = 1 means undirected
        return cls.Adjacency(A, mode=1)

    @classmethod
    def from_correalation_matrix(cls, correalation_matrix,
                                 threshold=None, edge_density=None):
        """
        generate an igraph network from a correlation matrix

        :param correalation_matrix: The NxN correlation matrix that should be\
        used to generate the network.

        :param threshold:  If NOT none but float between 0 and 1, a network\
        with a fixed global threshold is generated.\n
        NOTE: EITHER the threshold OR the edge density method can be used!

        :param edge_density: If NOT none but float between 0 and 1, a network\
        with a fixed edge density where the strongest links are part of network\
        is generated. Note, EITHER the threshold OR the edge density method can\
        be used!
        """

        adjacency = np.zeros_like(correalation_matrix)

        cls.N = correalation_matrix.shape[0]

        np.fill_diagonal(correalation_matrix, 0)

        if ((threshold is None and edge_density is None)
           or (threshold is not None and edge_density is not None)):
            raise Exception("Either use the fixed threshold method \
                            OR the fixed edge_density method!")

        if threshold is not None:
            #adjacency[correalation_matrix > threshold] = 1.
            adjacency[np.abs(correalation_matrix) > threshold] = 1.
            cls.threshold = threshold

        elif edge_density is not None:
            # get index for links
            n_possible_links = binom(cls.N, 2)
            nlinks = int(edge_density * n_possible_links)

            il = largest_indices(correalation_matrix, 2 * nlinks)
            adjacency[il] = 1
            cls.threshold = np.nanmin(correalation_matrix[il])

        return cls.from_adjacency(adjacency)

    def giant_fraction(self):
        """
        Returns the fraction of the nodes that are part of the giant component.
        """
        nodes_total = self.vcount()
        nodes_giant = self.clusters().giant().vcount()
        return nodes_giant/nodes_total

    def cluster_fraction(self, size=2):
        """
        Returns the fraction of the nodes that are part of a cluster of the
        given size (default: size=2).

        :type size: int
        :param size: Size of the cluster. Default:2.
        """
        nodes_total = self.vcount()
        nodes_cluster = self.clusters().sizes().count(size)
        return nodes_cluster/nodes_total

    def hamming_distance(self, other_adjacency):
        """
        Compute the Hamming distance of the climate Network to the provided
        other Network (by supplying the adjacency of the other Network).

        :param other_adjacency: The adjacency of the other climate Network.
        """
        try:
            N = self.vcount()

            # indeces for upper triangular matrix excluding the diagonal
            ui = np.triu_indices(N, 1)

            # Hamming distance
            H = np.sum(np.abs(self.adjacency_array[ui]
                              - other_adjacency[ui])) / binom(N, 2)
            return H

        except IndexError:
            logger.warning("Wrong input for computation of hamming distance.")
            return 0

    def corrected_hamming_distance(self, other_adjacency):
        """
        Compute the Hamming distance of the climate Network to the provided
        other Network (by supplying the adjacency of the other Network).
        Computation is done as described in Radebach et al. (2013).

        :param other_adjacency: The adjacency of the other climate Network.
        """
        try:
            N = self.vcount()

            # indeces for upper triangular matrix excluding the diagonal
            ui = np.triu_indices(N, 1)

            # count types of link changes
            b = np.sum((self.adjacency_array[ui] == 1) &
                       (other_adjacency[ui] == 0))

            c = np.sum((self.adjacency_array[ui] == 0) &
                       (other_adjacency[ui] == 1))

            d = np.sum((self.adjacency_array[ui] == 1) &
                       (other_adjacency[ui] == 1))

            # edge densities
            rho = (b + d) / binom(N, 2)
            rho_dash = (c + d) / binom(N, 2)

            # corrected Hamming distance
            if rho >= rho_dash:
                Hstar = 2 * c / binom(N, 2)
            else:
                Hstar = 2 * b / binom(N, 2)
            return Hstar

        except IndexError:
            msg = "Wrong input for computation of corrected hamming distance."
            logger.warning(msg)
            return 0


class networkMetricsSeries(object):
    """
    Class for the computation of network metrics time series

    :type variable: str
    :param variable: The variable for which the network time series should\
    be computed.\

    :type dataset: str
    :param dataset: The dataset that should be used to build the network.\

    :type processed: str
    :param processed: Either '','anom' or 'normanom'.\

    :type threshold: float
    :param threshold: the threshold for a the correlation coeficent between\
    two grid point to be considered as connected.

    :param startyear: The first year for which the network analysis should\
    be done.

    :param endyear: The last year for which the network analysis should be\
    done.

    :param window_size: The size of the window for which the network\
    metrics are computed.

    :param lon_min,lon_max: The minimum and the maximum values of the\
    longitude grid for which the metrics shell be computed \
    (from 0 to 360 degrees east).

    :param lat_min,lat_max: The minimum and the maximum values of the\
    latitude grid for which the metrics shell be computed\
    (from -180 to 180 degrees east).
    """
    def __init__(self, variable, dataset, processed='anom',
                 threshold=None, edge_density=None,
                 startyear=1948, endyear=2018, window_size=12,
                 lon_min=120, lon_max=260, lat_min=-30, lat_max=30,
                 verbose=0):

        self.variable = variable
        self.dataset = dataset
        self.processed = processed

        self.threshold = threshold
        self.edge_density = edge_density

        self.startyear = str(startyear)
        self.endyear = str(endyear)

        self.startdate = pd.to_datetime(self.startyear)
        self.enddate = pd.to_datetime(self.endyear) \
            + pd.tseries.offsets.YearEnd(0)

        self.window_size = window_size
        self.window_start = self.startdate
        self.window_end = self.window_start \
            + pd.tseries.offsets.MonthEnd(self.window_size)

        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max

        self.reader = data_reader(startdate=self.window_start,
                                  enddate=self.window_end,
                                  lon_min=self.lon_min, lon_max=self.lon_max,
                                  lat_min=self.lat_min, lat_max=self.lat_max)
        self.initalizeSeries()

        if verbose == 0:
            logger.setLevel(logging.DEBUG)
        elif verbose == 1:
            logger.setLevel(logging.INFO)
        elif verbose == 2:
            logger.setLevel(logging.WARNING)
        elif verbose == 3:
            logger.setLevel(logging.ERROR)

    def __del__(self):
        logging.shutdown()

    def initalizeSeries(self):
        """
        initializes the pandas Series and array that saves the adjacency of the
        network from the previous time step.
        """
        self.threshold_value = pd.Series()
        self.global_transitivity = pd.Series()
        self.avglocal_transitivity = pd.Series()
        self.frac_cluster_size2 = pd.Series()
        self.frac_cluster_size3 = pd.Series()
        self.frac_cluster_size5 = pd.Series()
        self.frac_giant = pd.Series()
        self.avg_path_length = pd.Series()
        self.edge_density_value = pd.Series()
        self.hamming_distance = pd.Series()
        self.corrected_hamming_distance = pd.Series()

        self._old_adjacency = np.array([])

    def computeCorrelationMatrix(self):
        start = timer()
        logger.debug("Start computeCorrelationMatrix()")

        logger.debug("- Read netcdf data")
        data = self.reader.read_netcdf(variable=self.variable,
                                       dataset=self.dataset,
                                       processed=self.processed,
                                       chunks={'time': 1})

        # Reshape
        logger.debug("- Reshape data")
        data3Darr = np.array(data)

        dims = data.coords.dims
        time_index = dims.index('time')
        lat_index = dims.index('latitude')
        lon_index = dims.index('longitude')

        len_time = data3Darr.shape[time_index]
        len_lat = data3Darr.shape[lat_index]
        len_lon = data3Darr.shape[lon_index]

        data2Darr = data3Darr.reshape(len_time, len_lat * len_lon)

        # Correlation matrix
        logger.debug("- Compute Correlation matrix")

        # just consider grid points that are finite
        data2Darr = data2Darr[:, np.isfinite(data2Darr).any(axis=0)]

        corrcoef = np.corrcoef(data2Darr.T)

        # correlations with std = 0 will have a corrcoef of nan. Therefore,
        # set NANs to 0
        corrcoef[np.isnan(corrcoef)] = 0

        end = timer()
        elapsed = round(end - start, 1)
        logger.debug(f"End computeCorrelationMatrix(): {elapsed} s")
        return corrcoef

    def computeNetworkMetrics(self, corrcoef):
        """
        computes network metrics from a correlation matrix in combination with
        the already given threshold

        :param corrcoef: The correlation matrix.
        """
        logger.debug("Start computeNetworkMetrics()")

        self.cn = climateNetwork.from_correalation_matrix(
                corrcoef, threshold=self.threshold,
                edge_density=self.edge_density)

        # save date is the first day of the last month from the time window
        save_date = self.reader.enddate - pd.tseries.offsets.MonthBegin(1)

        logger.debug(f'Save date: {save_date}')

        # The threshold of the climate network
        self.threshold_value[save_date] = self.cn.threshold

        # C1 as in Newman (2003) and Eq. (6) in Radebach et al. (2013)
        self.global_transitivity[save_date] = self.cn.transitivity_undirected()

        # C2 as in Newman (2003) and Eq. (7) in Radebach et al. (2013)
        self.avglocal_transitivity[save_date] = \
            self.cn.transitivity_avglocal_undirected(mode="zero")

        # fraction of nodes in clusters of size 2
        self.frac_cluster_size2[save_date] = self.cn.cluster_fraction(2)

        if self.frac_cluster_size2[save_date] == 0:
            logger.warning("c2 variable equal to 0!")

        # fraction of nodes in clusters of size 3
        self.frac_cluster_size3[save_date] = self.cn.cluster_fraction(3)

        # fraction of nodes in clusters of size 3
        self.frac_cluster_size5[save_date] = self.cn.cluster_fraction(5)

        # fraciont of nodes in giant component
        self.frac_giant[save_date] = self.cn.giant_fraction()

        # average path length
        self.avg_path_length[save_date] = self.cn.average_path_length()

        # edge density
        self.edge_density_value[save_date] = self.cn.density()

        # hamming distance
        self.hamming_distance[save_date] = \
            self.cn.hamming_distance(self._old_adjacency)

        # corrected hamming distance
        self.corrected_hamming_distance[save_date] = \
            self.cn.corrected_hamming_distance(self._old_adjacency)

        # copy the old adjacency
        self._old_adjacency = self.cn.adjacency_array.copy()
        logger.debug("End computeNetworkMetrics()")

    def save(self):
        self.data = pd.DataFrame(
              {'global_transitivity': self.global_transitivity,
               'avelocal_transmissivity': self.avglocal_transitivity,
               'fraction_clusters_size_2': self.frac_cluster_size2,
               'fraction_clusters_size_3': self.frac_cluster_size3,
               'fraction_clusters_size_5': self.frac_cluster_size5,
               'fraction_giant_component': self.frac_giant,
               'average_path_length': self.avg_path_length,
               'hamming_distance': self.hamming_distance,
               'corrected_hamming_distance': self.corrected_hamming_distance,
               'threshold': self.threshold_value,
               'edge_density': self.edge_density_value
               })

        filename = generateFileName(self.variable,
                                    self.dataset,
                                    processed=self.processed,
                                    suffix='csv')

        filename = '-'.join(['network_metrics', filename])

        if self.threshold is not None:
            # TODO: dynamic naming depending on the methods used
            pass
        elif self.edge_density is not None:
            pass
        self.data.to_csv(join(processeddir, filename))

    def computeTimeSeries(self):
        """
        Compute the evolving complex network timeseries, the corresping
        metrics and save the results to a csv-file in the data directory

        NOTE: Specify the data directory as 'datadir' in the ninolear.private
        module which you may not push the public repository.
        """
        while self.reader.enddate <= self.enddate:
            logger.info(f'{self.reader.startdate} till {self.reader.enddate}')
            corrcoef = self.computeCorrelationMatrix()
            self.computeNetworkMetrics(corrcoef)
            self.reader.shift_window(month=1)
        self.save()
