mod common;
mod sequential;

pub use sequential::SequentialSimilarityMatrixCreator;

use ndarray::Array2;

use super::SimilarityMatrix;

#[derive(Clone, Debug)]
pub struct NDArraySimilarityMatrix<S> {
    array: Array2<S>,
}

impl<S> NDArraySimilarityMatrix<S> {
    pub fn array(self) -> Array2<S> {
        self.array
    }
}

impl<S> SimilarityMatrix for NDArraySimilarityMatrix<S> {
    type Similarity = S;

    fn similarity_between(&self, i: usize, j: usize) -> Option<&Self::Similarity> {
        self.array.get((i, j))
    }

    fn len(&self) -> usize {
        self.array.dim().0
    }
}
