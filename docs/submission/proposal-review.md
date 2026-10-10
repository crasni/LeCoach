# Proposal artifact evidence — 2026-10-10

This record describes the replacement [editable proposal](proposal.fodp) and
[matching PDF](proposal.pdf), prepared for [#34](https://github.com/crasni/LeCoach/issues/34)
under the existing [INT-03 spec](../../openspec/changes/int-03-submission-and-hardware-evidence/proposal.md).
It identifies this artifact revision and its evidence. Live assignments,
acceptance and remaining package work stay in Issues #34/#12/#11/#20/#21.
The older `readiness.md` describes its own historical artifact hashes and does
not certify this replacement. Integration reviews the complete package.

## Authoring and artifact identity

The human collaborator explicitly requested Codex authoring instead of Claude
in the working session. [The Issue clarification](https://github.com/crasni/LeCoach/issues/34#issuecomment-6096741945)
records that direction. Codex wrote the English copy/layout. No Claude use or
output is claimed. Integration/maintainer content and visual acceptance remains
separate from this authoring-tool direction.

The deck contains **15 main pages**, including its cover and reference page,
with no appendix. The 16:9 source contains editable text, four native tables,
and ten native connectors for the workflow and architecture. Two embedded
illustrative assets accompany those objects. Table objects also have conversion
fallback images, which do not replace their editable cells.

| Artifact | Bytes | SHA-256 |
| --- | ---: | --- |
| `proposal.fodp` | 3,316,857 | `7e62d79281fc69ef528650e1b6f4a7b48914889841dbcb1373930fe97e9b048e` |
| `proposal.pdf` | 561,885 | `9133917f2d8ab821b306050774b8fbafe527490bc2af5fd5c2b14d987d6bf417` |

## Claims and limitations

Sources also appear in the relevant slide notes. All evidence below is dated
2026-10-10 unless its pinned repository revision supplies the attribution.

| Pages | Claim / source | Boundary |
| --- | --- | --- |
| 1–2, 12 | [Product scope](https://github.com/crasni/LeCoach/blob/ff24d09/GUIDE.md): private workplace rehearsal, specific next action, proposed pilot | Intended benefit and evaluation. No user study, market-size, paid deployment, revenue or learning-outcome claim. |
| 3 | Actual audience-panel screenshot from a preserved `b419a61` frontend preview, captured locally with `weak_to_improved` | Authored synthetic input, computed audience, devices off, default 5× replay. Only the audience panel appears. It does not show live capture or generated coaching. |
| 4–5, 7–8, 11 | [Architecture](https://github.com/crasni/LeCoach/blob/ff24d09/docs/ARCHITECTURE.md), [implementation](https://github.com/crasni/LeCoach/tree/ff24d09/src/lecoach), [coaching behavior](https://github.com/crasni/LeCoach/blob/ff24d09/src/lecoach/coaching/README.md) | Local CPU composition, one engine/recorder, canonical observations, in-memory session retention and raw recording off by default. No security audit, recognition accuracy, eye tracking or emotion detection. Filler recall remains under investigation. |
| 6 | [Computed synthetic scenario](https://github.com/crasni/LeCoach/blob/ff24d09/checks/coaching/demo/README.md) | Generated coaching at capture anchors 10/25/40 s, distinct from smoothed audience decisions. Synthetic values only. At 40 s, facing support comes from cited `vision-35`, not uncited `vision-40`. |
| 9 | [Actual limited pickup, source 225550f](https://github.com/crasni/LeCoach/issues/20#issuecomment-6096660374), [consumer assessment](https://github.com/crasni/LeCoach/issues/20#issuecomment-6096693124) | Headless 22.6512 s CPU session on the confirmed Ubuntu host. One improvement at 4 s, decision at 7.024865682 s, four cited vision windows. No usable speech, partial camera coverage, no scripted presenter/browser capture or strength/recovery acceptance. Reviewed public sanitized evidence only. |
| 10 | [Isolated vision timings, source 81dead7](https://github.com/crasni/LeCoach/issues/16#issuecomment-6096632027) | Three fresh 5 s camera sessions on Ubuntu 26.04.1 / Ryzen AI 7 450 / about 30 GiB RAM. Prepared model, camera 0, unchanged VisionConfig. All release checks true and read/inference errors zero. Startup/open/FPS/release endpoints do not establish concurrent speech/vision or capture-to-browser latency. |
| 11 | [Operator functional report](https://github.com/crasni/LeCoach/issues/11#issuecomment-6095334266) | Attributed Ubuntu/Bluetooth microphone report covering transcription/camera/audience, stop/feedback, repeat/release, short/no-person and missing microphone. This author did not repeat the device run. No quantified accuracy or final presenter/coaching acceptance. |
| 13 | [309-word CPU narration](https://github.com/crasni/LeCoach/blob/1f4607a/checks/coaching/demo/narration.md), [scenario](https://github.com/crasni/LeCoach/blob/ff24d09/checks/coaching/demo/README.md) | Proposed 175 s shot plan. Revised reading/per-slot holds/final edit remain unmeasured. Earlier approximately 2:20 timing belongs to the old 316-word script. Actual shots need their own supported observations. |
| 14 | [Hardware readiness](https://github.com/crasni/LeCoach/blob/ff24d09/docs/HARDWARE.md), [source hierarchy](https://github.com/crasni/LeCoach/blob/ff24d09/docs/SOURCES.md) | Stage I local CPU. UGen300 is unmeasured and remains Stage II after qualification. No target USB/runtime/model compatibility or performance claim. |
| 1, 13–15 | [Official competition rules](https://contest.bhuntr.com/tw/39jg9vimiynrhlksze/home/), retrieved 2026-10-10 | Embedded JSON-LD rules inspected after web extraction failed. English proposal, at most 20 main pages, required content/repository references, mainly English video with approximately three-minute guidance. Team track choice comes from #12/#34. This export is not registration, upload or a submission receipt. |

## Visual asset provenance

- Cover: generated conceptual editorial illustration using the built-in OpenAI
  imagegen tool. No real presenter, rehearsal, hardware result or product UI is
  depicted. The image is embedded in the editable source, not an external link.
  Prompt: “Create a sophisticated editorial illustration for a competition proposal
  slide, widescreen 16:9 composition. LeCoach is private presentation rehearsal on a
  local laptop. An adult workplace presenter stands near a desk practicing a talk
  to an open laptop in a quiet uncluttered room; a subtle small audience of simplified
  human silhouettes is visible ONLY within the laptop screen. Calm warm ivory
  background (#F4F1E8), deep ink navy, muted teal and one restrained coral accent.
  Flat print illustration with soft grain, strong simple silhouettes, elegant
  negative space, not photorealistic, no camera surveillance imagery, no robots,
  no circuitry, no cloud, no text, no logos. Subject and desk placed on the RIGHT
  half, LEFT half almost entirely empty warm ivory for editable slide title.
  Laptop UI is conceptual and abstract; do not fabricate detailed product features.
  Landscape high resolution.”
- Audience screenshot: actual delivered application rendering with synthetic
  fixture observations. It contains no private person, transcript, session export
  or raw microphone/camera media. Its explicit mode caption stays visible.
- Workflow/architecture and data tables: native editable slide objects.

## Export and verification

Authoring used JavaScript `@oai/artifact-tool` with Arial, verified installed on
the macOS arm64 authoring host. A private intermediate PPTX passed package,
15-slide geometry/font/native-table and first-party import checks with zero
findings/warnings. LibreOffice converted that intermediate to the requested
FODP. The FODP is the delivered editable source and sole source for the PDF.
Private intermediate files and validation outputs remain outside the staged scope.

Exporter: **LibreOfficeDev 26.8.0.0.alpha0, AARCH64**, build
`2c87e51eeaa2b413ff4ae097b2705eea1995d8e5`. PDF: 15 pages, 960.009 × 540 pt,
PDF 1.7, no encryption. Export emitted only Fontconfig cache warnings.
Every final page was rendered at 1600 px and individually inspected for clipping,
wrapping, contrast, arrow direction and table values. Corrected screenshot crop,
flow arrows and reference contrast before final export.

Reproduce an export to a **new directory**, leaving the tracked PDF untouched:

```sh
mkdir -p /tmp/lecoach-proposal-review
soffice --headless -env:UserInstallation=file:///tmp/lecoach-proposal-review-profile \
  --convert-to pdf --outdir /tmp/lecoach-proposal-review docs/submission/proposal.fodp
pdfinfo /tmp/lecoach-proposal-review/proposal.pdf
pdftoppm -scale-to 1600 -png /tmp/lecoach-proposal-review/proposal.pdf \
  /tmp/lecoach-proposal-review/page
shasum -a 256 docs/submission/proposal.fodp docs/submission/proposal.pdf
git diff --check
```

Re-exported PDF bytes can differ because of document creation timestamps or
exporter versions. Verify content/pages/links against the editable source rather
than requiring byte equality for a later export. The hashes above identify the
reviewed pair.

The following read-only check uses `pypdf` from an artifact-tool environment. It
does not require adding a dependency to the application manifest or lockfile:

```python
import collections
import re
import unicodedata
import xml.etree.ElementTree as ET
from pypdf import PdfReader

ns = {
    'office': 'urn:oasis:names:tc:opendocument:xmlns:office:1.0',
    'draw': 'urn:oasis:names:tc:opendocument:xmlns:drawing:1.0',
    'presentation': 'urn:oasis:names:tc:opendocument:xmlns:presentation:1.0',
    'text': 'urn:oasis:names:tc:opendocument:xmlns:text:1.0',
    'xlink': 'http://www.w3.org/1999/xlink',
}
pages = ET.parse('docs/submission/proposal.fodp').findall(
    './office:body/office:presentation/draw:page', ns)
pdf = PdfReader('docs/submission/proposal.pdf')
assert len(pages) == len(pdf.pages) == 15
def words(text):
    return collections.Counter(re.findall(r'\S+', unicodedata.normalize('NFKC', text)))
source_links = set()
pdf_links = set()
for page, output in zip(pages, pdf.pages):
    notes = page.find('presentation:notes', ns)
    assert notes is not None
    page.remove(notes)
    paragraphs = page.findall('.//text:p', ns) + page.findall('.//text:h', ns)
    assert words(' '.join(' '.join(p.itertext()) for p in paragraphs)) == words(output.extract_text())
    source_links.update(a.attrib['{'+ns['xlink']+'}href'] for a in page.findall('.//text:a', ns))
    for annotation in output.get('/Annots', []):
        action = annotation.get_object().get('/A', {})
        if action.get('/URI'):
            pdf_links.add(str(action['/URI']))
assert source_links == pdf_links and len(source_links) == 7
print('15 pages: per-page text token parity and 7 hyperlinks match')
```

Fresh artifact checks passed: 15 source/PDF pages, 238 visible source paragraphs
with per-page text-token parity, seven matching HTTPS links, four native tables,
ten connectors, two primary embedded assets and source notes on every page.
The source contains no local file-path reference or auth token. Full app tests
were not rerun for this document-only change. No actual input/model/accelerator,
native interactive edit/reopen, final footage or external delivery was tested by
this author. LibreOffice export and PDF rendering do not establish behavior in
every office application.
