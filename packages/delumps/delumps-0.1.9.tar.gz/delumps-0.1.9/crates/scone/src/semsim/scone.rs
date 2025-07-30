use std::sync::Arc;

use anyhow::Result;
use ontolius::{ontology::HierarchyQueries, Identified};

use phenotypes::{Observable, ObservableFeatures};

use super::{
    util::compute_two_sided_similarity, SimilarityKernel, SimilarityMeasure, SimilarityMeasureValue,
};

/// Strategy for resolving a conflict between a present HPO term (e.g. *Clonic seizure*) in subject *A*
/// and its excluded ancestor (e.g. no *Seizure*) in subject *B*.
#[derive(Clone, Copy, PartialEq, Eq, Debug, Hash)]
pub enum ExcludedAncestorStrategy {
    /// No explicit penalty. However, the excluded `ancestor` will contribute nothing to the match.
    Skip,
    // Apply a simple penalty: consider the excluded `ancestor` as a mismatch using the negated IC
    // of the excluded ancestor.
    Penalize,
}

#[derive(Clone, Debug, PartialEq, Eq)]
pub struct SconeConfig {
    pub excluded_ancestor_strategy: ExcludedAncestorStrategy,
    pub skip_matching_excluded_features: bool,
}

/// Use [`ExcludedAncestorStrategy::Skip`] and `skip_matching_excluded_features==false`.
impl Default for SconeConfig {
    fn default() -> Self {
        Self {
            excluded_ancestor_strategy: ExcludedAncestorStrategy::Skip,
            skip_matching_excluded_features: false,
        }
    }
}

pub struct SconeSimilarityKernel<O, SM> {
    hpo: Arc<O>,
    similarity_measure: SM,
    config: SconeConfig,
}

// Creation
impl<O, SM> SconeSimilarityKernel<O, SM> {
    pub fn new(hpo: Arc<O>, similarity_measure: SM, config: SconeConfig) -> Self {
        SconeSimilarityKernel {
            hpo,
            similarity_measure,
            config,
        }
    }
}

fn compute_one_sided<O, SM, M, A>(
    hpo: &O,
    sm: &SM,
    config: &SconeConfig,
    source: M,
    target: M,
) -> Vec<SM::Value>
where
    O: HierarchyQueries,
    SM: SimilarityMeasure<A>,
    M: AsRef<[A]>,
    A: Identified + Observable,
{
    let mut sim_measure_results = Vec::with_capacity(source.as_ref().len());

    for src_pf in source.as_ref() {
        if src_pf.is_present() {
            if !present_match_is_eligible(hpo, src_pf, source.as_ref(), target.as_ref()) {
                /*
                We must not match `src_pf` to `target` since `source` has an excluded descendant of `src_pf`
                that is ancestor of one of observed features of the `target`.
                */
                sim_measure_results.push(SM::Value::zero());
                continue;
            }

            if let Some(excluded_ancestor) =
                find_excluded_ancestor(hpo, src_pf, target.as_ref().excluded_features())
            {
                /*
                BRANCH 1
                There was at least one excluded ancestor of `src_pf` in the target.
                 */
                if let Some(smr) = handle_excluded_ancestor(sm, config, excluded_ancestor) {
                    sim_measure_results.push(smr);
                }
            } else {
                /*
                There was no excluded ancestor in the target, so, we can do normal matching.
                Let's find the best match from the present terms - the regular Phenomizer.
                */
                let smr = target.as_ref().present_features()
                        .map(|pf| {
                            sm
                                .compute_similarity(src_pf, pf)
                                .expect("Computing similarity between present features should never fail")
                        })
                        .max_by(|left, right| {
                            left.similarity()
                                .partial_cmp(&right.similarity())
                                .expect("Ordering should never fail since the similarity should never be non-finite!")
                        })
                        .unwrap_or(SM::Value::zero());

                sim_measure_results.push(smr);
            }
        } else {
            if !excluded_match_is_eligible(hpo, src_pf, source.as_ref(), target.as_ref()) {
                /*
                We must not match `src_pf_idx` to `target` since `source` has an observed ancestor of `src_pf_idx`
                that is descendant of one of excluded features of the `target`.
                */
                sim_measure_results.push(SM::Value::zero());
                continue;
            }

            let similarity = if find_observed_descendant(
                hpo,
                src_pf,
                target.as_ref().present_features(),
            )
            .is_some()
            {
                /*
                We found an observed descendant in the target's features.
                We handle the observed descendant in the same fashion as in BRANCH 1.
                */
                handle_excluded_ancestor(sm, config, src_pf)
            } else if config.skip_matching_excluded_features {
                None
            } else {
                target.as_ref()
                        .excluded_features()
                        .flat_map(|exf| sm.compute_similarity(src_pf, exf))
                        .max_by(|l, r| {
                            l.similarity()
                                .partial_cmp(&r.similarity())
                                .expect("Ordering should never fail since the similarity should never be non-finite!")
                        })
            };

            if let Some(sim) = similarity {
                sim_measure_results.push(sim)
            }
        }
    }

    sim_measure_results
}

fn handle_excluded_ancestor<SM, A>(sm: &SM, config: &SconeConfig, ancestor: &A) -> Option<SM::Value>
where
    SM: SimilarityMeasure<A>,
{
    match config.excluded_ancestor_strategy {
        ExcludedAncestorStrategy::Skip => None,
        ExcludedAncestorStrategy::Penalize => sm
            .compute_similarity(ancestor, ancestor)
            .map(SM::Value::negate)
            .ok(),
    }
}

/// Check the following conditions to determine if a present phenotypic feature `pf` is eligible for matching.
///
/// Let's explain this on an example.
/// Let `pf` be *Abnormality of liver*.
/// Then, if `source` is annotated with an excluded descendant of `pf`, such as *Abnormal liver morphology*
/// and the `target` is annotated with an observed exact match or a descendant,
/// such as *Abnormal liver morphology* or *Hepatosplenomegaly*,
/// then `pf` must not be matched with the target.
fn present_match_is_eligible<O, A>(hpo: &O, pf: &A, source: &[A], target: &[A]) -> bool
where
    O: HierarchyQueries,
    A: Identified + Observable,
{
    for src_exc in source.excluded_features() {
        if hpo.is_ancestor_of(pf, src_exc) {
            for t_obs_f in target.present_features() {
                if hpo.is_equal_or_ancestor_of(src_exc, t_obs_f) {
                    return false;
                }
            }
        }
    }
    true
}

/// Check the following conditions to determine if an *excluded* phenotypic feature `ef` is eligible for matching.
///
/// Let's explain this with an example.
/// Let `ef` be *Clonic seizure*. Then, if `source` is annotated with an observed ancestor of `ef`, such as *Seizure*
/// and the `target` is annotated with an excluded exact match or an ancestor, such as *Abnormality of nervous system*,
/// then `ef` must not be matched with the target.
fn excluded_match_is_eligible<O, A>(hpo: &O, ef: &A, source: &[A], target: &[A]) -> bool
where
    O: HierarchyQueries,
    A: Identified + Observable,
{
    for src_obs in source.present_features() {
        if hpo.is_ancestor_of(src_obs, ef) {
            for t_ex_f in target.excluded_features() {
                if hpo.is_equal_or_ancestor_of(t_ex_f, src_obs) {
                    return false;
                }
            }
        }
    }
    true
}

fn find_observed_descendant<'b, O, A, I>(
    hpo: &O,
    src_pf: &A,
    target_observed_indices: I,
) -> Option<&'b A>
where
    A: Identified + 'b,
    I: IntoIterator<Item = &'b A>,
    O: HierarchyQueries,
{
    target_observed_indices
        .into_iter()
        .find(|&pf| hpo.is_equal_or_ancestor_of(src_pf, pf))
}

fn find_excluded_ancestor<'b, O, A, I>(
    hpo: &O,
    src_pf: &A,
    target_excluded_features: I,
) -> Option<&'b A>
where
    O: HierarchyQueries,
    I: IntoIterator<Item = &'b A>,
    A: Identified + 'b,
{
    target_excluded_features
        .into_iter()
        .find(|&exf| hpo.is_equal_or_ancestor_of(exf, src_pf))
}

impl<O, SM, M, A> SimilarityKernel<M, A> for SconeSimilarityKernel<O, SM>
where
    O: HierarchyQueries,
    SM: SimilarityMeasure<A, Value = f64>,
    M: AsRef<[A]>,
    A: Identified + Observable,
{
    type Value = f64;

    fn compute(&self, a: &M, b: &M) -> Result<Self::Value> {
        let (a, b) = (a.as_ref(), b.as_ref());
        if a.is_empty() || b.is_empty() {
            return Ok(0.);
        }

        let a_to_b = compute_one_sided(
            self.hpo.as_ref(),
            &self.similarity_measure,
            &self.config,
            a,
            b,
        );
        let b_to_a = compute_one_sided(
            self.hpo.as_ref(),
            &self.similarity_measure,
            &self.config,
            b,
            a,
        );

        Ok(compute_two_sided_similarity(&a_to_b, &b_to_a))
    }

    fn is_symmetric(&self) -> bool {
        true
    }
}
