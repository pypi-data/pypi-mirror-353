/*
   This file is provided as part of the STAG library and released under the GPL
   license.
*/
#include <stdexcept>
#include <fstream>
#include <unordered_map>
#include <unordered_set>
#include <set>
#include "graph.h"
#include "utility.h"
#include "graphio.h"
#include "cluster.h"


//------------------------------------------------------------------------------
// Graph Object Constructors
//------------------------------------------------------------------------------
/**
 * Given a matrix, which is either an adjacency matrix OR a Laplacian matrix,
 * return the adjacency matrix of the graph.
 *
 * Throws a std::domain_error if the provided matrix doesn't look like an
 * adjacency matrix or Laplacian matrix of an unsigned graph.
 */
SprsMat adjacency_from_adj_or_lap(const SprsMat& matrix) {
  // Since we support only graphs with positive edge weights,
  // we can just check for negative entries in the matrix. If the matrix contains
  // negative entries, then it must be the Laplacian. Otherwise, we take it to
  // be an adjacency matrix.
  //
  // If we find a negative entry, then we check the following properties of the
  // Laplacian matrix:
  //    - no positive off-diagonal entries
  //    - diagonal entries are non-negative
  //    - matrix is diagonally dominant
  SprsMat adjacency_matrix(matrix.rows(), matrix.cols());
  bool found_negative_value = false;
  bool positive_off_diagonal_value = false;
  bool diagonally_dominant = true;
  for (int k = 0; k < matrix.outerSize() ; ++k) {
    StagReal col_total = 0;
    for (SprsMat::InnerIterator it(matrix, k); it; ++it) {
      col_total += it.value();
      if (it.value() < 0) {
        found_negative_value = true;
      } else {
        if (it.row() != it.col()) positive_off_diagonal_value = true;
      }
    }
    if (col_total < 0) diagonally_dominant = false;
  }

  if (found_negative_value) {
    // Check that the matrix is diagonally dominant and has no positive
    // off-diagonal entries.
    if (positive_off_diagonal_value) throw std::domain_error("Off-diagonal entries should be all negative or all positive.");
    if (!diagonally_dominant) throw std::domain_error("Laplacian matrix should be diagonally dominant.");

    // The adjacency matrix is D - L
    // First set it to negative the Laplacian, and then update the diagonal
    // entries.
    adjacency_matrix = -matrix;

    // The self-loop weights are equal to the difference between the diagonal
    // entry of the Laplacian and the rest of the entries in the row/column
    Eigen::VectorXd self_loop_weights = matrix * Eigen::VectorXd::Ones(matrix.cols());
    for (auto i = 0; i < matrix.cols(); i++) {
      adjacency_matrix.coeffRef(i, i) = self_loop_weights.coeff(i);
    }
  } else {
    adjacency_matrix = matrix;
  }
  // Due to floating-point errors, we sometimes see tiny floats showing up
  // in place of zeros. We don't want to introduce self-loops with tiny weights
  // so we set these to 0.
  adjacency_matrix.prune([](const StagInt& row, const StagInt& col, const StagReal& value)
                          {
                            (void) row;
                            (void) col;
                            return value > EPSILON;
                          });

  return adjacency_matrix;
}

stag::Graph::Graph(const SprsMat& matrix) {
  // Get the adjacency matrix from the provided (adjacency or Laplacian) matrix
  adjacency_matrix_ = adjacency_from_adj_or_lap(matrix);

  // The number of vertices is the dimensions of the adjacency matrix
  number_of_vertices_ = adjacency_matrix_.outerSize();

  // Check whether the graph has any self-loops
  has_self_loops_ = false;
  for (auto i = 0; i < number_of_vertices_; i++) {
    if (adjacency_matrix_.coeff(i, i) != 0) {
      has_self_loops_ = true;
      break;
    }
  }

  // Set the flags to indicate which matrices have been initialised.
  lap_init_ = false;
  signless_lap_init_ = false;
  signless_norm_lap_init_ = false;
  deg_init_ = false;
  inv_deg_init_ = false;
  norm_lap_init_ = false;
  lazy_rand_walk_init_ = false;

  // Check that the graph is configured correctly
  self_test_();
}

stag::Graph::Graph(std::vector<StagInt> &outerStarts, std::vector<StagInt> &innerIndices,
                   std::vector<StagReal> &values) {
  // Map the provided data vectors to the sparse matrix type.
  SprsMat matrix = stag::sprsMatFromVectors(outerStarts, innerIndices, values);
  adjacency_matrix_ = adjacency_from_adj_or_lap(matrix);

  // The number of vertices is the dimensions of the adjacency matrix
  number_of_vertices_ = adjacency_matrix_.outerSize();

  // Check whether the graph has any self-loops
  has_self_loops_ = false;
  for (auto i = 0; i < number_of_vertices_; i++) {
    if (adjacency_matrix_.coeff(i, i) != 0) {
      has_self_loops_ = true;
      break;
    }
  }

  // Set the flags to indicate which matrices have been initialised.
  lap_init_ = false;
  signless_lap_init_ = false;
  signless_norm_lap_init_ = false;
  deg_init_ = false;
  inv_deg_init_ = false;
  norm_lap_init_ = false;
  lazy_rand_walk_init_ = false;

  // Check that the graph is configured correctly
  self_test_();
}

//------------------------------------------------------------------------------
// Graph Object Public Methods
//------------------------------------------------------------------------------

const SprsMat* stag::Graph::adjacency() const {
  return &adjacency_matrix_;
}

const SprsMat* stag::Graph::laplacian() {
  initialise_laplacian_();
  return &laplacian_matrix_;
}

const SprsMat* stag::Graph::normalised_laplacian() {
  initialise_normalised_laplacian_();
  return &normalised_laplacian_matrix_;
}

const SprsMat* stag::Graph::signless_laplacian() {
  initialise_signless_laplacian_();
  return &signless_laplacian_matrix_;
}

const SprsMat* stag::Graph::normalised_signless_laplacian() {
  initialise_normalised_signless_laplacian_();
  return &normalised_signless_laplacian_matrix_;
}

const SprsMat* stag::Graph::degree_matrix() {
  initialise_degree_matrix_();
  return &degree_matrix_;
}

const SprsMat* stag::Graph::inverse_degree_matrix() {
  initialise_inverse_degree_matrix_();
  return &inverse_degree_matrix_;
}

const SprsMat* stag::Graph::lazy_random_walk_matrix() {
  initialise_lazy_random_walk_matrix_();
  return &lazy_random_walk_matrix_;
}

StagReal stag::Graph::total_volume() {
  // We will compute the total volume from the degree matrix of the graph.
  initialise_degree_matrix_();

  StagReal vol = 0;
  for (int k = 0; k < degree_matrix_.outerSize() ; ++k) {
    for (SprsMat::InnerIterator it(degree_matrix_, k); it; ++it) {
      vol += it.value();
    }
  }

  return vol;
}

StagReal stag::Graph::average_degree() {
  return total_volume() / number_of_vertices_;
}

StagInt stag::Graph::number_of_vertices() const {
  return number_of_vertices_;
}

StagInt stag::Graph::number_of_edges() const {
  StagInt nnz = adjacency_matrix_.nonZeros();

  if (has_self_loops_) {
    // If there are self loops in the graph, then we need to count the non-zeros
    // on the diagonal twice.
    for (auto i = 0; i < number_of_vertices_; i++) {
      if (adjacency_matrix_.coeff(i, i) != 0) nnz++;
    }

    // Now, we have counted every edge twice.
    return nnz / 2;
  } else {
    // If there are no self loops in the graph, then the number of edges is
    // half the number of non-zero elements in the adjacency matrix.
    return nnz / 2;
  }
}

void stag::Graph::add_edge(StagInt i, StagInt j, StagReal w) {
  number_of_vertices_ = MAX(number_of_vertices_, MAX(i, j) + 1);
  adjacency_matrix_.conservativeResize(number_of_vertices_, number_of_vertices_);
  adjacency_matrix_.coeffRef(i, j) += w;
  adjacency_matrix_.coeffRef(j, i) += w;
  adjacency_matrix_.makeCompressed();

  if (i == j) {
    has_self_loops_ = true;
  }

  // Set the flags to indicate which matrices have been initialised.
  lap_init_ = false;
  signless_lap_init_ = false;
  signless_norm_lap_init_ = false;
  deg_init_ = false;
  inv_deg_init_ = false;
  norm_lap_init_ = false;
  lazy_rand_walk_init_ = false;
}

void stag::Graph::remove_edge(StagInt i, StagInt j) {
  if (i >= number_of_vertices_ || j >= number_of_vertices_) return;

  adjacency_matrix_.coeffRef(i, j) = 0;
  adjacency_matrix_.coeffRef(j, i) = 0;
  adjacency_matrix_.prune(0.0);
  adjacency_matrix_.makeCompressed();

  if (i == j) {
    assert(has_self_loops_);

    // If we removed a self-loop, we need to check whether there is still
    // a self loop.
    has_self_loops_ = false;
    for (auto i = 0; i < number_of_vertices_; i++) {
      if (adjacency_matrix_.coeff(i, i) != 0) {
        has_self_loops_ = true;
        break;
      }
    }
  }

  // Set the flags to indicate which matrices have been initialised.
  lap_init_ = false;
  signless_lap_init_ = false;
  signless_norm_lap_init_ = false;
  deg_init_ = false;
  inv_deg_init_ = false;
  norm_lap_init_ = false;
  lazy_rand_walk_init_ = false;
}

bool stag::Graph::has_self_loops() const {
  return has_self_loops_;
}

bool stag::Graph::is_connected() {
  if ((StagInt) stag::connected_component(this, 0).size()
        == number_of_vertices_) return true;
  return false;
}

void stag::Graph::check_vertex_argument(StagInt v) const {
  // Check that the value is smaller than the number of vertices
  if (v >= number_of_vertices_) {
    throw std::invalid_argument("Specified vertex index too large.");
  }

  // Check that the specified vertex is not negative
  if (v < 0) {
    throw std::invalid_argument("Vertex indices cannot be negative.");
  }
}

//------------------------------------------------------------------------------
// Local Graph Methods
//------------------------------------------------------------------------------

std::vector<StagReal> stag::Graph::degrees(std::vector<StagInt> vertices) {
    std::vector<StagReal> degrees;

    for (StagInt v : vertices) {
        degrees.emplace_back(degree(v));
    }

    return degrees;
}

std::vector<StagInt> stag::Graph::degrees_unweighted(
        std::vector<StagInt> vertices) {
    std::vector<StagInt> degrees;

    for (StagInt v : vertices) {
        degrees.emplace_back(degree_unweighted(v));
    }

    return degrees;
}


StagReal stag::Graph::degree(StagInt v) {
  check_vertex_argument(v);

  // For now, we can be a little lazy and use the degree matrix. Once this is
  // initialised, then checking degree is constant time.
  initialise_degree_matrix_();
  return degree_matrix_.coeff(v, v);
}

StagInt stag::Graph::degree_unweighted(StagInt v) {
  check_vertex_argument(v);

  // The combinatorical degree of a vertex is equal to the number of non-zero
  // entries in its adjacency matrix row, plus 1 if there is a self-loop.
  const StagInt *indexPtr = adjacency_matrix_.outerIndexPtr();
  StagInt rowStart = *(indexPtr + v);
  StagInt nextRowStart = *(indexPtr + v + 1);
  StagInt self_loop = 0;
  if (adjacency_matrix_.coeff(v, v) != 0) self_loop = 1;

  return nextRowStart - rowStart + self_loop;
}

std::vector<stag::edge> stag::Graph::neighbors(StagInt v) {
  check_vertex_argument(v);

  // Iterate through the non-zero entries in the vth row of the adjacency matrix
  const StagReal *weights = adjacency_matrix_.valuePtr();
  const StagInt *innerIndices = adjacency_matrix_.innerIndexPtr();
  const StagInt *rowStarts = adjacency_matrix_.outerIndexPtr();
  StagInt vRowStart = *(rowStarts + v);
  StagInt degree_unw = degree_unweighted(v);

  // If there is a self-loop, then we have to subtract one from the unweighted
  // degree.
  StagInt self_loop = 0;
  if (adjacency_matrix_.coeff(v, v) != 0) self_loop = 1;

  std::vector<stag::edge> edges;
  for (StagInt i = 0; i < degree_unw - self_loop; i++) {
    if (*(weights + vRowStart + i) != 0) {
      edges.push_back({v, *(innerIndices + vRowStart + i), *(weights + vRowStart + i)});
    }
  }

  return edges;
}

std::vector<StagInt> stag::Graph::neighbors_unweighted(StagInt v) {
  check_vertex_argument(v);

  // Return the non-zero indices in the vth row of the adjacency matrix
  const StagInt *innerIndices = adjacency_matrix_.innerIndexPtr();
  const StagInt *rowStarts = adjacency_matrix_.outerIndexPtr();
  StagInt vRowStart = *(rowStarts + v);
  StagInt degree = degree_unweighted(v);

  // If there is a self-loop, then we have to subtract one from the unweighted
  // degree.
  StagInt self_loop = 0;
  if (adjacency_matrix_.coeff(v, v) != 0) self_loop = 1;

  return {innerIndices + vRowStart, innerIndices + vRowStart + degree - self_loop};
}

bool stag::Graph::vertex_exists(StagInt v) {
  return v >= 0 && v < number_of_vertices_;
}

stag::Graph stag::Graph::subgraph(std::vector<StagInt>& vertices) {
  // Convert the vector of vertices to a set, and construct the map from old
  // vertex ID to the new one.
  std::unordered_set<StagInt> vertex_set;
  std::unordered_map<StagInt, StagInt> old_to_new_id;
  StagInt next_id = 0;
  for (StagInt v : vertices) {
    if (!vertex_set.contains(v)) {
      vertex_set.insert(v);
      old_to_new_id.insert({v, next_id});
      next_id++;
    }
  }

  // Construct the non-zero entries in the new adjacency matrix
  std::vector<EdgeTriplet> non_zero_entries;
  for (StagInt v : vertex_set) {
    for (stag::edge e : neighbors(v)) {
      if (e.v2 >= v && vertex_set.contains(e.v2)) {
        non_zero_entries.emplace_back(
            old_to_new_id[v], old_to_new_id[e.v2], e.weight);

        // Add the symmetric entry to the adjacency matrix only if this is
        // not a self-loop.
        if (e.v2 > v) {
          non_zero_entries.emplace_back(
              old_to_new_id[e.v2], old_to_new_id[v], e.weight);
        }
      }
    }
  }

  // Construct the final adjacency matrix
  SprsMat adj_mat((StagInt) vertex_set.size(), (StagInt) vertex_set.size());
  adj_mat.setFromTriplets(non_zero_entries.begin(), non_zero_entries.end());
  return stag::Graph(adj_mat);
}

stag::Graph stag::Graph::disjoint_union(Graph& other) {
  // Get the adjacency matrix data from this graph
  std::vector<StagReal> values = stag::sprsMatValues(&adjacency_matrix_);
  std::vector<StagInt> innerIndices = stag::sprsMatInnerIndices(&adjacency_matrix_);
  std::vector<StagInt> outerStarts = stag::sprsMatOuterStarts(&adjacency_matrix_);

  // Get the adjacency matrix data from the other graph
  SprsMat other_adj = *other.adjacency();
  std::vector<StagReal> other_values = stag::sprsMatValues(&other_adj);
  std::vector<StagInt> other_innerIndices = stag::sprsMatInnerIndices(&other_adj);
  std::vector<StagInt> other_outerStarts = stag::sprsMatOuterStarts(&other_adj);

  // We will extend the matrix data vectors with the data from the other graph
  values.reserve(values.size() + distance(other_values.begin(),
                                          other_values.end()));
  values.insert(values.end(), other_values.begin(), other_values.end());

  StagInt start_offset = outerStarts.at(outerStarts.size() - 1);
  for (StagInt other_start : other_outerStarts) {
    if (other_start != 0) {
      outerStarts.push_back(other_start + start_offset);
    }
  }

  StagInt inner_offset = number_of_vertices_;
  for (StagInt other_inner : other_innerIndices) {
    innerIndices.push_back(other_inner + inner_offset);
  }

  return {outerStarts, innerIndices, values};
}

//------------------------------------------------------------------------------
// Graph Object Private Methods
//------------------------------------------------------------------------------

void stag::Graph::self_test_() {
  // Check that the adjacency matrix is symmetric.
  if (!stag::isSymmetric(&adjacency_matrix_)) {
    throw std::domain_error("STAG Error: graph adjacency matrix must be symmetric.");
  }
}

void stag::Graph::initialise_laplacian_() {
  // If the laplacian matrix has already been initialised, then we do not
  // initialise it again.
  if (lap_init_) return;

  // Ensure that the degree matrix is initialised
  initialise_degree_matrix_();

  // Construct and return the laplacian matrix.
  laplacian_matrix_ = degree_matrix_ - adjacency_matrix_;
  laplacian_matrix_.makeCompressed();

  // We have now initialised the laplacian.
  lap_init_ = true;
}

void stag::Graph::initialise_signless_laplacian_() {
  // If the signless laplacian matrix has already been initialised, then we do not
  // initialise it again.
  if (signless_lap_init_) return;

  // Ensure that the degree matrix is initialised
  initialise_degree_matrix_();

  // Construct and return the signless Laplacian matrix.
  signless_laplacian_matrix_ = degree_matrix_ + adjacency_matrix_;
  signless_laplacian_matrix_.makeCompressed();

  // We have now initialised the signless laplacian.
  signless_lap_init_ = true;
}

void stag::Graph::initialise_normalised_laplacian_() {
  // If the normalised laplacian matrix has already been initialised, then we
  // do not initialise it again.
  if (norm_lap_init_) return;

  // Ensure that the degree matrix is initialised
  initialise_degree_matrix_();

  // Construct the inverse degree matrix
  SprsMat sqrt_inv_deg_mat(number_of_vertices_, number_of_vertices_);
  std::vector<EdgeTriplet> non_zero_entries;
  for (StagInt i = 0; i < number_of_vertices_; i++) {
    non_zero_entries.emplace_back(i, i, 1 / sqrt(degree_matrix_.coeff(i, i)));
  }
  sqrt_inv_deg_mat.setFromTriplets(non_zero_entries.begin(), non_zero_entries.end());

  // The normalised laplacian is defined by I - D^{-1/2} A D^{-1/2}
  SprsMat identity_matrix(number_of_vertices_, number_of_vertices_);
  identity_matrix.setIdentity();
  normalised_laplacian_matrix_ = identity_matrix - sqrt_inv_deg_mat * adjacency_matrix_ * sqrt_inv_deg_mat;
  normalised_laplacian_matrix_.makeCompressed();

  // We have now initialised the normalised laplacian matrix.
  norm_lap_init_ = true;
}

void stag::Graph::initialise_normalised_signless_laplacian_() {
  // If the normalised signless laplacian matrix has already been initialised, then we
  // do not initialise it again.
  if (signless_norm_lap_init_) return;

  // Ensure that the degree matrix is initialised
  initialise_degree_matrix_();

  // Construct the inverse degree matrix
  SprsMat sqrt_inv_deg_mat(number_of_vertices_, number_of_vertices_);
  std::vector<EdgeTriplet> non_zero_entries;
  for (StagInt i = 0; i < number_of_vertices_; i++) {
    non_zero_entries.emplace_back(i, i, 1 / sqrt(degree_matrix_.coeff(i, i)));
  }
  sqrt_inv_deg_mat.setFromTriplets(non_zero_entries.begin(), non_zero_entries.end());

  // The normalised signless laplacian is defined by I + D^{-1/2} A D^{-1/2}
  SprsMat identity_matrix(number_of_vertices_, number_of_vertices_);
  identity_matrix.setIdentity();
  normalised_signless_laplacian_matrix_ = identity_matrix + sqrt_inv_deg_mat * adjacency_matrix_ * sqrt_inv_deg_mat;
  normalised_signless_laplacian_matrix_.makeCompressed();

  // We have now initialised the normalised laplacian matrix.
  signless_norm_lap_init_ = true;
}

void stag::Graph::initialise_degree_matrix_() {
  // If the degree matrix has already been initialised, then we do not
  // initialise it again.
  if (deg_init_) return;

  // Construct the vertex degrees.
  Eigen::VectorXd simple_degrees = adjacency_matrix_ * Eigen::VectorXd::Ones(adjacency_matrix_.cols());
  degree_matrix_ = SprsMat(adjacency_matrix_.cols(), adjacency_matrix_.cols());
  for (StagInt i = 0; i < adjacency_matrix_.cols(); i++) {
    // If there is a self-loop on this vertex, then we count its weight twice
    // for the vertex degree.
    degree_matrix_.insert(i, i) = simple_degrees[i] + adjacency_matrix_.coeff(i, i);
  }

  // Compress the degree matrix storage, and set the initialised flag
  degree_matrix_.makeCompressed();
  deg_init_ = true;
}

void stag::Graph::initialise_inverse_degree_matrix_() {
  // If the inverse degree matrix has already been initialised, then we do not
  // initialise it again.
  if (inv_deg_init_) return;

  // We will construct the inverse degree matrix from the degree matrix itself
  initialise_degree_matrix_();
  inverse_degree_matrix_ = SprsMat(adjacency_matrix_.cols(), adjacency_matrix_.cols());
  for (StagInt i = 0; i < adjacency_matrix_.cols(); i++) {
    inverse_degree_matrix_.insert(i, i) = 1./degree_matrix_.coeff(i, i);
  }

  // Compress the degree matrix storage, and set the initialised flag
  inverse_degree_matrix_.makeCompressed();
  inv_deg_init_ = true;
}

void stag::Graph::initialise_lazy_random_walk_matrix_() {
  // If the lazy random walk matrix has already been initialised, then we do not
  // initialise it again.
  if (lazy_rand_walk_init_) return;

  // The lazy random walk matrix is defined to be
  //   (1/2) I + (1/2) A * D^{-1}
  initialise_inverse_degree_matrix_();
  SprsMat identityMatrix(number_of_vertices_, number_of_vertices_);
  identityMatrix.setIdentity();

  lazy_random_walk_matrix_ = SprsMat(number_of_vertices_, number_of_vertices_);
  lazy_random_walk_matrix_ = (1./2) * identityMatrix + (1./2) * adjacency_matrix_ * inverse_degree_matrix_;

  // Compress and set initialisation flag
  lazy_random_walk_matrix_.makeCompressed();
  lazy_rand_walk_init_ = true;
}

//------------------------------------------------------------------------------
// Equality Operators
//------------------------------------------------------------------------------
bool stag::operator==(const stag::Graph& lhs, const stag::Graph& rhs) {
  bool outerIndicesEqual = stag::sprsMatOuterStarts(lhs.adjacency()) == stag::sprsMatOuterStarts(rhs.adjacency());
  bool innerIndicesEqual = stag::sprsMatInnerIndices(lhs.adjacency()) == stag::sprsMatInnerIndices(rhs.adjacency());
  bool valuesEqual = stag::sprsMatValues(lhs.adjacency()) == stag::sprsMatValues(rhs.adjacency());
  return (outerIndicesEqual && innerIndicesEqual) && valuesEqual;
}

bool stag::operator!=(const stag::Graph &lhs, const stag::Graph &rhs) {
  return !(lhs == rhs);
}

bool stag::operator==(const stag::edge &lhs, const stag::edge &rhs) {
  return lhs.v1 == rhs.v1 && lhs.v2 == rhs.v2 && lhs.weight == rhs.weight;
}

bool stag::operator!=(const stag::edge &lhs, const stag::edge &rhs) {
  return !(lhs == rhs);
}

//------------------------------------------------------------------------------
// Adjacency List Local Graph
//------------------------------------------------------------------------------
StagInt stag::AdjacencyListLocalGraph::goto_next_content_line() {
  std::string current_line;

  // Read the current line, discarding it. This leaves the file pointer at the
  // beginning of a line.
  std::streampos current_loc = is_.tellg();
  if (current_loc != 0) stag::safeGetline(is_, current_line);

  current_loc = is_.tellg();
  while (true) {
    // If the current position is the end of the file, we have failed to find
    // a content line. Return -1.
    if (current_loc == end_of_file_) {
      return -1;
    }

    // Read until we find a non-empty line.
    // Make sure to set current_loc to the position just before calling getline.
    current_line.clear();
    while (current_line.empty()) {
      current_loc = is_.tellg();
      stag::safeGetline(is_, current_line);
    }

    // Check if this line is a valid content line.
    size_t split_pos = current_line.find(':');
    if (split_pos != std::string::npos) {
      std::string token = current_line.substr(0, split_pos);
      StagInt source_node_id = std::stoi(token);

      // We found a content line, reset the position of the reader to the start
      // of the line and return the node id.
      is_.seekg(current_loc);
      return source_node_id;
    }
  }

  // If we couldn't find a content line, then the adjacencylist is badly formed.
  throw std::runtime_error("Malformed adjacencylist file.");
}

stag::AdjacencyListLocalGraph::AdjacencyListLocalGraph(const std::string &filename) {
  // Open the file handle to the graph on disk, and get the maximum length of the
  // file.
  is_ = std::ifstream(filename);

  // If the file could not be opened, throw an exception
  if (!is_.is_open()) {
    throw std::runtime_error(std::strerror(errno));
  }

  // Get the length of the file in bytes.
  is_.seekg(0, std::ios::end);
  end_of_file_ = is_.tellg();
}

void stag::AdjacencyListLocalGraph::find_vertex(StagInt v) {
  // Set the maximum and minimum ranges of the file to search
  std::streampos range_min = 0;
  std::streampos range_max = end_of_file_;

  // Perform a binary search for the target node
  StagInt current_id;
  bool found_target = false;
  while (!found_target) {
    // If min is greater than max, then we have failed to find our target point
    if (range_min > range_max) throw std::runtime_error("Couldn't find node in adjacencylist file.");

    // Search half-way between the search points.
    StagInt search_point = floor((range_max + range_min) / 2);

    // Check whether this point has been searched before
    if (fileloc_to_node_id_.find(search_point) != fileloc_to_node_id_.end()) {
      // We have searched this point before
      current_id = fileloc_to_node_id_[search_point];

      // If this is the point we're looking for, make sure that the file pointer
      // is pointing to the right place.
      if (current_id == v) {
        is_.seekg((std::streampos) search_point);
        goto_next_content_line();
      }
    } else {
      // We have never searched this point before - we need to check the
      // file on disk.
      is_.seekg((std::streampos) search_point);
      current_id = goto_next_content_line();
      fileloc_to_node_id_[search_point] = current_id;
    }

    if (current_id == v) {
      found_target = true;
    } else if (current_id == -1 || current_id > v) {
      range_max = search_point - std::streamoff(1);
    } else {
      range_min = search_point + std::streamoff(1);
    }
  }
}

std::vector<stag::edge> stag::AdjacencyListLocalGraph::neighbors(StagInt v) {
  // If we have searched for this vertex before, just returned the cached copy.
  if (node_id_to_edgelist_.find(v) != node_id_to_edgelist_.end()) {
    return node_id_to_edgelist_[v];
  }

  // First, find the target vertex in the adjacencylist file.
  find_vertex(v);

  // We are pointing at the correct content line. Parse it to get the neighbours.
  std::string content_line;
  stag::safeGetline(is_, content_line);
  std::vector<stag::edge> neighbors;
  std::vector<stag::edge> edges = stag::parse_adjacencylist_content_line(
      content_line);

  // Update our internal edgelist.
  node_id_to_edgelist_[v] = edges;

  return edges;
}

std::vector<StagInt> stag::AdjacencyListLocalGraph::neighbors_unweighted(StagInt v) {
  auto edges = neighbors(v);
  std::vector<StagInt> unweighted_neighbors;
  for (stag::edge e : edges) {
    unweighted_neighbors.push_back(e.v2);
  }
  return unweighted_neighbors;
}

StagReal stag::AdjacencyListLocalGraph::degree(StagInt v) {
  auto edges = neighbors(v);
  StagReal deg = 0;
  for (stag::edge e : edges) {
    // Self-loops count twice towards the degree
    if (e.v2 == v) deg += 2 * e.weight;
    else deg += e.weight;
  }
  return deg;
}

StagInt stag::AdjacencyListLocalGraph::degree_unweighted(StagInt v) {
  auto edges = neighbors(v);
  return edges.size();
}

std::vector<StagReal> stag::AdjacencyListLocalGraph::degrees(std::vector<StagInt> vertices) {
  std::vector<StagReal> degs;
  for (auto v : vertices) {
    degs.push_back(degree(v));
  }
  return degs;
}

std::vector<StagInt> stag::AdjacencyListLocalGraph::degrees_unweighted(std::vector<StagInt> vertices) {
  std::vector<StagInt> degs;
  for (auto v : vertices) {
    degs.push_back(degree_unweighted(v));
  }
  return degs;
}

bool stag::AdjacencyListLocalGraph::vertex_exists(StagInt v) {
  try {
    find_vertex(v);
    return true;
  } catch (std::runtime_error& e) {
    return false;
  }
}

stag::AdjacencyListLocalGraph::~AdjacencyListLocalGraph() {
  is_.close();
}

//------------------------------------------------------------------------------
// Standard Graph Constructors
//------------------------------------------------------------------------------
stag::Graph stag::cycle_graph(StagInt n) {
  if (n < 2) throw std::invalid_argument("Number of vertices must be at least 2.");

  SprsMat adj_mat(n, n);
  std::vector<EdgeTriplet> non_zero_entries;
  for (StagInt i = 0; i < n; i++) {
    non_zero_entries.emplace_back(i, (i + n + 1) % n, 1);
    non_zero_entries.emplace_back(i, (i + n - 1) % n, 1);
  }
  adj_mat.setFromTriplets(non_zero_entries.begin(), non_zero_entries.end());
  return stag::Graph(adj_mat);
}

stag::Graph stag::complete_graph(StagInt n) {
  if (n < 2) throw std::invalid_argument("Number of vertices must be at least 2.");

  SprsMat adj_mat(n, n);
  std::vector<EdgeTriplet> non_zero_entries;
  for (StagInt i = 0; i < n; i++) {
    for (StagInt j = 0; j < n; j++) {
      if (i != j) {
        non_zero_entries.emplace_back(i, j, 1);
      }
    }
  }
  adj_mat.setFromTriplets(non_zero_entries.begin(), non_zero_entries.end());
  return stag::Graph(adj_mat);
}

stag::Graph stag::barbell_graph(StagInt n) {
  if (n < 2) throw std::invalid_argument("Number of vertices must be at least 2.");

  // Construct the non-zero entries in the complete blocks of the adjacency
  // matrix
  std::vector<EdgeTriplet> non_zero_entries;
  for (StagInt i = 0; i < n; i++) {
    for (StagInt j = 0; j < n; j++) {
      if (i != j) {
        non_zero_entries.emplace_back(i, j, 1);
        non_zero_entries.emplace_back(n + i, n + j, 1);
      }
    }
  }

  // Add a single edge to connect the complete graphs
  non_zero_entries.emplace_back(n - 1, n, 1);
  non_zero_entries.emplace_back(n, n - 1, 1);

  // Construct the final adjacency matrix
  SprsMat adj_mat(2 * n, 2 * n);
  adj_mat.setFromTriplets(non_zero_entries.begin(), non_zero_entries.end());
  return stag::Graph(adj_mat);
}

stag::Graph stag::star_graph(StagInt n) {
  if (n < 2) throw std::invalid_argument("Number of vertices must be at least 2.");

  // Construct the non-zero entries in the adjacency matrix
  std::vector<EdgeTriplet> non_zero_entries;
  for (StagInt i = 1; i < n; i++) {
    non_zero_entries.emplace_back(0, i, 1);
    non_zero_entries.emplace_back(i, 0, 1);
  }

  // Construct the final adjacency matrix
  SprsMat adj_mat(n, n);
  adj_mat.setFromTriplets(non_zero_entries.begin(), non_zero_entries.end());
  return stag::Graph(adj_mat);
}

stag::Graph stag::identity_graph(StagInt n) {
  if (n < 1) throw std::invalid_argument("Number of vertices must be at least 1.");

  SprsMat adj_mat(n, n);
  adj_mat.setIdentity();
  return stag::Graph(adj_mat);
}

//------------------------------------------------------------------------------
// Other operators
//------------------------------------------------------------------------------
stag::Graph stag::operator+(const stag::Graph& lhs, const stag::Graph& rhs) {
  if (lhs.number_of_vertices() != rhs.number_of_vertices())
    throw std::invalid_argument("Number of vertices must match.");

  return stag::Graph(*lhs.adjacency() + *rhs.adjacency());
}