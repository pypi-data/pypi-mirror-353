use std::{fs::File, io::BufReader, path::Path, sync::Arc};

use flate2::bufread::GzDecoder;
use ontolius::{io::OntologyLoaderBuilder, ontology::csr::MinimalCsrOntology};

pub(crate) fn load_hpo(fpath_hpo: impl AsRef<Path>) -> anyhow::Result<Arc<MinimalCsrOntology>> {
    let loader = OntologyLoaderBuilder::new().obographs_parser().build();
    if let Some(ext) = fpath_hpo.as_ref().extension() {
        if ext == "gz" {
            let reader = GzDecoder::new(BufReader::new(
                File::open(fpath_hpo).expect("File should exist"),
            ));
            return Ok(loader.load_from_read(reader).map(Arc::new)?);
        }
    }

    Ok(loader.load_from_path(fpath_hpo).map(Arc::new)?)
}
