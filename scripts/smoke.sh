#!/usr/bin/env bash
set -euo pipefail
BASE_URL="${FIXCHECK_API_URL:-http://localhost:8000}"
curl --fail --silent --show-error "$BASE_URL/api/health" >/dev/null
cases=$(curl --fail --silent --show-error "$BASE_URL/api/demo")
rows=$(python -c 'import json,sys; cases=json.load(sys.stdin); sys.exit("No demo cases available") if not cases else None; [print(c["case_id"],c["expected"]) for c in cases]' <<< "$cases")
failed=0
while read -r case_id expected; do
    response=$(curl --fail --silent --show-error -X POST "$BASE_URL/api/demo/$case_id/verify")
    got=$(python -c 'import json,sys; print(json.load(sys.stdin)["verdict"])' <<< "$response")
    echo "$case_id $expected → $got"
    if [[ "$got" != "$expected" ]]; then failed=1; fi
done <<< "$rows"
exit "$failed"
