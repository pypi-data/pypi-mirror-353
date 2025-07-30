#!/bin/bash

test_data=neurobagel_examples/data-upload

bagel pheno \
    --pheno ${test_data}/example_synthetic.tsv \
    --dictionary ${test_data}/example_synthetic.json \
    --portal https://github.com/bids-standard/bids-examples \
    --name "BIDS synthetic" \
    --output "${test_data}/example_synthetic.jsonld" \
    --overwrite
