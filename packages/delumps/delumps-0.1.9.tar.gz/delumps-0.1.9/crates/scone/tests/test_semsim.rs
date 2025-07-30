#[cfg(test)]
mod test_sm_io {
    use std::{error::Error, path::Path};

    use scone::semsim::io::read_ic_mica_data;

    #[test]
    fn test_sm_io() -> Result<(), Box<dyn Error>> {
        let csv_path = Path::new("resources").join("term-pair-similarity.2023-10-09.FBN1.csv.gz");
        let ic_mica_data = read_ic_mica_data(csv_path)?;

        assert_eq!(ic_mica_data.len(), 355, "There are 355 HPO terms");
        assert_eq!(
            ic_mica_data.values().flat_map(|inner| inner.iter()).count(),
            10_836,
            "There are 10_836 values"
        );
        Ok(())
    }
}
