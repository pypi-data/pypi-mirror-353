pub mod simple;

pub trait SampleLabels {
    fn label(&self) -> &str;

    fn meta_label(&self) -> Option<&str>;
}

pub trait Labeled {
    type Labels: SampleLabels;
    fn labels(&self) -> &Self::Labels;
}

#[derive(Clone, PartialEq, Eq, Debug)]
pub struct Sample<L, PF> {
    labels: L,
    phenotypic_features: Box<[PF]>,
}

impl<L, PF> Sample<L, PF>
where
    L: SampleLabels,
{
    pub fn new<IL, IP>(labels: IL, phenotypic_features: IP) -> Sample<L, PF>
    where
        IL: Into<L>,
        IP: IntoIterator<Item = PF>,
    {
        Sample {
            labels: labels.into(),
            phenotypic_features: phenotypic_features.into_iter().collect::<Box<[_]>>(),
        }
    }
}

impl<L, PF> Labeled for Sample<L, PF>
where
    L: SampleLabels,
{
    type Labels = L;
    fn labels(&self) -> &Self::Labels {
        &self.labels
    }
}

impl<L, PF> AsRef<[PF]> for Sample<L, PF> {
    fn as_ref(&self) -> &[PF] {
        &self.phenotypic_features
    }
}

impl<L, PF> AsRef<L> for Sample<L, PF> {
    fn as_ref(&self) -> &L {
        &self.labels
    }
}
