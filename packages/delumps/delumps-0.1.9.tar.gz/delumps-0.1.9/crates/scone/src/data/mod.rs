//! The `data` module includes fake and real-world samples for testing.

pub mod fbn1;

use crate::model::simple::{SimplePhenotypicFeature, SimpleSampleLabels};
use crate::model::Sample;

fn make_sample(
    label: &str,
    phenotypes: &[(&str, bool)],
) -> Sample<SimpleSampleLabels, SimplePhenotypicFeature> {
    Sample::new(
        label,
        phenotypes
            .iter()
            .map(|&(curie, is_present)| {
                SimplePhenotypicFeature::new(
                    curie.parse().expect("CURIE should be parsable"),
                    is_present,
                )
            })
            .collect::<Vec<_>>(),
    )
}
