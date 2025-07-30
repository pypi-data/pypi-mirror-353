use std::{
    cmp::Ordering, collections::HashMap, fs::File, io::{BufRead, BufReader, Read}, path::Path, str::FromStr
};

use anyhow::{bail, Context, Result};

use flate2::read::GzDecoder;
use ontolius::TermId;

pub fn read_ic_mica_data<'a>(fpath: impl AsRef<Path>) -> Result<HashMap<TermId, HashMap<TermId, f64>>> {
    let read = open_for_reading(fpath)?;
    let mut buf_reader = BufReader::new(read);
    let (_comments, header) = parse_header(&mut buf_reader, '#')?;

    let field_names: Vec<&str> = header.split(',').collect();

    let mut ic_mica_map = HashMap::new();
    for (i, ele) in buf_reader.lines().enumerate() {
        match ele {
            Ok(line) => {
                let field2val: HashMap<&str, &str> =
                    field_names.iter().cloned().zip(line.split(',')).collect();
                let a = TermId::from_str(field2val["term_a"])
                    .context("Parsing `term_a` value into `TermId`")?;
                let b = TermId::from_str(field2val["term_b"])
                    .context("Parsing `term_b` value into `TermId`")?;
                let ic_mica = f64::from_str(field2val["ic_mica"])
                    .context("Parsing `ic_mica` value into `f64`")?;
                let (leq, gt) = match a.cmp(&b) {
                    Ordering::Less | Ordering::Equal => (a, b),
                    Ordering::Greater => (b, a),
                };
                ic_mica_map
                    .entry(leq)
                    .or_insert(HashMap::new())
                    .insert(gt, ic_mica);
            }
            Err(e) => bail!("Invalid line #{i}: {:?}", e.to_string()),
        }
    }

    // We won't be inserting more stuff in the map
    ic_mica_map.shrink_to_fit();
    Ok(ic_mica_map)
}

fn parse_header<R>(buf_read: &mut R, comment_char: char) -> Result<(Vec<String>, String)>
where
    R: BufRead,
{
    let mut comments = Vec::new();
    let mut maybe_header = None;

    for ele in buf_read.lines() {
        match ele {
            Ok(line) => {
                if line.starts_with(comment_char) {
                    if let Some(val) = line.strip_suffix('\n') {
                        comments.push(val.to_owned())
                    }
                } else {
                    maybe_header = Some(line);
                    break;
                }
            }
            Err(e) => bail!(e),
        }
    }

    if let Some(h) = maybe_header {
        Ok((comments, h))
    } else {
        bail!("Did not find header".to_string())
    }
}

fn open_for_reading(path: impl AsRef<Path>) -> Result<Box<dyn Read>> {
    match File::open(&path) {
        Ok(file) => {
            if let Some(extension) = path.as_ref().extension() {
                if extension == "gz" {
                    return Ok(Box::new(GzDecoder::new(file)));
                }
            }
            Ok(Box::new(file))
        }
        Err(e) => bail!(e),
    }
}
