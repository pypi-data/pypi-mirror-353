use std::mem::MaybeUninit;

use ndarray::Array2;

use crate::semsim::SimilarityKernel;

use super::NDArraySimilarityMatrix;

pub(super) fn use_symmetric_kernel<C, M, A, SK, SR>(
    kernel: &SK,
    cohort: C,
) -> anyhow::Result<NDArraySimilarityMatrix<SK::Value>>
where
    C: AsRef<[M]>,
    M: AsRef<[A]>,
    SK: SimilarityKernel<M, A, Value = SR>,
    SR: Clone,
{
    let cohort = cohort.as_ref();
    let n_samples = cohort.len();
    let mut array = Array2::uninit((n_samples, n_samples));

    for row in 0..n_samples {
        let a = &cohort[row];
        for col in row..n_samples {
            let b = &cohort[col];

            let result = kernel.compute(a, b)?;

            if row == col {
                // Assiging a value on the diagonal (self-similarity).
                // Dropping `MaybeUninit` does nothing.
                array[[row, col]] = MaybeUninit::new(result);
            } else {
                // Assigning non-diagonal item. This is symmetric kernel so we assign
                // the same value to both `i, j` and `j, i` cells.
                // Dropping `MaybeUninit` does nothing.
                array[[row, col]] = MaybeUninit::new(result.clone());
                array[[col, row]] = MaybeUninit::new(result);
            }
        }
    }

    // SAFETY: The ranges are OK and we assign *all* matrix cells with an initialized value.
    // If the code panics before getting here, the partially initialized `array` will be dropped,
    // resulting in a MEMORY LEAK but no memory safety issues.
    let array = unsafe { array.assume_init() };

    Ok(NDArraySimilarityMatrix { array })
}

pub(super) fn use_asymmetric_kernel<C, M, A, SK>(
    kernel: &SK,
    cohort: C,
) -> anyhow::Result<NDArraySimilarityMatrix<SK::Value>>
where
    C: AsRef<[M]>,
    M: AsRef<[A]>,
    SK: SimilarityKernel<M, A>,
{
    let cohort = cohort.as_ref();
    let n_samples = cohort.len();
    let mut array = Array2::<SK::Value>::uninit((n_samples, n_samples));

    for row in 0..n_samples {
        let a = &cohort[row];
        for col in 0..n_samples {
            let b = &cohort[col];

            let result = kernel.compute(a, b)?;
            array[[row, col]] = MaybeUninit::new(result); // Dropping `MaybeUninit` does nothing.
        }
    }

    // SAFETY: We exhaustively assign *all* matrix cells with result of `MaybeUninit::new`, which is safe to assume init.
    // If the code panics before getting here, the partially initialized `array` will be dropped,
    // resulting in a memory LEAK but no memory safety issues.
    let array = unsafe { array.assume_init() };

    Ok(NDArraySimilarityMatrix { array })
}
