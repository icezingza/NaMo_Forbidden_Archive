#!/bin/bash
# This script contains the full, correct, single-line command to deploy the service.
gcloud run deploy namo-forbidden-archive --image "gcr.io/arctic-signer-471822-i8/namo-forbidden-archive" --region "asia-southeast1" --platform "managed" --allow-unauthenticated --verbosity=debug
