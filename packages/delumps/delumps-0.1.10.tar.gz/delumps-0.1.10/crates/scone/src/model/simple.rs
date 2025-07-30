use std::str::FromStr;

use ontolius::{Identified, TermId};
use phenotypes::Observable;

use super::SampleLabels;

#[derive(Clone, Debug, PartialEq, Eq, Hash)]
pub struct SimplePhenotypicFeature {
    term_id: TermId,
    is_present: bool,
}

impl SimplePhenotypicFeature {
    pub fn new(term_id: TermId, is_present: bool) -> Self {
        SimplePhenotypicFeature {
            term_id,
            is_present,
        }
    }
}

impl Identified for SimplePhenotypicFeature {
    fn identifier(&self) -> &TermId {
        &self.term_id
    }
}

impl Observable for SimplePhenotypicFeature {
    fn is_present(&self) -> bool {
        self.is_present
    }
}

/// Struct to represent the sample identifiers.
#[derive(Clone, PartialEq, Eq, Debug, Hash, PartialOrd, Ord)]
pub struct SimpleSampleLabels {
    label: String,
    meta_label: Option<String>,
}

impl SimpleSampleLabels {
    /// Create new sample labels from `label` and optional `meta_label`.
    ///
    /// The data that backs `label` and `meta_label` are copied.
    ///
    /// # Examples
    ///
    /// Create sample labels with both `label` and `meta_label`:
    /// ```
    /// use scone::model::SampleLabels;
    /// use scone::model::simple::SimpleSampleLabels;
    ///
    /// let labels = SimpleSampleLabels::new("III:A", Some("PMID:1234-FBN1"));
    ///
    /// assert_eq!(labels.label(), "III:A");
    /// assert_eq!(labels.meta_label(), Some("PMID:1234-FBN1"));
    /// ```
    ///
    ///
    /// Create sample labels with just `label`:
    /// ```
    /// use scone::model::SampleLabels;
    /// use scone::model::simple::SimpleSampleLabels;
    ///
    /// let labels = SimpleSampleLabels::new("III:A", None);
    ///
    /// assert_eq!(labels.label(), "III:A");
    /// assert_eq!(labels.meta_label(), None);
    /// ```
    pub fn new(label: impl AsRef<str>, meta_label: Option<&str>) -> Self {
        SimpleSampleLabels {
            label: label.as_ref().to_string(),
            meta_label: meta_label.map(|x| x.to_string()),
        }
    }
}

impl SampleLabels for SimpleSampleLabels {
    fn label(&self) -> &str {
        &self.label
    }

    fn meta_label(&self) -> Option<&str> {
        self.meta_label.as_deref()
    }
}

/// Create `SimpleSampleLabels` from a tuple with label and metalabel.
///
/// # Examples
///
/// ```
/// use scone::model::SampleLabels;
/// use scone::model::simple::SimpleSampleLabels;
///
/// let labels = SimpleSampleLabels::from(("III:A", "PMID:1234-FBN1"));
///
/// assert_eq!(labels.label(), "III:A");
/// assert_eq!(labels.meta_label(), Some("PMID:1234-FBN1"));
/// ```
impl From<(&str, &str)> for SimpleSampleLabels {
    fn from(value: (&str, &str)) -> Self {
        SimpleSampleLabels {
            label: value.0.into(),
            meta_label: Some(value.1.into()),
        }
    }
}

/// Create `SampleLabels` from a string slice with label.
/// The metalabel will not be set.
///
/// # Examples
///
/// ```
/// use scone::model::SampleLabels;
/// use scone::model::simple::SimpleSampleLabels;
///
/// let labels = SimpleSampleLabels::from("III:A");
///
/// assert_eq!(labels.label(), "III:A");
/// assert_eq!(labels.meta_label(), None);
/// ```
impl<'a> From<&'a str> for SimpleSampleLabels {
    fn from(value: &'a str) -> Self {
        SimpleSampleLabels {
            label: value.to_owned(),
            meta_label: None,
        }
    }
}

/// Create `SampleLabels` from a label, while omitting the metalabel.
///
/// # Examples
///
/// ```
/// use std::str::FromStr;
/// use scone::model::SampleLabels;
/// use scone::model::simple::SimpleSampleLabels;
///
/// let labels = SimpleSampleLabels::from_str("III:A").unwrap();
///
/// assert_eq!(labels.label(), "III:A");
/// assert_eq!(labels.meta_label(), None);
/// ```
impl FromStr for SimpleSampleLabels {
    type Err = ();

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        Ok(SimpleSampleLabels {
            label: s.into(),
            meta_label: None,
        })
    }
}
