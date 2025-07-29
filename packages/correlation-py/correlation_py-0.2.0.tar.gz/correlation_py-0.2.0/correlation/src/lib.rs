use std::collections::HashMap;

use argmin::core::{CostFunction, Error, Executor, Gradient};
use argmin::solver::linesearch::MoreThuenteLineSearch;
use argmin::solver::quasinewton::LBFGS;
use itertools::Itertools;
use kahan::{KahanSum, KahanSummator};
use ndarray::{Array1, Array2};
use rayon::prelude::*;
use smallvec::SmallVec;

pub use io::{read_01_file, read_b8_file};

mod io;

/// Calculate the 2nd order correlation analytically.
///
/// # Arguments
///
/// * `detection_events` - A matrix of detection events with shape (num_shots, num_detectors).
///
/// * `detector_mask` - Boolean mask to mask certain detectors out. If the i-th element is true,
///   the i-th detector is masked out.
///
/// # Returns
///
/// A tuple of two elements. The first element is a vector of boundary correlations. The second
/// element is a matrix of edge correlations.
pub fn cal_2nd_order_correlation(detection_events: &Array2<f64>) -> (Array1<f64>, Array2<f64>) {
    let num_dets = detection_events.ncols();
    let mut correlation_edges = Array2::<f64>::zeros((num_dets, num_dets));
    let expect_ixj = cal_two_points_expects(detection_events);
    for i in 0..num_dets {
        let xi = expect_ixj[[i, i]];
        for j in 0..i {
            let xj = expect_ixj[[j, j]];
            let xij = expect_ixj[[i, j]];
            let denom = 1.0 - 2.0 * xi - 2.0 * xj + 4.0 * xij;
            let num = xij - xi * xj;
            let under_sqrt: f64 = 1.0 - 4.0 * num / denom;

            let pij = if under_sqrt > 0.0 {
                0.5 - 0.5 * under_sqrt.sqrt()
            } else {
                0.0
            };
            correlation_edges[[i, j]] = pij;
        }
    }
    correlation_edges += &correlation_edges.t().to_owned();

    let correlation_bdy = Array1::from_iter((0..num_dets).map(|i| {
        let xi = expect_ixj[[i, i]];
        let pi_sum = correlation_edges
            .row(i)
            .iter()
            .fold(0.0, |p, &q| p + q - 2.0 * p * q);
        (xi - pi_sum) / (1.0 - 2.0 * pi_sum)
    }));
    (correlation_bdy, correlation_edges)
}

fn cal_two_points_expects(detection_events: &Array2<f64>) -> Array2<f64> {
    let num_shots = detection_events.nrows() as f64;
    let expect_ixj = detection_events.t().dot(detection_events);
    expect_ixj / num_shots
}

pub type HyperEdge = SmallVec<[usize; 4]>;

type Cluster = Vec<usize>;

/// Calculate the high order correlations.
///
/// # Arguments
///
/// * `detection_events` - A matrix of detection events with shape (num_shots, num_detectors).
///
/// * `hyperedges` - A list of hyperedges. Each hyperedge is a list of detectors.
///
/// * `num_threads` - Number of threads to use in parallel, default to number of cpus.
///
/// * `max_iters` - Number of iterations the optimizer can take.
///
/// # Returns
///
/// A map from hyperedges to their correlation probabilities.
pub fn cal_high_order_correlations(
    detection_events: &Array2<f64>,
    hyperedges: Option<&[Vec<usize>]>,
    num_threads: Option<usize>,
    max_iters: Option<u64>,
) -> Result<HashMap<HyperEdge, f64>, Error> {
    let num_detectors = detection_events.ncols();
    let all_hyperedges = all_hyperedges_considered(num_detectors, hyperedges);
    // divide the hyperedges into clusters
    let (extended_hyperedges, clusters) = cluster_hyperedges(&all_hyperedges);
    // calculate the expectations of each hyperedge
    let expectations = calculate_expectations(detection_events, &extended_hyperedges);
    // precomputed intersections per superset
    let precomputed_intersections = clusters
        .iter()
        .map(|c| (c.len() as f32 + 1.0).log2() as usize)
        .unique()
        .map(|s| (s, precompute_intersections_per_superset(s)))
        .collect::<HashMap<_, _>>();
    // thread pool to use
    let pool = create_thread_pool(num_threads.unwrap_or(num_cpus::get()));
    // solve each cluster in parallel
    let solved_probs = pool.install(|| {
        clusters
            .par_iter()
            .with_max_len(1)
            .map(|cluster| {
                solve_cluster(
                    cluster,
                    &extended_hyperedges,
                    &expectations,
                    max_iters,
                    &precomputed_intersections,
                )
            })
            .collect::<Result<Vec<_>, Error>>()
    })?;
    // adjust probabilities
    let mut adjusted_probs = adjust_probabilities(&clusters, &extended_hyperedges, &solved_probs);
    // retain concerned hyperedges
    adjusted_probs.retain(|h, _| all_hyperedges.contains(h));
    Ok(adjusted_probs)
}

fn all_hyperedges_considered(
    num_detectors: usize,
    hyperedges: Option<&[Vec<usize>]>,
) -> Vec<HyperEdge> {
    let mut all_hyperedges: Vec<HyperEdge> = Vec::new();
    if let Some(hyperedges) = hyperedges {
        all_hyperedges.extend(hyperedges.iter().map(|e| {
            let mut hyperedge = HyperEdge::from_iter(e.clone());
            hyperedge.sort();
            hyperedge
        }));
    } else {
        all_hyperedges.extend((0..num_detectors).map(|e| HyperEdge::from_iter(std::iter::once(e))));
        all_hyperedges.extend(
            (0..num_detectors)
                .combinations(2)
                .map(|e| e.into_iter().collect()),
        );
    }
    all_hyperedges.sort_by_key(|h| h.len());
    all_hyperedges
}

fn create_thread_pool(num_threads: usize) -> rayon::ThreadPool {
    rayon::ThreadPoolBuilder::new()
        .num_threads(num_threads)
        .build()
        .unwrap()
}

fn cluster_hyperedges(hyperedges: &Vec<HyperEdge>) -> (Vec<HyperEdge>, Vec<Cluster>) {
    let mut extended_hyperedges = hyperedges.clone();
    let mut clusters = Vec::new();
    let mut indices_wait_cluster = (0..hyperedges.len()).collect_vec();
    while let Some(i) = indices_wait_cluster.pop() {
        let root = &hyperedges[i];
        let cluster = (1..=root.len())
            .flat_map(move |k| {
                root.clone()
                    .into_iter()
                    .combinations(k)
                    .map(|c| c.into_iter().collect::<HyperEdge>())
            })
            .map(|h| {
                if let Some(idx) = extended_hyperedges.iter().position(|e| *e == h) {
                    idx
                } else {
                    extended_hyperedges.push(h);
                    extended_hyperedges.len() - 1
                }
            })
            .collect_vec();
        indices_wait_cluster.retain(|j| !cluster.contains(j));
        clusters.push(cluster);
    }
    (extended_hyperedges, clusters)
}

fn calculate_expectations(
    detection_events: &Array2<f64>,
    extended_hyperedges: &[HyperEdge],
) -> Vec<f64> {
    let shape = detection_events.shape();
    let num_shots = shape[0];
    let num_detectors = shape[1];
    // pre-calculate 2-point expectations using
    // matrix multiply to reduce overhead
    let expect_ixj = cal_two_points_expects(detection_events);
    let mut expectations =
        Vec::from_iter(extended_hyperedges.iter().take_while(|e| e.len() <= 2).map(
            |e| match e.len() {
                1 => expect_ixj[(e[0], e[0])],
                2 => expect_ixj[(e[0], e[1])],
                _ => {
                    unreachable!("unreachable!")
                }
            },
        ));
    // calculate the rest of the expectations
    // use a matrix with new data layout to reduce row-wise operation overhead
    let detection_events = Array2::from_shape_fn((num_detectors, num_shots), |(i, j)| {
        detection_events[[j, i]]
    });
    for hyperedge in extended_hyperedges.iter().skip_while(|e| e.len() <= 2) {
        expectations.push(
            hyperedge
                .iter()
                .fold(Array1::from_elem(num_shots, 1.0), |acc, &det| {
                    acc * detection_events.row(det)
                })
                .mean()
                .unwrap(),
        );
    }
    expectations
}

type IntersectionsMap = HashMap<usize, Vec<SplitIntersection>>;

fn precompute_intersections_per_superset(size: usize) -> IntersectionsMap {
    let root = HyperEdge::from_iter(0..size);
    let hyperedges = powerset(&root)
        .into_iter()
        .map(HyperEdge::from_iter)
        .collect_vec();
    let mut intersections = HashMap::with_capacity(hyperedges.len());
    let mut supersets = HashMap::with_capacity(hyperedges.len());
    for (index, hyperedge) in hyperedges.iter().enumerate() {
        let intersect = intersects(&hyperedges, index);
        let superset = powerset(&intersect)
            .into_iter()
            .filter(|set| {
                let sym_diff = symmetric_difference(set, &hyperedges).collect_vec();
                hyperedge.iter().all(|i| sym_diff.contains(i))
            })
            .collect_vec();
        intersections.insert(index, intersect);
        supersets.insert(index, superset);
    }

    let mut intersections_per_superset = HashMap::new();

    for index in 0..hyperedges.len() {
        let intersection = &intersections[&index];
        let superset = &supersets[&index];

        let data = superset
            .iter()
            .map(|select| {
                // First list all intersection Hyperedges that are part of this superset
                let mut v = intersection
                    .iter()
                    .cloned()
                    .filter(|i| select.contains(i))
                    .collect_vec();

                // Record the location of the changeover
                let start_of_nonincluded = v.len();

                // Second list all intersection Hyperedges that are NOT part of this superset
                v.extend(
                    intersection
                        .iter()
                        .cloned()
                        .filter(|i| !select.contains(i))
                        .collect_vec(),
                );

                SplitIntersection {
                    intersection: v,
                    start_of_nonincluded,
                }
            })
            .collect_vec();

        intersections_per_superset.insert(index, data);
    }

    intersections_per_superset
}

struct ClusterSolver<'a> {
    hyperedges: Vec<HyperEdge>,
    expectations: Vec<f64>,

    /// The key is the target Hyperedge.
    ///
    /// For each "select" set in the SuperSet of the target we store the intersection set for the target, split by whether they are included the the "select" set.
    /// For a given HyperEdge index, we store the intersection list in two parts, with the start of the second half marked with the usize in the tuple.
    /// The first part contains the indicies of intersection hyperedges that where also part of the superset, the second half contains those that where not part of it.
    /// Doing this during problem setup allows to avoid many "contains" search loops during iterations.
    intersections_per_superset: &'a IntersectionsMap,
}

struct SplitIntersection {
    intersection: Vec<usize>,
    start_of_nonincluded: usize,
}

impl SplitIntersection {
    #[inline]
    fn prob_within_cluster(&self, param: &[f64], skip: Option<usize>) -> f64 {
        // let mut prob = 1.0;
        // for &s in self.included().iter() {
        //     if skip.map(|skip| s != skip).unwrap_or(true) {
        //         prob *= param[s];
        //     }
        // }

        // for &ns in self.nonincluded().iter() {
        //     if skip.map(|skip| ns != skip).unwrap_or(true) {
        //         prob *= 1.0 - param[ns];
        //     }
        // }
        self.prob_within_cluster_included(param, skip)
            * self.prob_within_cluster_nonincluded(param, skip)
    }

    #[inline]
    fn prob_within_cluster_included(&self, param: &[f64], skip: Option<usize>) -> f64 {
        let mut prob = 1.0;
        for &s in self.included().iter() {
            if skip.map(|skip| s != skip).unwrap_or(true) {
                prob *= param[s];
            }
        }
        prob
    }

    #[inline]
    fn prob_within_cluster_nonincluded(&self, param: &[f64], skip: Option<usize>) -> f64 {
        let mut prob = 1.0;
        for &ns in self.nonincluded().iter() {
            if skip.map(|skip| ns != skip).unwrap_or(true) {
                prob *= 1.0 - param[ns];
            }
        }
        prob
    }

    fn included(&self) -> &[usize] {
        &self.intersection[..self.start_of_nonincluded]
    }

    fn nonincluded(&self) -> &[usize] {
        &self.intersection[self.start_of_nonincluded..]
    }
}

impl<'a> ClusterSolver<'a> {
    fn new(
        cluster: &Cluster,
        all_hyperedges: &[HyperEdge],
        expectations: &[f64],
        precomputed_intersections: &'a HashMap<usize, IntersectionsMap>,
    ) -> Self {
        let hyperedges = cluster
            .iter()
            .map(|&i| all_hyperedges[i].clone())
            .collect_vec();
        let expectations = cluster.iter().map(|&i| expectations[i]).collect_vec();
        let size = all_hyperedges[*cluster.last().unwrap()].len();
        let intersections_per_superset = precomputed_intersections.get(&size).unwrap();
        Self {
            hyperedges,
            expectations,
            intersections_per_superset,
        }
    }
}

#[inline]
fn equation_lhs(hyperedge_index: usize, param: &[f64], cluster: &ClusterSolver) -> KahanSum<f64> {
    cluster.intersections_per_superset[&hyperedge_index]
        .iter()
        .map(|intersection| intersection.prob_within_cluster(param, None))
        .kahan_sum()
}

fn sum_squared_residuals(param: &[f64], cluster: &ClusterSolver) -> KahanSum<f64> {
    debug_assert_eq!(param.len(), cluster.hyperedges.len());
    (0..cluster.hyperedges.len())
        .zip(cluster.expectations.iter())
        .fold(KahanSum::new(), |acc, (i, &expect)| {
            let residual = equation_lhs(i, param, cluster) + (-expect);
            // low accuracy: acc + residual.sum() * residual.sum()
            // full accuracy: ((KahanSum::new_with_value(residual.err() * residual.err()) + 2.0 * residual.sum() * residual.err()) + residual.sum() * residual.sum()) + acc
            // good enough:
            (KahanSum::new_with_value(2.0 * residual.sum() * residual.err())
                + residual.sum() * residual.sum())
                + acc
        })
}

#[allow(dead_code)]
fn analytical_gradient(param: &[f64], cluster: &ClusterSolver) -> Array1<f64> {
    let mut gradients = vec![KahanSum::new(); cluster.hyperedges.len()];

    for (hyperedge_index, &expect) in (0..cluster.hyperedges.len()).zip(&cluster.expectations) {
        let equation_diff = 2.0 * (equation_lhs(hyperedge_index, param, cluster) + (-expect)).sum();
        for intersection in &cluster.intersections_per_superset[&hyperedge_index] {
            // In the next loops the gradient calculations change depending on what element is being skipped.
            // The probability is calculated in two halves, we can precompute each half assuming that no elements are skipped in it.
            // In each iteration we know whether the item is included or no so we can pair each half of the probability calculation.
            let noskip_included =
                intersection.prob_within_cluster_included(param, None) * equation_diff;
            let noskip_nonincluded =
                intersection.prob_within_cluster_nonincluded(param, None) * equation_diff;

            for &s in intersection.included() {
                gradients[s] +=
                    noskip_nonincluded * intersection.prob_within_cluster_included(param, Some(s));
            }

            for &ns in intersection.nonincluded() {
                gradients[ns] += (-noskip_included)
                    * intersection.prob_within_cluster_nonincluded(param, Some(ns));
            }
        }
    }

    Array1::from_iter(gradients.iter().map(KahanSum::sum))
}

#[allow(dead_code)]
fn analytical_gradient_relative_error(
    param: &Array1<f64>,
    cluster: &ClusterSolver,
    step_size: f64,
) -> f64 {
    let grad = analytical_gradient(param.as_slice().unwrap(), cluster);
    let cost_0 = sum_squared_residuals(param.as_slice().unwrap(), cluster);
    let grad_norm = grad.dot(&grad).sqrt();

    let step_vector1 = grad.clone() * (step_size / grad_norm);

    let param_1 = step_vector1 + param;

    let cost_1 = sum_squared_residuals(param_1.as_slice().unwrap(), cluster);

    let expected_change = step_size * grad_norm;

    let actual_change = cost_1.sum() - cost_0.sum();

    (expected_change - actual_change).abs() / expected_change.max(actual_change)
}

impl CostFunction for ClusterSolver<'_> {
    type Param = Array1<f64>;
    type Output = f64;

    fn cost(&self, param: &Self::Param) -> Result<Self::Output, Error> {
        // let start = Instant::now();
        let res = sum_squared_residuals(param.as_slice().unwrap(), self).sum();

        // let re1 = analytical_gradient_relative_error(param, self, 1e-5);
        // let re2 = analytical_gradient_relative_error(param, self, -1e-5);

        // let elapsed = start.elapsed().as_micros();
        // println!("{res}\t{elapsed}us");

        Ok(res)
    }
}

impl Gradient for ClusterSolver<'_> {
    type Param = Array1<f64>;
    type Gradient = Array1<f64>;
    fn gradient(&self, param: &Self::Param) -> Result<Self::Gradient, Error> {
        cfg_if::cfg_if! {
            if #[cfg(feature = "finite-diff")] {
                use finitediff::FiniteDiff;
                Ok((*param).forward_diff(&|x| sum_squared_residuals(x.as_slice().unwrap(), self)))
            } else {
                // let start = Instant::now();
                let grad = analytical_gradient(param.as_slice().unwrap(), self);
                // let elapsed = start.elapsed().as_micros();
                // println!("\t{elapsed}us");
                Ok(grad)
            }
        }
    }
}

fn solve_cluster(
    cluster: &Cluster,
    all_hyperedges: &[HyperEdge],
    expectations: &[f64],
    max_iters: Option<u64>,
    precomputed_intersections: &HashMap<usize, IntersectionsMap>,
) -> Result<Vec<f64>, Error> {
    let problem = ClusterSolver::new(
        cluster,
        all_hyperedges,
        expectations,
        precomputed_intersections,
    );
    let n_params = cluster.len();
    let init_param: Array1<f64> = Array1::from_elem(n_params, 1.0 / n_params as f64);

    let linesearch = MoreThuenteLineSearch::new();

    // let beta_method = PolakRibiere::new();
    // let solver = NonlinearConjugateGradient::new(linesearch, beta_method)
    //     .restart_iters(100)
    //     .restart_orthogonality(0.1);

    let solver = LBFGS::new(linesearch, 15);

    // FINE TUNE OF THE SOLVER PARAMS IS NEEDED
    let res = Executor::new(problem, solver)
        .configure(|state| {
            state
                .param(init_param)
                .max_iters(max_iters.unwrap_or(20 * n_params as u64))
                .target_cost(1e-12) //1e-6
        })
        .run()?;
    Ok(res.state.best_param.unwrap().into_iter().collect_vec())
}

fn adjust_probabilities(
    clusters: &[Cluster],
    all_hyperedges: &[HyperEdge],
    solved_probs: &[Vec<f64>],
) -> HashMap<HyperEdge, f64> {
    let mut adjusted_probs = HashMap::with_capacity(all_hyperedges.len());
    // cache for lengths
    let hyperedge_lengths: Vec<usize> = all_hyperedges.iter().map(|h| h.len()).collect();
    // Insert largest hyperedges directly without adjustment
    for (cluster, probs) in clusters.iter().zip(solved_probs) {
        let i = *cluster.last().unwrap();
        adjusted_probs.insert(all_hyperedges[i].clone(), *probs.last().unwrap());
    }

    let mut weight_to_adjust = all_hyperedges[*clusters[0].last().unwrap()].len() - 1;
    while weight_to_adjust > 0 {
        let mut collected_probs = HashMap::new();
        // adjust the probability of hyperedges with weight
        // weight_to_adjust in each clusters by the probability
        // of the hyperedges with weight greater than that
        for (cluster, probs) in clusters
            .iter()
            .zip(solved_probs)
            .filter(|&(cluster, _)| hyperedge_lengths[*cluster.last().unwrap()] > weight_to_adjust)
        {
            for (&hyperedge_i, &prob_this) in cluster
                .iter()
                .zip(probs)
                .filter(|&(i, _)| hyperedge_lengths[*i] == weight_to_adjust)
            {
                let hyperedge = &all_hyperedges[hyperedge_i];
                let adjusted_prob = adjusted_probs
                    .iter()
                    .filter_map(|(h, &p)| {
                        if hyperedge.iter().any(|i| !h.contains(i)) {
                            return None;
                        }
                        let i = *cluster.last().unwrap();
                        let max_h = &all_hyperedges[i];
                        assert!(hyperedge.iter().all(|e| max_h.contains(e)));
                        let num_intersect = max_h.iter().filter(|&e| h.contains(e)).count();
                        if num_intersect != weight_to_adjust {
                            return None;
                        }
                        Some(p)
                    })
                    .fold(prob_this, |p, q| (p - q) / (1.0 - 2.0 * q));
                collected_probs
                    .entry(hyperedge)
                    .or_insert_with(Vec::new)
                    .push(adjusted_prob);
            }
        }
        // average the probabilities of the same hyperedge in different clusters
        for (h, probs) in collected_probs {
            let prob = probs.iter().sum::<f64>() / probs.len() as f64;
            adjusted_probs.insert(h.clone(), prob);
        }
        weight_to_adjust -= 1;
    }
    adjusted_probs
}

#[inline]
fn powerset(hyperedge_indicies: &[usize]) -> Vec<Vec<usize>> {
    (1..=hyperedge_indicies.len())
        .flat_map(move |k| hyperedge_indicies.iter().cloned().combinations(k))
        .collect_vec()
}

/// Returns the indicies of all HyperEdges which have a component in common with the target HyperEdge
#[inline]
fn intersects(hyperedges: &[HyperEdge], target_index: usize) -> Vec<usize> {
    let target = &hyperedges[target_index];
    hyperedges
        .iter()
        .enumerate()
        .filter(|(_, h)| h.iter().any(|&e| target.contains(&e)))
        .map(|(i, _h)| i)
        .collect_vec()
}

#[inline]
fn symmetric_difference(
    hyperedge_indicies: &[usize],
    hyperedges: &[HyperEdge],
) -> impl Iterator<Item = usize> {
    let mut counts = HashMap::new();
    for &index in hyperedge_indicies {
        for &e in &hyperedges[index] {
            *counts.entry(e).or_insert(0) += 1;
        }
    }
    counts
        .into_iter()
        .filter_map(|(e, c)| if c % 2 == 1 { Some(e) } else { None })
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;

    #[test]
    fn test_symmetric_difference1() {
        let hyper_edges = [
            HyperEdge::from_slice(&[0, 1, 2]),
            HyperEdge::from_slice(&[1, 2, 3]),
        ];
        let set_indicies = [0, 1];
        assert_eq!(
            symmetric_difference(&set_indicies, &hyper_edges).collect::<HashSet<usize>>(),
            HashSet::from_iter([0, 3].into_iter())
        );
    }

    #[test]
    fn test_symmetric_difference2() {
        let hyperedges = [
            HyperEdge::from_slice(&[0, 1, 2]),
            HyperEdge::from_slice(&[1, 2, 3]),
            HyperEdge::from_slice(&[2, 3, 4]),
        ];
        let set_indicies = [0, 1, 2];

        assert_eq!(
            symmetric_difference(&set_indicies, &hyperedges).collect::<HashSet<usize>>(),
            HashSet::from_iter([0, 2, 4].into_iter())
        )
    }
}
