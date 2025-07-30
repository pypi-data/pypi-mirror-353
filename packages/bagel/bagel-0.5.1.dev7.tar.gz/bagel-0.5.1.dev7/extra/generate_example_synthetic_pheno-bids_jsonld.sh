#!/bin/bash

test_data=neurobagel_examples/data-upload

bagel bids --jsonld-path ${test_data}/example_synthetic.jsonld \
    --bids-dir bids-examples/synthetic \
    --output ${test_data}/pheno-bids-output/example_synthetic_pheno-bids.jsonld \
    --overwrite
