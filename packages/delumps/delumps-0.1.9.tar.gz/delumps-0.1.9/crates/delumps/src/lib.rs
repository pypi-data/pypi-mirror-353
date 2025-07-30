use numpy::ndarray::Array2;
use ontolius::py::PyTermId;
use phenotypes::Observable;
use pyo3::prelude::*;
use scone::semsim::io::read_ic_mica_data;
use scone::semsim::precalc::PrecomputedIcMicaSimilarityMeasure;
use scone::semsim::scone::{SconeConfig, SconeSimilarityKernel};
use scone::semsim::smc::NDArraySimilarityMatrix;
use scone::semsim::SimilarityMatrixCreator as SconeSimilarityMatrixCreator;
use scone::semsim::{phenomizer::Phenomizer, smc::SequentialSimilarityMatrixCreator};

use std::collections::HashMap;
use std::sync::Arc;

use crate::io::load_hpo;
use numpy::{PyArray2, ToPyArray};
use ontolius::ontology::csr::MinimalCsrOntology;
use ontolius::{Identified, TermId};

mod io;

/// A module with Rust implementation of selected parts of the Delumps algorithm.
#[pymodule]
fn delumps(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<PhenotypicFeature>()?;
    m.add_class::<Sample>()?;

    m.add_class::<ExcludedAncestorStrategy>()?;
    m.add_class::<SimilarityMatrix>()?;
    m.add_class::<SimilarityMatrixCreator>()?;
    m.add_class::<SimilarityMatrixCreatorFactory>()?;
    Ok(())
}

#[pyclass]
#[derive(FromPyObject, Debug, PartialEq, Eq)]
pub struct PhenotypicFeature {
    identifier: PyTermId,
    is_present: bool,
}

#[pymethods]
impl PhenotypicFeature {
    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __repr__(&self) -> String {
        format!(
            "PhenotypicFeature(identifier='{}', is_present={})",
            self.identifier.identifier(),
            &self.is_present
        )
    }
}

impl Identified for PhenotypicFeature {
    fn identifier(&self) -> &TermId {
        &self.identifier
    }
}

impl Observable for PhenotypicFeature {
    fn is_present(&self) -> bool {
        self.is_present
    }
}

#[pyclass]
#[derive(FromPyObject, Debug, PartialEq, Eq)]
pub struct Sample {
    phenotypic_features: Vec<PhenotypicFeature>,
}

impl AsRef<[PhenotypicFeature]> for Sample {
    fn as_ref(&self) -> &[PhenotypicFeature] {
        &self.phenotypic_features
    }
}

#[pymethods]
impl Sample {
    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __repr__(&self) -> String {
        format!(
            "Sample(phenotypic_features={:?})",
            &self.phenotypic_features
        )
    }
}

#[derive(Clone, Debug)]
#[pyclass]
pub(crate) enum ExcludedAncestorStrategy {
    /// No explicit penalty. However, the excluded `ancestor` will contribute nothing to the match.
    Skip,
    // Apply a simple penalty: consider the excluded `ancestor` as a mismatch using the negated IC
    // of the excluded ancestor.
    Penalize,
}

impl From<ExcludedAncestorStrategy> for scone::semsim::scone::ExcludedAncestorStrategy {
    fn from(value: ExcludedAncestorStrategy) -> Self {
        match value {
            ExcludedAncestorStrategy::Skip => scone::semsim::scone::ExcludedAncestorStrategy::Skip,
            ExcludedAncestorStrategy::Penalize => {
                scone::semsim::scone::ExcludedAncestorStrategy::Penalize
            }
        }
    }
}

#[derive(Debug)]
#[pyclass]
pub(crate) struct SimilarityMatrix {
    similarity_matrix: Array2<f64>,
}

#[pymethods]
impl SimilarityMatrix {
    #[getter]
    fn similarity_matrix<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray2<f64>> {
        self.similarity_matrix.to_pyarray_bound(py)
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __repr__(&self) -> String {
        format!("SimilarityMatrix: {:?}", self.similarity_matrix.shape())
    }
}

#[pyclass]
pub(crate) struct SimilarityMatrixCreator {
    similarity_matrix_creator: Box<
        dyn SconeSimilarityMatrixCreator<
                Vec<Sample>,
                Sample,
                PhenotypicFeature,
                Matrix = NDArraySimilarityMatrix<f64>,
            > + Send,
    >,
}

#[pymethods]
impl SimilarityMatrixCreator {
    /// Compute semantic similarity matrix for a bunch of samples.
    fn calculate_matrix(&self, samples: Vec<Sample>) -> PyResult<SimilarityMatrix> {
        let similarity_matrix = self.similarity_matrix_creator.calculate_matrix(samples)?;
        Ok(SimilarityMatrix {
            similarity_matrix: similarity_matrix.array(),
        })
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __repr__(&self) -> String {
        "SimilarityMatrixCreator".to_owned()
    }
}

#[pyclass]
pub(crate) struct SimilarityMatrixCreatorFactory {
    hpo: Arc<MinimalCsrOntology>,
    ic_mica_dict: Arc<HashMap<TermId, HashMap<TermId, f64>>>,
}

#[pymethods]
impl SimilarityMatrixCreatorFactory {
    /// The static constructor of the factory.
    ///
    /// We need paths to HPO JSON file and to the table with IC MICA values.
    #[staticmethod]
    fn from_hpo_and_ic_mica(fpath_hpo: &str, fpath_ic_mica: &str) -> PyResult<Self> {
        let hpo = load_hpo(fpath_hpo)?;

        let ic_mica_dict = read_ic_mica_data(fpath_ic_mica).map(Arc::new)?;

        Ok(SimilarityMatrixCreatorFactory { hpo, ic_mica_dict })
    }

    fn create_phenomizer_smc(&self) -> SimilarityMatrixCreator {
        SimilarityMatrixCreator {
            similarity_matrix_creator: Box::new(SequentialSimilarityMatrixCreator::new(
                Phenomizer::from(Arc::clone(&self.ic_mica_dict)),
            )),
        }
    }

    #[pyo3(signature = (
                excluded_ancestor_strategy = ExcludedAncestorStrategy::Skip,
                skip_matching_excluded_features = false,
            ))]
    fn create_scone_smc(
        &self,
        excluded_ancestor_strategy: ExcludedAncestorStrategy,
        skip_matching_excluded_features: bool,
    ) -> SimilarityMatrixCreator {
        SimilarityMatrixCreator {
            similarity_matrix_creator: Box::new(SequentialSimilarityMatrixCreator::new(
                SconeSimilarityKernel::new(
                    Arc::clone(&self.hpo),
                    PrecomputedIcMicaSimilarityMeasure::new(
                        Arc::clone(&self.ic_mica_dict),
                        Arc::clone(&self.hpo),
                    ),
                    SconeConfig {
                        excluded_ancestor_strategy: excluded_ancestor_strategy.into(),
                        skip_matching_excluded_features,
                    },
                ),
            )),
        }
    }

    fn __str__(&self) -> String {
        self.__repr__()
    }

    fn __repr__(&self) -> String {
        format!(
            "RsSimilarityMatrixCreatorFactory(HPO: {hpo}, IC_MICA: {ic_mica})",
            hpo = Arc::strong_count(&self.hpo),
            ic_mica = Arc::strong_count(&self.ic_mica_dict),
        )
    }
}
