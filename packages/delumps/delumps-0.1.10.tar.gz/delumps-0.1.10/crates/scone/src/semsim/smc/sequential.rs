use anyhow::{bail, Result};

use crate::semsim::{SimilarityKernel, SimilarityMatrixCreator};

use super::{
    common::{use_asymmetric_kernel, use_symmetric_kernel},
    NDArraySimilarityMatrix,
};

pub struct SequentialSimilarityMatrixCreator<SK> {
    similarity_kernel: SK,
}

impl<SK> SequentialSimilarityMatrixCreator<SK> {
    pub fn new(similarity_kernel: SK) -> Self {
        SequentialSimilarityMatrixCreator { similarity_kernel }
    }
}

impl<C, M, A, SR, SK> SimilarityMatrixCreator<C, M, A> for SequentialSimilarityMatrixCreator<SK>
where
    C: AsRef<[M]>,
    M: AsRef<[A]>,
    SK: SimilarityKernel<M, A, Value = SR>,
    SR: Clone,
{
    type Matrix = NDArraySimilarityMatrix<SK::Value>;

    fn calculate_matrix(&self, cohort: C) -> Result<Self::Matrix> {
        check_patients(cohort.as_ref())?;
        if self.similarity_kernel.is_symmetric() {
            use_symmetric_kernel(&self.similarity_kernel, cohort)
        } else {
            use_asymmetric_kernel(&self.similarity_kernel, cohort)
        }
    }
}

fn check_patients<P>(patients: &[P]) -> Result<()> {
    if patients.is_empty() {
        bail!("Patients must not be empty");
    } else if patients.len() == 1 {
        bail!("Patients must contain >1 elements");
    } else {
        Ok(())
    }
}
