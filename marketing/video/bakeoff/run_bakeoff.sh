#!/bin/bash
# Bake-off: same illustration -> multiple image-to-video models, silent clips.
# Usage: BAKEOFF_IMAGE=<path> bash run_bakeoff.sh
# Requires REPLICATE_API_TOKEN in env. Estimated cost: <$1 total.
set -euo pipefail

IMG="${BAKEOFF_IMAGE:?set BAKEOFF_IMAGE to an illustration path}"
OUTDIR="$(dirname "$0")/out"
mkdir -p "$OUTDIR"
PROMPT="Subtle gentle animation of this children's book illustration: the character blinks and breathes softly, ambient elements drift slowly (clouds, leaves, water), camera pushes in very slowly. Preserve the illustration's exact art style, colors and composition. No new elements. Calm, dreamy, minimal motion."
DURATION=5

run_model() {
  local name="$1" model="$2" extra="${3:-}"
  echo "== $name =="
  local out="$OUTDIR/${name}.mp4"
  # escape image as data uri
  local payload_file="/tmp/bakeoff_payload.json"
  python3 - "$PROMPT" "$DURATION" "$extra" "$IMG" "$payload_file" <<'PY'
import json,sys,base64
p,dur,extra,img,dest=sys.argv[1:6]
d="data:image/png;base64,"+base64.b64encode(open(img,'rb').read()).decode()
inp={"image":d,"prompt":p,"duration":int(dur)}
if extra: inp.update(json.loads(extra))
open(dest,'w').write(json.dumps({"input":inp}))
PY
  local pred
  pred=$(curl -s -X POST "https://api.replicate.com/v1/models/${model}/predictions" \
    -H "Authorization: Bearer ${REPLICATE_API_TOKEN}" \
    -H "Content-Type: application/json" --data-binary "@${payload_file}")
  local pid
  pid=$(echo "$pred" | python3 -c "import sys,json;print(json.load(sys.stdin).get('id',''))")
  if [ -z "$pid" ]; then echo "SUBMIT FAILED: $pred"; return 1; fi
  echo "prediction: $pid (polling...)"
  for i in $(seq 1 60); do
    sleep 10
    local res
    res=$(curl -s "https://api.replicate.com/v1/predictions/${pid}" \
      -H "Authorization: Bearer ${REPLICATE_API_TOKEN}")
    local status
    status=$(echo "$res" | python3 -c "import sys,json;print(json.load(sys.stdin).get('status',''))")
    echo "  status: $status"
    [ "$status" = "succeeded" ] || [ "$status" = "failed" ] || continue
    if [ "$status" = "succeeded" ]; then
      local url
      url=$(echo "$res" | python3 -c "import sys,json;d=json.load(sys.stdin)['output'];print(d if isinstance(d,str) else d[0])")
      curl -sL -o "$out" "$url" && echo "saved: $out"
    else
      echo "FAILED: $res"
    fi
    break
  done
}

# Cheapest -> priciest. Costs are per output second. Skips models whose clip already exists.
[ -f "$OUTDIR/wan-2.2-720p.mp4" ] || run_model "wan-2.2-720p" "wan-video/wan-2.2-i2v-fast"
run_model "seedance-2.0-720p"  "bytedance/seedance-2.0"          '{"resolution":"720p"}'
run_model "kling-v2.5-turbo"   "kwaivgi/kling-v2.5-turbo-pro"

echo "done. compare clips in $OUTDIR"
