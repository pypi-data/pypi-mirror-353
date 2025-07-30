use anyhow::Result;

pub mod io;
pub mod phenomizer;
pub mod precalc;
pub mod scone;
pub mod smc;
mod util;

/// A container for result of [`SimilarityMeasure`] between a pair of phenotypic features.
///
/// Note: the `similarity` should *never* be non-finite!
pub trait SimilarityMeasureValue {
    /// Get the similarity value as finite non-negative [`f64`] value.
    ///
    /// ## Examples
    ///
    /// ```rust
    /// use scone::semsim::SimilarityMeasureValue;
    ///
    /// let smr: f64 = 8.;
    ///
    /// assert_eq!(smr.similarity().to_bits(), smr.to_bits());
    /// ```
    fn similarity(&self) -> f64;

    /// Construct a similarity measure result with value of `0.` to represent no similarity.
    ///
    /// ## Examples
    ///
    /// ```rust
    /// use scone::semsim::SimilarityMeasureValue;
    ///
    /// let zero = f64::zero();
    /// ```
    fn zero() -> Self;

    /// Consume the similarity measure result and return the result with negated similarity.
    ///
    /// ## Examples
    ///
    /// ```rust
    /// use scone::semsim::SimilarityMeasureValue;
    ///
    /// let one: f64 = 1.0;
    /// let minus_one = one.negate();
    ///
    /// assert!(minus_one + 1. < 1e-10);
    /// ```
    fn negate(self) -> Self;
}

impl SimilarityMeasureValue for f64 {
    fn similarity(&self) -> f64 {
        *self
    }

    fn zero() -> Self {
        0.
    }

    fn negate(self) -> Self {
        -self
    }
}

/// Calculate similarity between a pair of annotations `A`.
pub trait SimilarityMeasure<A> {
    type Value: SimilarityMeasureValue;

    /// Compute similarity between two annotations `a` and `b`.
    fn compute_similarity(&self, a: &A, b: &A) -> Result<Self::Value>;

    /// Returns `true` if the similarity measure is symmetric (when `sim(a, b) == sim(b, a)`).
    fn is_symmetric(&self) -> bool;
}

pub trait SimilarityValue {
    fn similarity(&self) -> f64;
}

impl SimilarityValue for f64 {
    fn similarity(&self) -> f64 {
        *self
    }
}

impl SimilarityValue for f32 {
    fn similarity(&self) -> f64 {
        *self as f64
    }
}

/// `M` - Member
/// `A` - Annotation
pub trait SimilarityKernel<M, A> {
    type Value: SimilarityValue;

    fn compute(&self, a: &M, b: &M) -> Result<Self::Value>;

    fn is_symmetric(&self) -> bool;
}

pub trait SimilarityMatrix {
    type Similarity;

    fn similarity_between(&self, i: usize, j: usize) -> Option<&Self::Similarity>;

    fn len(&self) -> usize;
}

pub trait SimilarityMatrixCreator<C, M, A> {
    type Matrix: SimilarityMatrix;
    fn calculate_matrix(&self, cohort: C) -> Result<Self::Matrix>;
}

#[cfg(test)]
mod test {
    use core::f32;

    use super::SimilarityMatrix;

    #[test]
    fn similarity_matrix_is_object_safe() {
        let _x: Option<&dyn SimilarityMatrix<Similarity = f32>> = None;
    }
}
