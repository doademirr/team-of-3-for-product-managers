#!/usr/bin/env bash
# test-critic.sh — committed eval gate for the Team-of-3 seam (dogfoods the coding ruler, Step 6C half 1).
#
# Two layers:
#   1. Unit cases on the REAL canonicaliser — extracted from critic.sh at runtime, so the test can
#      never drift from a copy. Covers accept/reject incl. the location field and every fail-closed path.
#   2. Schema strict-mode lint on verdict.schema.json — every property must be in `required` and every
#      object must set additionalProperties:false. This is the exact class of bug that broke the seam on
#      2026-09-14 (nullable-but-omitted-from-required → 400 invalid_json_schema).
#
# IMPORTANT: a green run does NOT replace a live smoke test. Unit tests cannot catch API-contract
# regressions (the 2026-09-14 bug was invisible to them). After ANY seam edit, still run one live
# critic.sh call against a real draft before relying on it.
#
# Usage: bash test-critic.sh   (exit 0 = all green, 1 = red)

set -uo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRITIC="$DIR/critic.sh"
SCHEMA="$DIR/verdict.schema.json"
TMP="$(mktemp -d)" || { echo "FATAL: cannot mktemp"; exit 1; }
trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0

[ -f "$CRITIC" ] || { echo "FATAL: critic.sh not found at $CRITIC"; exit 1; }
[ -f "$SCHEMA" ] || { echo "FATAL: verdict.schema.json not found at $SCHEMA"; exit 1; }

# --- Extract the real canonicaliser from critic.sh (the python heredoc between <<'PY' and PY) ---
awk "/<<'PY'/{f=1;next} /^PY\$/{f=0} f" "$CRITIC" > "$TMP/canon.py"
[ -s "$TMP/canon.py" ] || { echo "FATAL: could not extract canonicaliser from critic.sh (markers changed?)"; exit 1; }

check() { # $1 name  $2 expected(ACC|REJ)  $3 json
  printf '%s' "$3" > "$TMP/case.json"
  out="$(python3 "$TMP/canon.py" "$TMP/case.json")"
  [ -z "$out" ] && got=REJ || got=ACC
  if [ "$got" = "$2" ]; then
    pass=$((pass+1))
  else
    fail=$((fail+1)); printf '  FAIL: %-26s want=%s got=%s\n' "$1" "$2" "$got"
    [ "$got" = ACC ] && printf '        -> %s\n' "$out"
  fi
}

echo "== Layer 1: canonicaliser unit cases (real code, extracted from critic.sh) =="
# accepted
check "PASS clean"             ACC '{"verdict":"PASS","issues":null,"reason":null}'
check "ISSUES + location"      ACC '{"verdict":"ISSUES","issues":[{"ruler_item":"Scope","problem":"no non-goals","severity":"moderate","location":"§4"}],"reason":null}'
check "ISSUES no location key" ACC '{"verdict":"ISSUES","issues":[{"ruler_item":"Scope","problem":"x","severity":"moderate"}],"reason":null}'
check "ISSUES location null"   ACC '{"verdict":"ISSUES","issues":[{"ruler_item":"Scope","problem":"x","severity":"minor","location":null}],"reason":null}'
check "ISSUES multi"           ACC '{"verdict":"ISSUES","issues":[{"ruler_item":"A","problem":"x","severity":"critical","location":"F8"},{"ruler_item":"B","problem":"y","severity":"minor","location":null}],"reason":null}'
check "BLOCKED + reason"       ACC '{"verdict":"BLOCKED","issues":null,"reason":"need the source PRD"}'
# rejected -> fail closed
check "location non-string"    REJ '{"verdict":"ISSUES","issues":[{"ruler_item":"Scope","problem":"x","severity":"moderate","location":4}],"reason":null}'
check "bad severity"           REJ '{"verdict":"ISSUES","issues":[{"ruler_item":"Scope","problem":"x","severity":"high","location":null}],"reason":null}'
check "unknown extra key"      REJ '{"verdict":"ISSUES","issues":[{"ruler_item":"Scope","problem":"x","severity":"minor","foo":"bar"}],"reason":null}'
check "issue missing field"    REJ '{"verdict":"ISSUES","issues":[{"ruler_item":"Scope","severity":"minor"}],"reason":null}'
check "PASS with issues"       REJ '{"verdict":"PASS","issues":[{"ruler_item":"Scope","problem":"x","severity":"minor","location":null}],"reason":null}'
check "PASS with reason"       REJ '{"verdict":"PASS","issues":null,"reason":"why"}'
check "ISSUES with reason"     REJ '{"verdict":"ISSUES","issues":[{"ruler_item":"A","problem":"x","severity":"minor","location":null}],"reason":"also this"}'
check "ISSUES empty list"      REJ '{"verdict":"ISSUES","issues":[],"reason":null}'
check "BLOCKED no reason"      REJ '{"verdict":"BLOCKED","issues":null,"reason":null}'
check "unknown verdict"        REJ '{"verdict":"MAYBE","issues":null,"reason":null}'
check "model-emitted UNABLE"   REJ '{"verdict":"UNABLE_TO_REVIEW","issues":null,"reason":"x"}'
check "malformed json"         REJ 'not json at all'

echo "== Layer 2: schema strict-mode lint =="
if python3 - "$SCHEMA" <<'PY'
import json, sys
schema = json.load(open(sys.argv[1]))
bad = []
def walk(node, path="root"):
    if isinstance(node, dict):
        if isinstance(node.get("properties"), dict):
            props = set(node["properties"].keys())
            req = set(node.get("required", []))
            missing = props - req
            if missing:
                bad.append(f"{path}: properties not in `required`: {sorted(missing)}")
            if node.get("additionalProperties") is not False:
                bad.append(f"{path}: object must set additionalProperties:false (strict mode)")
        for k, v in node.items():
            walk(v, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]")
walk(schema)
if bad:
    print("  SCHEMA LINT FAIL (OpenAI strict mode: every property in `required`, additionalProperties:false):")
    for b in bad:
        print("    " + b)
    sys.exit(1)
print("  ok: every property is in `required`; every object sets additionalProperties:false")
PY
then lint=0; else lint=1; fi

echo "== summary =="
echo "  unit: $pass passed, $fail failed  |  schema-lint: $([ "$lint" -eq 0 ] && echo ok || echo FAIL)"
if [ "$fail" -eq 0 ] && [ "$lint" -eq 0 ]; then
  echo "ALL GREEN"; exit 0
else
  echo "RED — do not ship the seam"; exit 1
fi
