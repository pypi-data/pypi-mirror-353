"""
Tests for the graph object.
"""
import numpy as np
import scipy as sp
import scipy.sparse
import networkx
import pytest
from context import stag
import stag.graph
import stag.random
import stag.graphio
import stag.utility

# Define the matrices of some useful graphs.
C4_ADJ_MAT = scipy.sparse.csc_matrix([[0, 1, 0, 1],
                                      [1, 0, 1, 0],
                                      [0, 1, 0, 1],
                                      [1, 0, 1, 0]])
C4_LAP_MAT = scipy.sparse.csc_matrix([[2, -1, 0, -1],
                                      [-1, 2, -1, 0],
                                      [0, -1, 2, -1],
                                      [-1, 0, -1, 2]])
K6_ADJ_MAT = scipy.sparse.csc_matrix([[0, 1, 1, 1, 1, 1],
                                      [1, 0, 1, 1, 1, 1],
                                      [1, 1, 0, 1, 1, 1],
                                      [1, 1, 1, 0, 1, 1],
                                      [1, 1, 1, 1, 0, 1],
                                      [1, 1, 1, 1, 1, 0]])
K6_LAP_MAT = scipy.sparse.csc_matrix([[5, -1, -1, -1, -1, -1],
                                      [-1, 5, -1, -1, -1, -1],
                                      [-1, -1, 5, -1, -1, -1],
                                      [-1, -1, -1, 5, -1, -1],
                                      [-1, -1, -1, -1, 5, -1],
                                      [-1, -1, -1, -1, -1, 5]])
BARBELL5_ADJ_MAT = scipy.sparse.csc_matrix([[0, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                                            [1, 0, 1, 1, 1, 0, 0, 0, 0, 0],
                                            [1, 1, 0, 1, 1, 0, 0, 0, 0, 0],
                                            [1, 1, 1, 0, 1, 0, 0, 0, 0, 0],
                                            [1, 1, 1, 1, 0, 1, 0, 0, 0, 0],
                                            [0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
                                            [0, 0, 0, 0, 0, 1, 0, 1, 1, 1],
                                            [0, 0, 0, 0, 0, 1, 1, 0, 1, 1],
                                            [0, 0, 0, 0, 0, 1, 1, 1, 0, 1],
                                            [0, 0, 0, 0, 0, 1, 1, 1, 1, 0],
                                            ])


def test_graph_constructor():
    # Start by constructing the cycle graph on 4 vertices.
    graph = stag.graph.Graph(C4_ADJ_MAT)

    # The graph has 4 vertices and 4 edges
    assert graph.number_of_vertices() == 4
    assert graph.number_of_edges() == 4

    # Check the vertex degrees
    for i in range(4):
        assert graph.degree(i) == 2

    # Now, try creating the complete graph on 6 vertices.
    graph = stag.graph.Graph(K6_ADJ_MAT)
    assert graph.number_of_vertices() == 6
    assert graph.number_of_edges() == 15
    for i in range(4):
        assert graph.degree(i) == 5

    # Now, try the barbell graph
    graph = stag.graph.Graph(BARBELL5_ADJ_MAT)
    assert graph.number_of_vertices() == 10
    assert graph.number_of_edges() == 21
    assert graph.degree(2) == 4
    assert graph.degree(4) == 5

    # Check that initialising with the Laplacian matrices gives the same result
    g1 = stag.graph.Graph(C4_ADJ_MAT)
    g2 = stag.graph.Graph(C4_LAP_MAT)
    assert g1 == g2

    g1 = stag.graph.Graph(K6_ADJ_MAT)
    g2 = stag.graph.Graph(K6_LAP_MAT)
    assert g1 == g2


def test_complete_graph():
    # Create a complete graph
    n = 4
    graph = stag.graph.complete_graph(n)
    expected_adjacency_matrix = sp.sparse.csc_matrix([[0, 1, 1, 1],
                                                      [1, 0, 1, 1],
                                                      [1, 1, 0, 1],
                                                      [1, 1, 1, 0]])

    assert graph.number_of_vertices() == 4
    adj_mat_diff = (graph.adjacency().to_scipy() - expected_adjacency_matrix)
    adj_mat_diff.eliminate_zeros()
    assert adj_mat_diff.nnz == 0

    expected_norm_lap = sp.sparse.csc_matrix([[1, -1/3, -1/3, -1/3],
                                              [-1/3, 1, -1/3, -1/3],
                                              [-1/3, -1/3, 1, -1/3],
                                              [-1/3, -1/3, -1/3, 1]])
    norm_lap_diff = (graph.normalised_laplacian().to_scipy() - expected_norm_lap)
    assert(np.all(norm_lap_diff.todense() == pytest.approx(0)))


def test_star_graph():
    # Create a star graph
    n = 5
    graph = stag.graph.star_graph(n)
    expected_adjacency_matrix = sp.sparse.csc_matrix([[0, 1, 1, 1, 1],
                                                      [1, 0, 0, 0, 0],
                                                      [1, 0, 0, 0, 0],
                                                      [1, 0, 0, 0, 0],
                                                      [1, 0, 0, 0, 0]])
    assert graph.number_of_vertices() == 5
    adj_mat_diff = (graph.adjacency().to_scipy() - expected_adjacency_matrix)
    adj_mat_diff.eliminate_zeros()
    assert adj_mat_diff.nnz == 0


def test_cycle_graph():
    # Create a cycle graph
    n = 5
    graph = stag.graph.cycle_graph(n)
    expected_adjacency_matrix = sp.sparse.csc_matrix([[0, 1, 0, 0, 1],
                                                      [1, 0, 1, 0, 0],
                                                      [0, 1, 0, 1, 0],
                                                      [0, 0, 1, 0, 1],
                                                      [1, 0, 0, 1, 0]])

    assert graph.number_of_vertices() == 5
    adj_mat_diff = (graph.adjacency().to_scipy() - expected_adjacency_matrix)
    adj_mat_diff.eliminate_zeros()
    assert adj_mat_diff.nnz == 0

    expected_laplacian_matrix = sp.sparse.csc_matrix([[2, -1, 0, 0, -1],
                                                      [-1, 2, -1, 0, 0],
                                                      [0, -1, 2, -1, 0],
                                                      [0, 0, -1, 2, -1],
                                                      [-1, 0, 0, -1, 2]])
    lap_diff = (graph.laplacian().to_scipy() - expected_laplacian_matrix)
    lap_diff.eliminate_zeros()
    assert lap_diff.nnz == 0


def test_identity_graph():
    # Create an identity graph
    n = 5
    graph = stag.graph.identity_graph(n)
    expected_mat = sp.sparse.csc_matrix([[1, 0, 0, 0, 0],
                                         [0, 1, 0, 0, 0],
                                         [0, 0, 1, 0, 0],
                                         [0, 0, 0, 1, 0],
                                         [0, 0, 0, 0, 1]])
    adj_mat_diff = graph.adjacency().to_scipy() - expected_mat
    adj_mat_diff.eliminate_zeros()
    assert adj_mat_diff.nnz == 0

    lap_mat_diff = graph.laplacian().to_scipy() - expected_mat
    lap_mat_diff.eliminate_zeros()
    assert lap_mat_diff.nnz == 0


def test_adjacency_matrix():
    graph = stag.graph.Graph(BARBELL5_ADJ_MAT)
    adj_mat_diff = (graph.adjacency().to_scipy() - BARBELL5_ADJ_MAT)
    adj_mat_diff.eliminate_zeros()
    assert adj_mat_diff.nnz == 0


def test_neighbors():
    graph = stag.graph.cycle_graph(10)
    ns = graph.neighbors(3)
    vs = [e.v2 for e in ns]
    assert vs == [2, 4]

    ns2 = graph.neighbors_unweighted(3)
    assert vs == list(ns2)


def test_symmetry():
    # Generate a large graph from the stochastic block model
    big_graph = stag.random.sbm(1000, 5, 0.8, 0.2)

    # Check that all of the graph matrices are truly symmetric
    assert np.allclose(big_graph.adjacency().to_dense(),
                       big_graph.adjacency().to_dense().T)

    lap_mat = big_graph.normalised_laplacian()
    lap_mat_dense = lap_mat.to_dense()
    assert np.allclose(lap_mat_dense, lap_mat_dense.T)

    lap_mat = big_graph.laplacian()
    lap_mat_dense = lap_mat.to_dense()
    assert np.allclose(lap_mat_dense, lap_mat_dense.T)


def test_num_edges():
    # Generate a known graph
    graph = stag.graph.Graph(BARBELL5_ADJ_MAT)

    # Check the number of edges in the graph
    assert graph.number_of_vertices() == 10
    assert graph.number_of_edges() == 21
    assert graph.total_volume() == 42

    # Now create a weighted graph and check the number of edges method.
    adjacency_matrix = scipy.sparse.csc_matrix([[0, 2, 0, 1],
                                                [2, 0, 3, 0],
                                                [0, 3, 0, 1],
                                                [1, 0, 1, 0]])
    graph = stag.graph.Graph(adjacency_matrix)
    assert graph.number_of_vertices() == 4
    assert graph.number_of_edges() == 4
    assert graph.total_volume() == 14


def test_float_weights():
    # Create a graph with floating-point edge weights.
    adjacency_matrix = scipy.sparse.csc_matrix([[0, 2.2, 0, 1],
                                                [2.2, 0, 3.1, 0],
                                                [0, 3.1, 0, 1.09],
                                                [1, 0, 1.09, 0]])
    graph = stag.graph.Graph(adjacency_matrix)
    assert graph.number_of_vertices() == 4
    assert graph.number_of_edges() == 4
    assert graph.total_volume() == pytest.approx(14.78)
    assert graph.degree(0) == pytest.approx(3.2)
    assert graph.degree(2) == pytest.approx(4.19)

    # Check the unweighted degrees
    assert graph.degree_unweighted(0) == 2
    assert graph.degree_unweighted(2) == 2


def test_networkx():
    # Test the methods for converting from and to networkx graphs.
    # Start by constructing a networkx graph
    netx_graph = networkx.generators.barbell_graph(4, 1)
    graph = stag.graph.from_networkx(netx_graph)

    assert graph.number_of_vertices() == 9
    assert graph.number_of_edges() == 14

    expected_adjacency_matrix = sp.sparse.csc_matrix([[0, 1, 1, 1, 0, 0, 0, 0, 0],
                                                      [1, 0, 1, 1, 0, 0, 0, 0, 0],
                                                      [1, 1, 0, 1, 0, 0, 0, 0, 0],
                                                      [1, 1, 1, 0, 0, 0, 0, 0, 1],
                                                      [0, 0, 0, 0, 0, 1, 1, 1, 1],
                                                      [0, 0, 0, 0, 1, 0, 1, 1, 0],
                                                      [0, 0, 0, 0, 1, 1, 0, 1, 0],
                                                      [0, 0, 0, 0, 1, 1, 1, 0, 0],
                                                      [0, 0, 0, 1, 1, 0, 0, 0, 0]])
    adj_mat_diff = (graph.adjacency().to_scipy() - expected_adjacency_matrix)
    adj_mat_diff.eliminate_zeros()
    assert adj_mat_diff.nnz == 0

    # Now, construct a graph using the sgtl Graph object, and convert it to networkx
    graph = stag.graph.Graph(expected_adjacency_matrix)
    netx_graph = graph.to_networkx()

    # Check that the networkx graph looks correct
    assert netx_graph.number_of_nodes() == 9
    assert netx_graph.number_of_edges() == 14
    assert netx_graph.has_edge(0, 1)
    assert netx_graph.has_edge(3, 8)
    assert netx_graph.has_edge(8, 4)
    assert not netx_graph.has_edge(2, 8)


def test_degree_matrix():
    # Construct a graph and get its degree matrix
    g = stag.graph.barbell_graph(4)
    expected_degree_mat = sp.sparse.diags([3, 3, 3, 4, 4, 3, 3, 3])
    deg_mat_diff = g.degree_matrix().to_scipy() - expected_degree_mat
    assert(np.all(deg_mat_diff.todense() == pytest.approx(0)))


def test_inverse_degree_matrix():
    # Construct a graph and get its inverse degree matrix
    g = stag.graph.barbell_graph(4)
    expected_inv_degree_mat = sp.sparse.diags([1/3, 1/3, 1/3, 1/4, 1/4, 1/3, 1/3, 1/3])
    inv_deg_mat_diff = g.inverse_degree_matrix().to_scipy() - expected_inv_degree_mat
    assert(np.all(inv_deg_mat_diff.todense() == pytest.approx(0)))


def test_lazy_random_walk_matrix():
    # Construct a graph
    g = stag.graph.barbell_graph(3)
    expected_rw_mat = sp.sparse.csc_matrix([[1/2, 1/4, 1/6,   0,   0,   0],
                                            [1/4, 1/2, 1/6,   0,   0,   0],
                                            [1/4, 1/4, 1/2, 1/6,   0,   0],
                                            [  0,   0, 1/6, 1/2, 1/4, 1/4],
                                            [  0,   0,   0, 1/6, 1/2, 1/4],
                                            [  0,   0,   0, 1/6, 1/4, 1/2]])
    rw_mat_diff = g.lazy_random_walk_matrix().to_scipy() - expected_rw_mat
    assert(np.all(rw_mat_diff.todense() == pytest.approx(0)))


def test_edge():
    # Test the edge object
    e = stag.graph.Edge(1, 2, 0.3)
    assert(e.v1 == 1)
    assert(e.v2 == 2)
    assert(e.weight == 0.3)

    # Define two edges and make sure they are equal
    e2 = stag.graph.Edge(1, 2, 0.3)
    assert(e == e2)

    # Define a different edge
    e3 = stag.graph.Edge(1, 3, 0.2)
    assert (e2 != e3)


def test_graph_equality():
    g1 = stag.graph.complete_graph(6)
    g2 = stag.graph.complete_graph(6)
    assert g1 == g2

    g3 = stag.graph.Graph(K6_ADJ_MAT)
    assert g2 == g3

    g4 = stag.graph.Graph(BARBELL5_ADJ_MAT)
    assert g2 != g4

    g5 = stag.graph.barbell_graph(5)
    assert g4 == g5


def test_graph_degrees():
    g1 = stag.graph.barbell_graph(4)
    degrees = g1.degrees_unweighted([0, 1, 2, 3, 4, 5])
    assert list(degrees) == [3, 3, 3, 4, 4, 3]

    # Test np.ndarray objects
    degrees = g1.degrees_unweighted(np.asarray([0, 1, 2, 3, 4, 5]))
    assert list(degrees) == [3, 3, 3, 4, 4, 3]


def test_graph_average_degree():
    g = stag.graph.barbell_graph(4)
    avg_degree = g.average_degree()
    assert avg_degree == 26/8


def test_adjacencylist_graph():
    file = "data/test1.adjlist"
    g = stag.graph.AdjacencyListLocalGraph(file)
    assert g.vertex_exists(1)
    assert not g.vertex_exists(10)


def test_subgraph():
    g1 = stag.graph.Graph(BARBELL5_ADJ_MAT)

    vertices = [3, 4, 5, 6]
    g2 = g1.subgraph(vertices)
    expected_adj_mat = sp.sparse.csc_matrix([[0, 1, 0, 0],
                                             [1, 0, 1, 0],
                                             [0, 1, 0, 1],
                                             [0, 0, 1, 0]])
    mat_diff = g2.adjacency().to_scipy() - expected_adj_mat
    assert(np.all(mat_diff.todense() == pytest.approx(0)))

    # Check that numpy arrays also work
    g3 = g1.subgraph(np.asarray(vertices))
    assert g2 == g3


def test_union():
    g1 = stag.graph.complete_graph(3)
    g2 = stag.graph.cycle_graph(3)
    g3 = g1.disjoint_union(g2)
    expected_adj_mat = sp.sparse.csc_matrix([[0, 1, 1, 0, 0, 0],
                                             [1, 0, 1, 0, 0, 0],
                                             [1, 1, 0, 0, 0, 0],
                                             [0, 0, 0, 0, 1, 1],
                                             [0, 0, 0, 1, 0, 1],
                                             [0, 0, 0, 1, 1, 0]])
    mat_diff = g3.adjacency().to_scipy() - expected_adj_mat
    assert (np.all(mat_diff.todense() == pytest.approx(0)))


def test_self_loops():
    adj_mat = sp.sparse.csc_matrix([[1, 1, 1],
                                    [1, 0, 0],
                                    [1, 0, 1]])
    graph = stag.graph.Graph(adj_mat)
    assert graph.has_self_loops()

    graph = stag.graph.complete_graph(5)
    assert not graph.has_self_loops()


def test_connected():
    g1 = stag.graph.cycle_graph(100)
    assert g1.is_connected()

    g2 = stag.random.sbm(100, 2, 0.5, 0)
    assert not g2.is_connected()

    g3 = g1.disjoint_union(stag.graph.complete_graph(3))
    assert not g3.is_connected()

    g4 = stag.random.sbm(100, 1, 0.7, 0)
    assert g4.is_connected()


def test_add_graphs():
    g1 = stag.graph.complete_graph(4)
    g2 = stag.graph.cycle_graph(4)
    g3 = g1 + g2
    expected_adj_mat = sp.sparse.csc_matrix([[0, 2, 1, 2],
                                             [2, 0, 2, 1],
                                             [1, 2, 0, 2],
                                             [2, 1, 2, 0]])
    mat_diff = g3.adjacency().to_scipy() - expected_adj_mat
    assert (np.all(mat_diff.todense() == pytest.approx(0)))

    g4 = stag.graph.cycle_graph(5)
    try:
        g = g1 + g4

        # We should not reach this point
        assert False
    except ValueError as error:
        assert True


def test_scalar_multiplication():
    g1 = stag.graph.cycle_graph(4)
    g2 = 2 * g1
    g3 = g1 * 2
    assert g2 == g3

    expected_adj_mat = sp.sparse.csc_matrix([[0, 2, 0, 2],
                                             [2, 0, 2, 0],
                                             [0, 2, 0, 2],
                                             [2, 0, 2, 0]])
    mat_diff = g3.adjacency().to_scipy() - expected_adj_mat
    assert (np.all(mat_diff.todense() == pytest.approx(0)))


def test_invalid_matrix_initialisation():
    """See STAG C++ Issue 126."""
    # Try creating a bad graph
    with pytest.raises(AttributeError):
        bad_mat = sp.sparse.csc_matrix([[0, -1, 0, 1],
                                        [-1, 0, 1, 0],
                                        [0, 1, 0, 1],
                                        [1, 0, 1, 0]])
        g = stag.graph.Graph(bad_mat)


def test_add_edge():
    # Create a graph
    mat = sp.sparse.csc_matrix([[5.3333, -2, -3.3333, 0],
                                [-2, 8, -6, 0],
                                [-3.3333, -6, 10.3333, -1],
                                [0, 0, -1, 1]])
    g = stag.graph.Graph(mat)

    # Add an edge
    g.add_edge(1, 3, 1.5)

    # Check that the graph looks as we expect
    expected_adj_mat = sp.sparse.csc_matrix([[0, 2, 3.3333, 0],
                                             [2, 0, 6, 1.5],
                                             [3.3333, 6, 0, 1],
                                             [0, 1.5, 1, 0]])
    mat_diff = g.adjacency().to_scipy() - expected_adj_mat
    assert (np.all(mat_diff.todense() == pytest.approx(0)))


def test_increase_weight():
    # Create a graph
    mat = sp.sparse.csc_matrix([[5.3333, -2, -3.3333, 0],
                                [-2, 8, -6, 0],
                                [-3.3333, -6, 10.3333, -1],
                                [0, 0, -1, 1]])
    g = stag.graph.Graph(mat)

    # Add an edge
    g.add_edge(0, 1, 0.5)

    # Check that the graph looks as we expect
    expected_adj_mat = sp.sparse.csc_matrix([[0, 2.5, 3.3333, 0],
                                             [2.5, 0, 6, 0],
                                             [3.3333, 6, 0, 1],
                                             [0, 0, 1, 0]])
    mat_diff = g.adjacency().to_scipy() - expected_adj_mat
    assert (np.all(mat_diff.todense() == pytest.approx(0)))


def test_remove_edge():
    # Create a graph
    mat = sp.sparse.csc_matrix([[5.3333, -2, -3.3333, 0],
                                [-2, 8, -6, 0],
                                [-3.3333, -6, 10.3333, -1],
                                [0, 0, -1, 1]])
    g = stag.graph.Graph(mat)

    # Remove an edge
    g.remove_edge(0, 2)

    # Check that the graph looks as we expect
    expected_adj_mat = sp.sparse.csc_matrix([[0, 2, 0, 0],
                                             [2, 0, 6, 0],
                                             [0, 6, 0, 1],
                                             [0, 0, 1, 0]])
    mat_diff = g.adjacency().to_scipy() - expected_adj_mat
    assert (np.all(mat_diff.todense() == pytest.approx(0)))


def test_add_vertices():
    # Create a graph
    mat = sp.sparse.csc_matrix([[5.3333, -2, -3.3333, 0],
                                [-2, 8, -6, 0],
                                [-3.3333, -6, 10.3333, -1],
                                [0, 0, -1, 1]])
    g = stag.graph.Graph(mat)
    assert(g.number_of_vertices() == 4)

    # Add an edge which adds two vertices
    g.add_edge(1, 5, 1.5)
    assert(g.number_of_vertices() == 6)

    # Check that the graph looks as we expect
    expected_adj_mat = sp.sparse.csc_matrix([[0, 2, 3.3333, 0, 0, 0],
                                             [2, 0, 6, 0, 0, 1.5],
                                             [3.3333, 6, 0, 1, 0, 0],
                                             [0, 0, 1, 0, 0, 0],
                                             [0, 0, 0, 0, 0, 0],
                                             [0, 1.5, 0, 0, 0, 0]])
    mat_diff = g.adjacency().to_scipy() - expected_adj_mat
    assert (np.all(mat_diff.todense() == pytest.approx(0)))


def test_initialise_with_negative_weights():
    # See stagpy issue #43.
    mat = stag.utility.SprsMat([[0, -1, 0, 1],
                                [-1, 0, 1, 0],
                                [0, 1, 0, 1],
                                [1, 0, 1, 0]])

    # Initialising a graph should throw an error
    with pytest.raises(AttributeError):
        _ = stag.graph.Graph(mat)

        
def test_square_adjacency():
    # See stagpy issue #49.
    # Create a graph with some nodes of degree 0.
    g = stag.random.sbm(100, 10, 0.01, 0)

    # Check that the adjacency matrix is square
    adj = g.adjacency()
    rows = adj.shape()[0]
    cols = adj.shape()[1]
    assert(rows == cols)

    # Matrix should still be square when converted to scipy
    adj = adj.to_scipy()
    rows = adj.shape[0]
    cols = adj.shape[1]
    assert(rows == cols)
