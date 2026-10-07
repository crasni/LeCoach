# Competition and hardware source provenance

Reviewed 2026-10-07 for INT-03. The source hierarchy is defined in [GUIDE.md](../GUIDE.md#0-source-of-truth). [CONTEST.md](CONTEST.md) records verified external requirements; [STATUS.md](STATUS.md) records LeCoach's observed implementation and hardware readiness. Reference information does not establish working LeCoach inference.

## Competition source

The [official competition page](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/) was fetched directly over HTTPS. The browser extraction service returned 404, but direct retrieval succeeded and included the full rules in the `application/ld+json` Event description. Sections III–VII were inspected for platform, schedule, deliverable and judging requirements. The top-level metadata contains inconsistent/dynamic end dates; the rules prose establishes the date recorded in CONTEST, but does not establish a precise cutoff timezone.

The retrieved HTML SHA-256 is `6eb1c65f1f3b9052823c6ca5106578dc02531107d40edc9380b4452cf557b254`. Retrieval snapshots remain temporary investigation files, not committed copies of the rules. To recheck from a shell:

```sh
curl --fail --location --silent --show-error \
  'https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/' \
  -o /tmp/lecoach-official-contest.html
```

Read the current rendered page or parse the JSON-LD description; a successful HTTP response alone is not evidence that the requirements were checked.

## Repository reference PDFs

These were supplied with the repository. Publication provenance was not independently authenticated. They support development research; newer organizer or manufacturer documentation takes precedence. PDF page numbers below are physical pages, followed by printed slide numbers where different.

| Reference | Relevant pages inspected | SHA-256 |
| --- | --- | --- |
| [Competition promotion](ASUS_UGen_AI_League_Hackathon_推廣簡報_ZH.pdf) | 1–3: platforms, applications, Stage I schedule/deliverables. | `236805410b911b101ae89814bf525173c72541db5e4793e2ee04f3d1f20b4078` |
| [UGen sales kit](ASUS_UGen_Series_SalesKit_FINAL_Matt_20260917_v3_up.pdf) | 2–8: specifications/model coverage; 12: apps; 15 (slide 39): runtime/HEF flow. | `d769386b9099e110dd3c241e9255ec81a13471a112b410e7dbc8c5a0481ec3f6` |
| [Arc Pro B70 reference](UGen_Arc_Pro_B70.pdf) | 3: preliminary specifications; 5–10: attributed benchmarks; 11–15: software and development status. B70 is outside the selected track. | `e40a10584d0b1a26412dc797a74890fd502eb12155ef244d0b05fb90ecf7a12f` |

Text extraction used `pdftotext -layout`; image-only appendix pages were not used as evidence. Counts and vendor/demo benchmarks in the PDFs are not LeCoach measurements.

## Manufacturer and runtime references

The [ASUS USB-8G technical specifications](https://www.asus.com/motherboards-components/ai-accelerator/ugen/ugen300-usb-8g/techspec/) list Hailo-10H, 8 GB LPDDR4, USB 3.1 Gen2 Type-C, up to 40 TOPS INT4 / 20 TOPS INT8, and typical 2.5 W consumption. These are advertised hardware properties, not end-to-end application latency or measured host power.

Official Hailo revisions were resolved through GitHub's public commit API to make these references reproducible:

| Repository | Inspected revision | Relevant documentation |
| --- | --- | --- |
| HailoRT | `f51959034a8a49b7ee53cd0034a161faa30352ba` | [Runtime overview](https://github.com/hailo-ai/hailort/blob/f51959034a8a49b7ee53cd0034a161faa30352ba/README.md). Hailo-10/15 use master; Hailo-8 uses a different branch. |
| Hailo Apps | `c61f843b618ea2faa20dad79097c0591900319f4` | [Prerequisites](https://github.com/hailo-ai/hailo-apps/blob/c61f843b618ea2faa20dad79097c0591900319f4/doc/user_guide/prerequisites.md) and [installation](https://github.com/hailo-ai/hailo-apps/blob/c61f843b618ea2faa20dad79097c0591900319f4/doc/user_guide/installation.md). |
| Vision Model Zoo | `49039700f5c1aff9063e028c3bc55ef174371b36` | [Hailo-10H pose models](https://github.com/hailo-ai/hailo_model_zoo/blob/49039700f5c1aff9063e028c3bc55ef174371b36/docs/public_models/HAILO10H/HAILO10H_pose_estimation.rst). |
| GenAI Model Zoo | `187484184ff8bdfb04f035b30d6be2bbf4fcb57f` | [Models and version compatibility](https://github.com/hailo-ai/hailo_model_zoo_genai/blob/187484184ff8bdfb04f035b30d6be2bbf4fcb57f/docs/MODELS.rst). |

## Candidate adapter paths — untested

| Subsystem | Evidence-backed candidate | Compatibility / measurement still required |
| --- | --- | --- |
| Speech | GenAI Model Zoo lists Whisper Tiny/Base/Small with C++/Python inference and compiled v5.4.0 HEFs. It describes 16 kHz audio in 10-second windows. | Lane 2 must verify model/runtime compatibility, chunking/revision behavior and delivery latency; this documentation does not establish a streaming LeCoach producer. |
| Vision | The Hailo-10H pose table provides `yolov8s_pose` and `yolov8m_pose` HEFs with 640×640×3 input. | Lane 3 must validate preprocessing, keypoint postprocessing, approximate facing/activity mapping and model rights. Published FPS uses PCIe Gen3 ×4, not the selected USB host path. |

Hailo Apps' inspected prerequisites identify v5.4.0 as their tested HailoRT version. Installation is platform/app dependent, and Python wheels are ABI-specific. Validate an actual USB-8G driver/runtime/firmware combination through ASUS/Hailo before selecting dependencies; generic PCIe instructions are not USB installation evidence. Do not change the core Python 3.12 pin or install an incompatible wheel based on a model list alone.

The speech path's windowing and both producers' device contention need measurement before tuning engagement staleness. Shared capture-time and adapter cleanup contracts stay in [ARCHITECTURE.md](ARCHITECTURE.md); this research changes no contracts or producer implementation.
