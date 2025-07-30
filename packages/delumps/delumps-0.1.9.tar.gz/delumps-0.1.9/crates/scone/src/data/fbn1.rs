//! The `fbn1` module includes a bunch of phenotypes of samples mutations in *FBN1*.

use crate::model::simple::{SimplePhenotypicFeature, SimpleSampleLabels};
use crate::model::Sample;

use super::make_sample;

pub fn all_samples() -> Box<[Sample<SimpleSampleLabels, SimplePhenotypicFeature>]> {
    ectopia_lentis_familial()
        .into_iter()
        .chain(marfan())
        .collect()
}

pub fn ectopia_lentis_familial() -> [Sample<SimpleSampleLabels, SimplePhenotypicFeature>; 5] {
    [
        make_sample(
            "BM",
            &[
                ("HP:0001083", true),
                ("HP:0001065", true),
                ("HP:0012773", true),
                ("HP:0000501", false),
                ("HP:0000545", false),
                ("HP:0000486", false),
                ("HP:0002650", false),
                ("HP:0001382", false),
                ("HP:0000767", false),
                ("HP:0001166", false),
                ("HP:0000541", false),
                ("HP:0000768", false),
                ("HP:0000218", false),
                ("HP:0002616", false),
                ("HP:0001634", false),
            ],
        ),
        make_sample(
            "JL",
            &[
                ("HP:0001083", true),
                ("HP:0000545", true),
                ("HP:0001382", true),
                ("HP:0000768", true),
                ("HP:0000218", true),
                ("HP:0001065", true),
                ("HP:0000501", false),
                ("HP:0000486", false),
                ("HP:0002650", false),
                ("HP:0000767", false),
                ("HP:0001166", false),
                ("HP:0000541", false),
                ("HP:0002616", false),
                ("HP:0001634", false),
                ("HP:0012773", false),
            ],
        ),
        make_sample(
            "OP",
            &[
                ("HP:0001083", true),
                ("HP:0000545", true),
                ("HP:0001166", true),
                ("HP:0000218", true),
                ("HP:0001634", true),
                ("HP:0012773", true),
                ("HP:0000501", false),
                ("HP:0000486", false),
                ("HP:0002650", false),
                ("HP:0001382", false),
                ("HP:0000767", false),
                ("HP:0000541", false),
                ("HP:0000768", false),
                ("HP:0001065", false),
                ("HP:0002616", false),
            ],
        ),
        make_sample(
            "RWT",
            &[
                ("HP:0001083", true),
                ("HP:0000545", true),
                ("HP:0000486", true),
                ("HP:0001382", true),
                ("HP:0001065", true),
                ("HP:0000501", false),
                ("HP:0002650", false),
                ("HP:0000767", false),
                ("HP:0001166", false),
                ("HP:0000541", false),
                ("HP:0000768", false),
                ("HP:0000218", false),
                ("HP:0002616", false),
                ("HP:0001634", false),
                ("HP:0012773", false),
            ],
        ),
        make_sample(
            "VW",
            &[
                ("HP:0001083", true),
                ("HP:0000501", true),
                ("HP:0002650", true),
                ("HP:0000218", true),
                ("HP:0001065", true),
                ("HP:0000545", false),
                ("HP:0000486", false),
                ("HP:0001382", false),
                ("HP:0000767", false),
                ("HP:0001166", false),
                ("HP:0000541", false),
                ("HP:0000768", false),
                ("HP:0002616", false),
                ("HP:0001634", false),
                ("HP:0012773", false),
            ],
        ),
    ]
}

pub fn marfan() -> [Sample<SimpleSampleLabels, SimplePhenotypicFeature>; 12] {
    [
        make_sample(
            "B1",
            &[
                ("HP:0000268", true),
                ("HP:0001763", true),
                ("HP:0001166", true),
                ("HP:0000218", true),
                ("HP:0001519", true),
                ("HP:0001377", true),
                ("HP:0001083", true),
                ("HP:0000545", true),
                ("HP:0002616", true),
                ("HP:0001634", true),
            ],
        ),
        make_sample(
            "B3",
            &[
                ("HP:0001166", true),
                ("HP:0000098", true),
                ("HP:0002650", true),
                ("HP:0001083", true),
                ("HP:0000545", true),
                ("HP:0002616", true),
            ],
        ),
        make_sample(
            "B9",
            &[
                ("HP:0001166", true),
                ("HP:0001763", true),
                ("HP:0000098", true),
                ("HP:0000767", true),
                ("HP:0001083", true),
                ("HP:0002616", true),
            ],
        ),
        make_sample(
            "B18",
            &[
                ("HP:0001166", true),
                ("HP:0001763", true),
                ("HP:0000218", true),
                ("HP:0001382", true),
                ("HP:0001083", true),
                ("HP:0000545", true),
                ("HP:0002616", true),
                ("HP:0001634", true),
            ],
        ),
        make_sample(
            "B19",
            &[
                ("HP:0002650", true),
                ("HP:0001166", true),
                ("HP:0000218", true),
                ("HP:0001519", true),
                ("HP:0001382", true),
                ("HP:0001083", true),
                ("HP:0002616", true),
            ],
        ),
        make_sample("B37", &[("HP:0002616", true), ("HP:0004933", true)]),
        make_sample(
            "B43",
            &[
                ("HP:0001763", true),
                ("HP:0002650", true),
                ("HP:0001166", true),
                ("HP:0000218", true),
                ("HP:0001519", true),
                ("HP:0001382", true),
                ("HP:0000767", true),
                ("HP:0001083", true),
                ("HP:0000545", true),
                ("HP:0002616", true),
            ],
        ),
        make_sample(
            "B45",
            &[
                ("HP:0001166", true), // Arachnodactyly
                ("HP:0000098", true), // Tall stature
                ("HP:0002616", true), // Aortic root aneurysm
                ("HP:0000023", true), // Inguinal hernia
            ],
        ),
        make_sample(
            "B51",
            &[
                ("HP:0000268", true), // Dolichocephaly
                ("HP:0001166", true), // Arachnodactyly
                ("HP:0000218", true), // High palate
                ("HP:0001519", true), // Disproportionate tall stature
                ("HP:0001377", true), // Limited elbow extension
                ("HP:0001083", true), // Ectopia lentis
                ("HP:0000545", true), // Myopia
                ("HP:0002616", true), // Aortic root aneurysm"
                ("HP:0001634", true), // Mitral valve prolapse
                ("HP:0000023", true), // Inguinal hernia
            ],
        ),
        make_sample(
            "B52",
            &[
                ("HP:0002650", true), // Scoliosis
                ("HP:0001166", true), // Arachnodactyly
                ("HP:0000098", true), // Tall stature
                ("HP:0001382", true), // Joint hypermobility
                ("HP:0000767", true), // Pectus excavatum
                ("HP:0001083", true), // Ectopia lentis
                ("HP:0002616", true), // Aortic root aneurysm
                ("HP:0001634", true), // Mitral valve prolapse
                ("HP:0001065", true), // Striae distensae
            ],
        ),
        make_sample(
            "B60",
            &[
                ("HP:0000268", true), // Dolichocephaly
                ("HP:0001763", true), // Pes planus
                ("HP:0002616", true), // Aortic root aneurysm
                ("HP:0004933", true), // Ascending aortic dissection
            ],
        ),
        make_sample(
            "B62",
            &[
                ("HP:0002650", true),
                ("HP:0001166", true),
                ("HP:0000098", true),
                ("HP:0001382", true),
                ("HP:0000767", true),
                ("HP:0001083", true),
                ("HP:0002616", true),
                ("HP:0001634", true),
                ("HP:0001065", true),
            ],
        ),
    ]
}
