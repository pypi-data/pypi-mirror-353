use std::cmp::Ordering;
use std::collections::HashMap;
use std::sync::Arc;

use ontolius::ontology::HierarchyQueries;
use ontolius::{Identified, TermId};
use phenotypes::Observable;

use super::SimilarityMeasure;

pub struct PrecomputedIcMicaSimilarityMeasure<O> {
    hpo: Arc<O>,
    mica_dict: Arc<HashMap<TermId, HashMap<TermId, f64>>>,
    ic_dict: HashMap<TermId, f64>,
}

impl<O> PrecomputedIcMicaSimilarityMeasure<O> {
    pub fn new(mica_dict: Arc<HashMap<TermId, HashMap<TermId, f64>>>, hpo: Arc<O>) -> Self {
        let mut ic_dict = HashMap::with_capacity(mica_dict.len());
        for (term_id, v) in mica_dict.iter() {
            if let Some(ic) = v.get(term_id) {
                ic_dict.insert(Clone::clone(term_id), *ic);
            }
        }
        ic_dict.shrink_to_fit();

        PrecomputedIcMicaSimilarityMeasure {
            hpo,
            mica_dict,
            ic_dict,
        }
    }
}

impl<O, A> SimilarityMeasure<A> for PrecomputedIcMicaSimilarityMeasure<O>
where
    O: HierarchyQueries,
    A: Identified + Observable,
{
    type Value = f64;

    fn compute_similarity(&self, a: &A, b: &A) -> anyhow::Result<Self::Value> {
        // This similarity measure only works for present/observed terms.
        if a.is_present() && b.is_present() {
            Ok(compute_present(&self.mica_dict, a, b))
        } else if a.is_excluded() && b.is_excluded() {
            Ok(compute_excluded(self.hpo.as_ref(), &self.ic_dict, a, b))
        } else {
            // Cannot compute similarity between present and excluded terms.
            anyhow::bail!("Cannot compute similarity between present and excluded feature")
        }
    }

    fn is_symmetric(&self) -> bool {
        true
    }
}

pub(crate) fn compute_present<A, D>(mica_dict: D, a: &A, b: &A) -> f64
where
    A: Identified,
    D: AsRef<HashMap<TermId, HashMap<TermId, f64>>>,
{
    // Assume both phenotypic features are present.
    let (leq, gt) = match a.identifier().cmp(b.identifier()) {
        Ordering::Less | Ordering::Equal => (a, b),
        Ordering::Greater => (b, a),
    };
    if let Some(va) = mica_dict.as_ref().get(leq.identifier()) {
        if let Some(val) = va.get(gt.identifier()) {
            return *val;
        }
    }
    0.
}

pub(crate) fn compute_excluded<Q, A>(hpo: &Q, ic_dict: &HashMap<TermId, f64>, a: &A, b: &A) -> f64
where
    Q: HierarchyQueries,
    A: Identified,
{
    // Assume both phenotypic features are excluded.
    if let Some(chosen) = choose_priority_term_id(hpo, a, b) {
        ic_dict
            .get(chosen)
            .copied()
            .expect("Term should be in `ic_dict`")
    } else {
        0.
    }
}

pub(crate) fn choose_priority_term_id<'a, Q, A>(hpo: &Q, a: &'a A, b: &'a A) -> Option<&'a TermId>
where
    Q: HierarchyQueries,
    A: Identified,
{
    if hpo.is_equal_or_ancestor_of(b, a) {
        Some(b.identifier())
    } else if hpo.is_ancestor_of(a, b) {
        Some(a.identifier())
    } else {
        None
    }
}
