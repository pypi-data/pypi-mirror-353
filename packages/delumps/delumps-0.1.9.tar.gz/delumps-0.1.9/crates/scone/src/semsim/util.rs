use std::{iter::Sum, ops::Div};

pub(super) fn compute_two_sided_similarity<A, B>(a_to_b_sims: A, b_to_a_sims: B) -> f64
where
    A: AsRef<[f64]>,
    B: AsRef<[f64]>,
{
    let a_to_b = compute_mean(a_to_b_sims.as_ref());
    let b_to_a = compute_mean(b_to_a_sims.as_ref());

    f64::max((a_to_b + b_to_a) * 0.5, 0.)
}

fn compute_mean<T>(vals: &[T]) -> f64
where
    T: for<'a> Sum<&'a T> + Div<f64, Output = f64>,
{
    if vals.is_empty() {
        0.
    } else {
        let len = vals.len() as f64;
        vals.iter().sum::<T>() / len
    }
}
