use std::fs::File;
use std::io::BufReader;
use std::path::Path;
use std::sync::Arc;

use criterion::{black_box, criterion_group, criterion_main, BenchmarkId, Criterion};
use flate2::bufread::GzDecoder;
use ontolius::io::OntologyLoaderBuilder;
use ontolius::ontology::csr::MinimalCsrOntology;
use scone::data::fbn1;
use scone::semsim::io::read_ic_mica_data;
use scone::semsim::precalc::PrecomputedIcMicaSimilarityMeasure;
use scone::semsim::scone::{SconeConfig, SconeSimilarityKernel};
use scone::semsim::smc::SequentialSimilarityMatrixCreator;
use scone::semsim::SimilarityMatrixCreator;

fn load_hpo(fpath_hpo: impl AsRef<Path>) -> MinimalCsrOntology {
    let loader = OntologyLoaderBuilder::new().obographs_parser().build();
    if let Some(ext) = fpath_hpo.as_ref().extension() {
        if ext == "gz" {
            let reader = GzDecoder::new(BufReader::new(
                File::open(fpath_hpo).expect("File should exist"),
            ));
            return loader.load_from_read(reader).unwrap();
        }
    }

    loader.load_from_path(fpath_hpo).unwrap()
}

fn sequential_scone_bench(c: &mut Criterion) {
    let fpath_hpo = "/todo/add/real/path/to/hp.v2023-10-09.json";
    let fpath_ic_mica =
        "/todo/add/real/path/to/term-pair-similarity.2023-10-09.csv.gz";

    let hpo = Arc::new(load_hpo(fpath_hpo));
    let ic_mica_dict = read_ic_mica_data(fpath_ic_mica).map(Arc::new).unwrap();
    let similarity_measure =
            PrecomputedIcMicaSimilarityMeasure::new(Arc::clone(&ic_mica_dict), Arc::clone(&hpo));
    let kernel = SconeSimilarityKernel::new(Arc::clone(&hpo), similarity_measure, SconeConfig::default());
    let smc = SequentialSimilarityMatrixCreator::new(kernel);

    let samples: Box<[_]> = fbn1::all_samples();

    let mut group = c.benchmark_group("Delumps::SconeSimilarityKernel");
    group.bench_function(
        BenchmarkId::from_parameter("SequentialSimilarityMatrixCreator::SconeSimilarityKernel"),
        |b| {
            b.iter(|| {
                black_box(
                    smc.calculate_matrix(&samples)
                        .expect("Should calculate the result!"),
                );
            })
        },
    );
}

criterion_group!(benches, sequential_scone_bench);
criterion_main!(benches);
