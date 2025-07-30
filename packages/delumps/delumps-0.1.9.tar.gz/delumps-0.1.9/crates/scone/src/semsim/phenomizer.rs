use std::{collections::HashMap, sync::Arc};

use ontolius::{Identified, TermId};
use phenotypes::Observable;

use super::{precalc::compute_present, util::compute_two_sided_similarity, SimilarityKernel};

/// Phenomizer semantic similarity measure.
pub struct Phenomizer {
    pub(crate) mica_dict: Arc<HashMap<TermId, HashMap<TermId, f64>>>,
}

impl From<Arc<HashMap<TermId, HashMap<TermId, f64>>>> for Phenomizer {
    fn from(value: Arc<HashMap<TermId, HashMap<TermId, f64>>>) -> Self {
        Phenomizer { mica_dict: value }
    }
}

fn compute_one_sided<M, A, D>(dict: D, source: M, target: M) -> Vec<f64>
where
    M: AsRef<[A]>,
    A: Identified + Observable,
    D: AsRef<HashMap<TermId, HashMap<TermId, f64>>>,
{
    let mut sim_measure_results = Vec::with_capacity(source.as_ref().len());

    for src_pf in source.as_ref() {
        if src_pf.is_present() {
            // Find the best match
            let similarity = target
                .as_ref()
                .iter()
                .filter(|&a| a.is_present())
                .map(|t_pf| compute_present(&dict, src_pf, t_pf))
                .max_by(|left, right| {
                    left.partial_cmp(right)
                        .expect("Compute present should always return a finite float")
                })
                .expect("Target should include at least one present feature");
            sim_measure_results.push(similarity);
        }
    }

    sim_measure_results
}

impl<M, A> SimilarityKernel<M, A> for Phenomizer
where
    M: AsRef<[A]>,
    A: Identified + Observable,
{
    type Value = f64;

    fn compute(&self, a: &M, b: &M) -> anyhow::Result<Self::Value> {
        let (a, b) = (a.as_ref(), b.as_ref());

        if a.iter().any(|ann| ann.is_present()) && b.iter().any(|ann| ann.is_present()) {
            // At least one term is present in both samples
            let a_to_b = compute_one_sided(&self.mica_dict, &a, &b);
            let b_to_a = compute_one_sided(&self.mica_dict, &b, &a);

            Ok(compute_two_sided_similarity(a_to_b, b_to_a))
        } else {
            Ok(0.)
        }
    }

    fn is_symmetric(&self) -> bool {
        true
    }
}

#[cfg(test)]
mod tests {
    use std::{collections::HashMap, sync::Arc};

    use ontolius::TermId;

    use crate::{model::simple::SimplePhenotypicFeature, semsim::SimilarityKernel};

    use super::Phenomizer;

    fn create_mica_dict() -> Arc<HashMap<TermId, HashMap<TermId, f64>>> {
        Arc::new(
            [
                (
                    "HP:1".parse().unwrap(),
                    vec![
                        ("HP:1".parse().unwrap(), 5.),
                        ("HP:2".parse().unwrap(), 1.),
                        ("HP:3".parse().unwrap(), 2.),
                        ("HP:4".parse().unwrap(), 3.),
                    ],
                ),
                (
                    "HP:2".parse().unwrap(),
                    vec![
                        ("HP:2".parse().unwrap(), 2.),
                        ("HP:3".parse().unwrap(), 10.),
                        ("HP:4".parse().unwrap(), 20.),
                    ],
                ),
                (
                    "HP:3".parse().unwrap(),
                    vec![
                        ("HP:3".parse().unwrap(), 8.),
                        ("HP:4".parse().unwrap(), 30.),
                    ],
                ),
            ]
            .into_iter()
            .map(|(key, val)| (key, val.into_iter().collect()))
            .collect(),
        )
    }

    macro_rules! test_semantic_similarity {
        ($($phenomizer: expr, $a: expr, $b: expr, $expected: expr)?) => {
            $(
                let a: Vec<_> = $a
                .into_iter()
                .map(|(curie, is_present)| {
                    SimplePhenotypicFeature::new(curie.parse().unwrap(), is_present)
                })
                .collect();
            let b = $b
                .into_iter()
                .map(|(curie, is_present)| {
                    SimplePhenotypicFeature::new(curie.parse().unwrap(), is_present)
                })
                .collect();

            let similarity = $phenomizer.compute(&a, &b).expect("Value should be present");

            assert_eq!(similarity, $expected);

            )?
        };
    }

    #[test]
    fn compute() {
        let phenomizer = Phenomizer {
            mica_dict: create_mica_dict(),
        };

        test_semantic_similarity! {
            &phenomizer,
            [("HP:1", true), ("HP:3", true),],
            [("HP:1", false), ("HP:3", true),],
            6.5
        };
        test_semantic_similarity! {
            &phenomizer,
            [("HP:1", true)],
            [("HP:2", true), ("HP:3", true)],
            1.75
        };
        test_semantic_similarity!(&phenomizer, [("HP:1", true)], [("HP:1", false)], 0.);
        test_semantic_similarity!(&phenomizer, [("HP:1", false)], [("HP:1", false)], 0.);
    }
}
