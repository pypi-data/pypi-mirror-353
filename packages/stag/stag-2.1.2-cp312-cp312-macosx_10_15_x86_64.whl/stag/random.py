"""
Construct graphs from random models.
"""
import numpy as np
from typing import Union
from . import stag_internal
from . import graph
from . import utility


def sbm(n: int, k: int, p: float, q: float, exact: bool = False) -> graph.Graph:
    r"""
    Generate a graph from the symmetric stochastic block model.

    Every cluster has the same number of vertices. For large enough values of
    \f$n\f$, this method samples from an approximate stochastic block model by
    default which significantly speeds up the execution time.
    To sample exactly from the stochastic block model, pass the optional 'exact'
    parameter to the method.

    The approximate sampling method has running time \f$O(k^2 + \mathrm{nnz})\f$
    and the exact method has running time \f$O(n^2)\f$ where \f$\mathrm{nnz}\f$
    is the number of non-zeros in the generated graph's adjacency matrix.

    @param n the number of vertices in the graph.
    @param k the number of clusters. Vertices are split evenly between clusters
    @param p the probability of including an edge inside a cluster.
    @param q the probability of including an edge between two clusters.
    @param exact (optional) whether to use the exact probability distribution
                  or an approximation.
    @return the randomly generated stag.graph.Graph
    """
    return graph.Graph(stag_internal.sbm(n, k, p, q, exact))


@utility.convert_ndarrays
def general_sbm(cluster_sizes: np.ndarray,
                probabilities: np.ndarray,
                exact: bool = False) -> graph.Graph:
    r"""
    Generate a graph from the general stochastic block model.

    The `cluster_sizes` list specifies the number of vertices in each
    generated cluster.
    Let \f$k\f$ be the length of the cluster_sizes list.

    Then, `probabilities` should be a \f$k \times k\f$ matrix which specifies
    the edge probability between every pair of vertices.
    That is, for each pair of vertices \f$u\f$ and \f$v\f$, the probability of
    including the edge \f$\{u, v\}\f$ in the graph is \f$P(u, v)\f$, where
    \f$P\f$ is the `probabilities` matrix.

    The approximate sampling method has running time \f$O(k^2 + \mathrm{nnz})\f$
    where \f$\mathrm{nnz}\f$ is the number of non-zeros in the generated
    graph's adjacency matrix,
    and the exact
    method has running time \f$O(n^2)\f$.

    \par Example

    \code{python}
    import numpy as np
    import stag.graph
    import stag.random

    cluster_sizes = np.asarray([100, 20, 10])
    prob_mat = np.asarray([[0.4, 0.1, 0.1],
                           [0.1, 0.7, 0],
                           [0.1, 0, 1]])
    my_graph = stag.random.general_sbm(cluster_sizes, prob_mat)
    print(my_graph.adjacency())
    \endcode

    @param cluster_sizes an array of length \f$k\f$ with the number of vertices
                         in each cluster.
    @param probabilities a \f$k \times k\f$ numpy matrix with the inter-cluster
                         probabilities.
    @param exact (optional) whether to use the exact probability distribution.
                 Default: false.
    @return the randomly generated stag.graph.Graph
    """
    return graph.Graph(stag_internal.general_sbm(
        cluster_sizes, utility.DenseMat(probabilities).internal_densemat, exact))


@utility.convert_ndarrays
def general_sbm_edgelist(filename: str,
                         cluster_sizes: np.ndarray,
                         probabilities: np.ndarray,
                         exact: bool = False) -> graph.Graph:
    r"""
    Generate a graph from the general stochastic block model and save the
    resulting graph as an edgelist file.

    This method uses only constant memory since the graph can be streamed to
    disk while it is being generated.

    @param filename the edgelist file to save the graph to
    @param cluster_sizes a list of length \f$k\f$ with the number of vertices in
                         each cluster.
    @param probabilities a \f$k \times k\f$ matrix with the inter-cluster
                         probabilities.
    @param exact (optional) whether to use the exact probability distribution.
                 Default: false.
    @return the randomly generated stag.graph.Graph
    """
    return stag_internal.general_sbm_edgelist(filename,
                                              cluster_sizes,
                                              utility.DenseMat(probabilities).internal_densemat,
                                              exact)


def erdos_renyi(n: int, p: float, exact: bool = False) -> graph.Graph:
    r"""
    Generate a graph from the Erdos-Renyi model.

    For large values of \f$n\f$, this method will use an approximate version of the
    random model with running time \f$O(\mathrm{nnz})\f$ where \f$\mathrm{nnz}\f$
    is the number of edges in the sampled graph.

    If the ``exact`` parameter is true, then the true Erdos-Renyi distribution
    will be used, with running time \f$O(n^2)\f$.

    @param n the number of vertices in the graph.
    @param p the probability of including each edge.
    @param exact (optional) whether to sample from the exact model.
    @return the randomly generated stag.graph.Graph
    """
    return graph.Graph(stag_internal.erdos_renyi(n, p, exact))


def sbm_gt_labels(n: int, k: int) -> np.ndarray:
    r"""
    Construct a vector with the ground truth labels for a graph drawn from the
    symmetric stochastic block model.

    \par Example

    \code{python}
    import stag.graph
    import stag.random

    n = 6
    k = 3
    myGraph = stag.random.sbm(n, k, 0.8, 0.1)

    gt_labels = stag.random.sbm_gt_labels(n, k)

    # gt_labels is the numpy array [0, 0, 1, 1, 2, 2].
    \endcode

    @param n the number of vertices in the graph
    @param k the number of clusters
    @return an array of integers containing the ground truth labels for the
            vertices in the graph.
    """
    return stag_internal.sbm_gt_labels(n, k)


@utility.convert_ndarrays
def general_sbm_gt_labels(cluster_sizes: np.ndarray) -> np.ndarray:
    r"""
    Construct a vector with the ground truth labels for a graph drawn from the
    general stochastic block model.

    \par Example

    \code{python}
    import stag.graph
    import stag.random
    import numpy as np

    cluster_sizes = np.asarray([4, 2])
    gt_labels = stag.random.general_sbm_gt_labels(cluster_sizes)

    # gt_labels is the numpy array [0, 0, 0, 0, 1, 1]
    \endcode

    @param cluster_sizes a list of length \f$k\f$ with the number of vertices
                         in each cluster.
    @return an array containing the ground truth labels for the vertices in the
            graph.
    """
    return stag_internal.general_sbm_gt_labels(cluster_sizes)
