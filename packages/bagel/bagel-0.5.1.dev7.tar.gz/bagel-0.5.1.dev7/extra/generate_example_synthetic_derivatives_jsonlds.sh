#!/bin/bash

test_data=neurobagel_examples/data-upload

bagel derivatives \
    --tabular ${test_data}/nipoppy_proc_status_synthetic.tsv \
    --jsonld-path ${test_data}/example_synthetic.jsonld \
    --output "${test_data}/pheno-derivatives-output/example_synthetic_pheno-derivatives.jsonld" \
    --overwrite

bagel derivatives \
    --tabular ${test_data}/nipoppy_proc_status_synthetic.tsv \
    --jsonld-path "${test_data}/pheno-bids-output/example_synthetic_pheno-bids.jsonld" \
    --output "${test_data}/pheno-bids-derivatives-output/example_synthetic_pheno-bids-derivatives.jsonld" \
    --overwrite
