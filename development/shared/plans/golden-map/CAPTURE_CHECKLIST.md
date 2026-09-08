# Golden Map capture checklist

Status: recording slots only. No screenshot or video is supplied in this pass.
Collect views only for routes actually executed; other slots remain NOT_RUN.

## Required views by route

| Slot | What to show | Must link to |
|---|---|---|
| rr-overview | RoadRunner source, curve/junction/slope overview | Source revision and export identity |
| source-editor | Saved Source CARLA map, not Dataprep preview | Reopen and material/reference checks |
| source-runtime | Loaded Source CARLA world and bounded vehicle view | Matching server/client and drive observations |
| package-runtime | Map loaded by the independent Package CARLA installation | Package hash, target identity and runtime checks |
| ue427-editor | Exact map in clean vanilla UE4.27 | Dependency, material and world-setting checks |
| ue427-pie | PIE in the receiver/cold-copy project | Receiver identity, reopen, PIE and collision results |

Optional pairs: material before/after, collision visualization, waypoint debug,
external-reference repair and matched performance plots. Use identical cameras,
lighting and workload for before/after comparisons; keep regressions visible.

## Recording and redaction

Recommend 1920×1080 PNG captures (16:9); 1280×720 is acceptable when readable.
Keep raw originals privately. Crop/redact project titles, machine paths, usernames,
IP addresses, dialogs, unrelated windows and proprietary labels. Do not fabricate,
retouch away map defects or use generated scenes as real screenshots.

Record capture ID, route, map alias/revision, tool version, camera/location,
timestamp, originating check ID, evidence path/hash and rights reviewer in the
public-safe evidence summary. Redaction must not conceal the check's actual result.

## README versus evidence

README: only rights-cleared, readable, reviewed views with a short case-specific
caption and a relative link to the accepted public evidence. Diagnostic screenshots
belong beside reviewed evidence only when rights and privacy allow; raw logs and
private paths never do. Unreviewed images remain outside Git.

After approval, place public media under [showcase assets](../../../../docs/assets/showcase/README.md)
and replace only the GOLDEN_MAP_SHOWCASE_START/END block in both READMEs.
Adding an image is a later explicit publication change: update the allowlist and
media policy then. Do not add broken image links now.
