# Competition and hardware source provenance

Competition rules content rechecked 2026-10-10; hardware sources reviewed 2026-10-07 for INT-03. The source hierarchy is defined in [GUIDE.md](../GUIDE.md#0-source-of-truth). [CONTEST.md](CONTEST.md) records verified external requirements; [STATUS.md](STATUS.md) records LeCoach's observed implementation and hardware readiness. Reference information does not establish working LeCoach inference.

## Competition source

The [official competition page](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/) was fetched directly over HTTPS. The browser extraction service returned 404, but direct retrieval succeeded and included the full rules in the `application/ld+json` Event description. Sections III–VII were inspected for platform, schedule, deliverable and judging requirements. The top-level metadata contains inconsistent/dynamic end dates; the rules prose establishes the date recorded in CONTEST, but does not establish a precise cutoff timezone.

Initial research HTML SHA-256: `6eb1c65f1f3b9052823c6ca5106578dc02531107d40edc9380b4452cf557b254`. During INT-03 apply on 2026-10-07 at approximately 15:48 UTC, direct retrieval was repeated: HTML SHA-256 `0a1b90451b558f665f677b5643b46c2d8d1aee86bb397cc6b25f103b83c1ec0b`; the HTML-unescaped Event rules-description SHA-256 is `5097d79890c35b3020cc654609f93f757bb5422ed5f449a0309205e2561e1fcb`. Sections III–VII, IX and XI were inspected. The verified deliverable/date guidance still agrees with CONTEST.

The root Event's `endDate` reflected retrieval time, while nested events carried a timezone-free `2026-10-14T09:00:00`. Neither establishes a supported cutoff timezone; do not turn that metadata into a deadline claim. The returned page contains a client-loaded application shell and public rules metadata, not an inspected submission form. Separate announcements/form fields were not established through this retrieval or the browser/search extractor. A final rendered-page/form check remains pending; this does not establish that no newer announcements exist.

On 2026-10-08 at approximately 11:18 UTC, direct retrieval before the refreshed package review produced HTML SHA-256 `3ac894f6a746662544072bdbfa9997297ce909623ac925a8cfb9de0c286563bf`. The HTML-unescaped rules-description hash still matches `5097d79890c35b3020cc654609f93f757bb5422ed5f449a0309205e2561e1fcb`; the inspected content and CONTEST requirements are unchanged. The browser extractor still returned 404. A fresh unauthenticated Chromium inspection also reached the rendered [official announcements page](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/news/), which displayed no announcements at that inspection. The public home page exposes registration buttons; no registration action was clicked and no account or submission form was used. The rendered [public FAQ](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/faq/) contains generic submission/edit/support guidance; it does not resolve the inspected cutoff, upload-limit or originality questions. Authenticated form details and team registration confirmation remain pending.

Retrieval snapshots remain temporary investigation files, not committed copies of the rules. To recheck from a shell:

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

### INT-03 apply source recheck

Re-fetched and inspected the five pinned documents on 2026-10-07. The candidate/window/runtime assumptions above remain supported at those revisions. No model/HEF was downloaded or executed.

| Pinned document | Retrieved SHA-256 |
| --- | --- |
| HailoRT README | `bf2d5a62e9b9698b5f97739e16d582af8afa10986f5bb070f273d025c036599f` |
| Hailo Apps prerequisites | `28039870709fd220c11aaec11ea7b2500e2e61852fc162126687cf33eec168b4` |
| Hailo Apps installation | `33517103049a7a6ed288202c173a8913a17e09e92e92eccd0e84a56a83fc79eb` |
| Hailo-10H pose table | `024583a942e9e2982676087cf0d2f0661e27d78ab87cc4bb764d1ac1ce1b4145` |
| GenAI model table | `14e6d96913d3066be56483e93bd7fe3e7602a72da94e5ce9ecb8018b86cf9af5` |

The prerequisites link to Hailo-8/PCIe-oriented installation guidance, despite the selected Hailo-10H USB device. That is a compatibility gap to resolve with official USB-specific guidance, not permission to install those drivers here. [HARDWARE.md](HARDWARE.md) defines the readiness/run procedure; actual observations remain in STATUS.

The speech path's windowing and both producers' device contention need measurement before tuning engagement staleness. Shared capture-time and adapter cleanup contracts stay in [ARCHITECTURE.md](ARCHITECTURE.md); this research changes no contracts or producer implementation.

## Rules recheck for Stage I CPU direction — 2026-10-09

Official source: https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/
Direct `curl --fail --location` response retrieved and embedded JSON-LD rules
content inspected after web extraction failed with 404. Response SHA-256:
`48d4f5ce771f478f18b03faa947e5693ddbb44356777fc00215a8eef804813d3`.
The temporary response stays outside Git; it contains public rules, not private
registration data. Sections V/VI retain ordinary Stage I hosts, later selected
platform validation, English deck (20 main pages) and mainly English video
explanation (three minutes recommended). No final video, authenticated form,
announcement or receipt was validated in this recheck.
The October 14 deadline is unchanged; exact form cutoff remains unconfirmed.

Maintainer direction is separate provenance: no team UGen300 access before
qualification; Lucas likely operator; English product/rehearsal after canceling
the Mandarin/zh-TW proposal.
It does not establish actual CPU/model performance or override official rules.

## Public rules recheck — 2026-10-10

Direct HTTPS retrieval of the official home page produced HTML SHA-256
`ac46e9644ad46887e4ca49bdc9004abce815496173392acf1de8c5a495a21524`.
The HTML-unescaped Event description in its JSON-LD graph still hashes to
`5097d79890c35b3020cc654609f93f757bb5422ed5f449a0309205e2561e1fcb`.
Sections III–VII, IX and XI were inspected; recorded Stage I date, English
deck/video requirements, page budget and Stage II distinction are unchanged.
The web extractor could not access the home/news/FAQ pages; that failure was
not treated as source verification. This direct rules check does not inspect
authenticated submission fields, confirm registration or resolve precise cutoff
time/timezone and originality interpretation. Temporary retrieval files remain
outside Git.

A separate unauthenticated Chromium inspection reached the rendered public
announcements and FAQ pages. Announcements displayed none at inspection; the FAQ
provides generic editing/receipt/support guidance and does not resolve the cutoff,
upload-limit or originality questions. No registration button was activated and
no account, submission form or receipt was accessed.
