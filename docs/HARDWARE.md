# Hardware readiness and reproducible evidence

This is INT-03's inspection and measurement procedure. [STATUS.md](STATUS.md#int-03-apply-hardware-readiness) records actual observations; [SOURCES.md](SOURCES.md) owns vendor provenance and pinned model candidates. [ARCHITECTURE.md](ARCHITECTURE.md) owns clocks, contracts and adapter boundaries. A procedure or model list is not evidence of a successful run.

## Inspect an available host

From the repository root, after the documented core setup:

```sh
git rev-parse HEAD
uname -srmo
lsusb
command -v hailortcli
.venv/bin/python - <<'PY'
import importlib.util
import sys
print('Application Python:', sys.version.split()[0])
print('hailo_platform:', importlib.util.find_spec('hailo_platform'))
PY
```

These commands do not capture microphone/camera data or install drivers/models. `command -v` returning no path and `find_spec` returning `None` mean the CLI/module is not available in those inspected environments. If the sandbox cannot initialize libusb, obtain the host's read-only USB listing; do not interpret sandbox failure as an absent device. On another OS, record the equivalent supported device/runtime inspection instead of running Linux commands blindly.

Record the observation date, host OS/architecture, source revision and actual output summary in STATUS. Device detection alone does not establish driver, firmware, model, or inference compatibility. A missing device on one host says nothing about the team's access elsewhere. Do not scan private files for models or credentials.

## Resolve target prerequisites

Use the official USB-8G specifications and pinned Hailo references in SOURCES. The speech candidate uses windowed audio; the pose table's published performance conditions use PCIe, while LeCoach targets USB. The inspected generic Hailo Apps prerequisites include PCIe/Hailo-8 instructions. Confirm a supported Hailo-10H USB host/driver/runtime/firmware combination before selecting an ABI-compatible wheel or installing anything.

Lane 2 owns speech inference, Lane 3 owns vision inference, Lane 4 owns the sole engagement engine, and Lane 5 owns the recorder/feedback. Integration owns composition and evidence review. Do not create alternate adapters or a second logger for a benchmark. Keep CPU/live and target-device paths separately named even when they implement the same public seam.

Before a measured target run, obtain:

- Identified UGen300 variant/interface and supported host; runtime/driver/firmware versions and official installation source.
- Approved owner adapter revisions and actual model/HEF hashes, model rights, preprocessing and postprocessing.
- INT-02 composition with the shared clock and accepted lifecycle, plus instrumentation that identifies timing endpoints without changing the event schema here.
- A consented reproducible local scenario; warm-up, workload, duration and repeat count agreed for the run.

If a prerequisite is missing, record it, the required owner/handoff action, and the unmeasured scope. Do not download weights, change the Python pin, install drivers, or turn vendor benchmarks into LeCoach measurements under this inspection procedure.

## Run record

Keep private media/transcripts/session exports under ignored `sessions/` or `recordings/`, weights under ignored `models/`, and receipts/credentials outside Git. Commit only sanitized configuration/procedure/results in STATUS. Include a reference to the private local run identifier without exposing its content or personal data.

| Field | What to record |
| --- | --- |
| Identity | Date, source revision, local run identifier, inspected host OS/CPU/architecture. |
| Mode | Synthetic/authored replay, live CPU, isolated target inference, or integrated target inference. Identify both input and output provenance. |
| Target | Actual device variant, USB/interface path, firmware, driver, HailoRT and binding versions; use `not used` for CPU/replay. |
| Models | Exact model name/revision, weight/HEF SHA-256, precision, rights/reference, installed runtime compatibility. |
| Data path | Audio sample rate/window/hop and transcription revision policy; camera resolution/rate; preprocessing and keypoint/facing/activity postprocessing. |
| Reproduction | Exact setup and launch commands, configuration values, scenario actions, warm-up, workload, capture duration and repeat count. |
| Instrumentation | Clock origin/offset mapping, timing endpoints, units, measurement code/revision, sample inclusion rules. |
| Results | Sample count, median, range and p95 where meaningful; failures, dropped/unavailable observations, and unmeasured intervals. |
| Behavior | Audience deterioration/recovery, evidence-supported feedback, unavailable-input handling, stop/drain/resource release and session restart/isolation. |
| Limitations | Isolated versus concurrent work, privacy/capture scope, model accuracy/filler limitations, missing instrumentation and next action. |

This table is a record template, not another event schema. A completed row must contain measured values or explicit `not measured`/`not applicable` entries; empty fields are not evidence.

## Timing definitions

Use the canonical capture clock and owner-provided instrumentation. Never subtract browser `performance.now()` directly from a backend capture timestamp; their origins differ unless a mapping is measured.

| Interval | Definition / interpretation |
| --- | --- |
| Input window | Audio `window_end_s - window_start_s`, or actual video acquisition interval. This is not inference time. |
| Producer delivery | Shared-clock emission/receipt endpoint minus capture/window-end timestamp, with the precise endpoint named. Includes processing/queuing after that capture endpoint. |
| Model processing | Model invocation end minus invocation start on a named monotonic clock; excludes prior capture/window accumulation. |
| Audience decision | Engine decision receipt time minus the newest relevant capture timestamp; identify smoothing/hysteresis settings and older supporting observations separately. |
| UI transport/render | Mapped decision-to-browser receipt/render intervals, only with known endpoints and clock mapping. Browser receipt is not proof of visible rendering. |

Report warm-up separately; use comparable samples for median/p95/range and document the p95 method/sample count. Include failures/drops instead of silently removing them. If only producer delivery is instrumented, report that interval and explicitly leave end-to-end response unmeasured. Vendor FPS/TOPS and speech window duration cannot fill a missing timing field.

## Validation sequence

1. Inspect prerequisites and record any missing-device/runtime outcome.
2. When the supported setup and owner adapters exist, run each model in isolation; report only isolated execution/measurements.
3. After INT-02's accepted composition, run concurrent speech and vision through the sole engine and recorder. Use Lane 5's weak-to-improved scenario with actual input. Observe audience behavior and inspect timestamped feedback/evidence.
4. Stop and repeat; check device release, session identity/isolation, unavailable input, late observations and drain behavior with the subsystem owners.
5. Record sanitized results in STATUS, update the submission claim references, and retain every unmeasured component explicitly.

An unavailable-hardware disposition can support an honest Stage I architecture proposal. It does not pass measured accelerator inference or INT-02 live acceptance. Revisit it when the team provides hardware/runtime access; keep local model-free preparation moving in the meantime.
