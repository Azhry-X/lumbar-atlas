# Lumbar Spine — Master Clinical Dossier & Companion Test Atlas

**Live Atlas:** https://azhry-x.github.io/lumbar-atlas/  
**Dossier PDF:** [`master_lumbar_dossier.pdf`](./master_lumbar_dossier.pdf) — 9 pages, A4 portrait, built for Apple Pencil in Notability / GoodNotes.

Sister projects:
- [Knee Complex dossier + atlas](https://github.com/Azhry-X/knee-atlas) — same design system, same page architecture.
- [Ankle & Foot dossier + atlas](https://github.com/Azhry-X/ankle-atlas) — same design system, same page architecture.

## What is in the dossier
| Page | Content | Accent |
|---|---|---|
| 1 | Triage, red flags (Cauda equina syndrome / PVR rule, fracture & malignancy Downie post-test probabilities, AAA palpation, Axial SpA ASAS, infection, NICE NG59 imaging rule), pathway router, subjective, pain map | red |
| 2 | Differential matrix (disc/radicular, stenosis, facet/somatic, SIJ, instability, spondylolysis, SpA, visceral/vascular), STarT Back & ÖMPSQ-10 stratification, Cook stenosis cluster, Laslett SIJ cluster, OLHT, Waddell signs, TBC / McKenzie DP, hip/SIJ/neural screen | blue |
| 3 | ROM table (write-in), L2–S1 neurological grid, segmental mobility & PIT reliability, passive lumbar extension test (PLET), Fritz instability predictors, McGill endurance ratios & Sørensen, aberrant movement checklist | blue |
| 4 | Neurodynamic tests (SLR, crossed SLR, slump, femoral stretch / PKB, Achilles reflex), Flynn/Childs manipulation CPR, Hicks stabilisation CPR, PROM dashboard (ODI, RMDQ, NPRS, PSFS, TSK-11, FABQ, PCS, STarT Back) | blue |
| 5 | Post-op: Discectomy, decompression, fusion; incidental durotomy rates; Oosterhuis, McGregor, Greenwood, Afzal, Swespine pre-op activity; wound/neuro/CES re-check; surgeon-directed restrictions | purple |
| 6 | Electrophysical agents & passive modalities: Cochrane traction & ultrasound, NICE NG59 "do not offer" list, ACP 2017 superficial heat, WHO 2023 guideline, dosing log | orange |
| 7 | Manual therapy: Rubinstein SMT, NICE NG59 1.2.7 package rule, Furlan massage, Schneider stenosis RCT, manipulation safety screen & informed consent | teal |
| 8 | Exercise & prevention: Hayden Cochrane & NMA, CFT (RESTORE), WalkBack, Steffens & Shiri prevention RRs, NICE 1.2.2, motor control & Pilates, Sweeney 2026 spondylolysis RTS, 12-week loading log | green |
| 9 | 12-visit flowsheet, discharge summary, objective milestones (ODI/RMDQ/NPRS/PSFS change vs MCID) | slate |

Every statistic carries an evidence marker: **H** high · **M** moderate · **L** low · **E** expert opinion.
Underlined test names open the matching Atlas card; **▸** marks cards with a verified video.

## Repository layout
```
index.html                  Atlas (GitHub Pages entry point) — generated
master_lumbar_dossier.html  Dossier (generated, self-contained CSS)
master_lumbar_dossier.pdf   Dossier PDF (generated)
src/pages/p1.html … p9.html Dossier page bodies  ← edit content here
src/dossier.css             Design system
atlas/data/tests.yaml       Atlas cards: steps, criteria, accuracy, evidence, videos, calculators  ← single source of truth
atlas/build_atlas.py        Builds index.html from tests.yaml (page badges/filters = every dossier page that links the card)
atlas/config.py             Atlas base URL
tools/build_dossier.py      Assembles HTML → PDF → runs every check
tools/render_and_check.py   Page count, overflow, overlap, fonts, required safety strings, previews
tools/check_links.py        Verifies every PDF link, Atlas anchor, card source (DOIs via the DOI registry) and video
tools/required_strings.txt  Safety-critical text that must never disappear
fonts/                      Source Sans 3 (OFL)
```

## Rebuild after an edit
One-time setup (Python 3.10+ and Node.js):
```bash
pip install -r requirements.txt
python -m playwright install chromium
npm install
```
Windows, one command (stops at the first failure):
```powershell
powershell -ExecutionPolicy Bypass -File build.ps1            # Atlas + PDF + all checks + link audit
powershell -ExecutionPolicy Bypass -File build.ps1 -SkipLinks # same, without the network link audit
```
Or step by step on any OS:
```bash
python atlas/build_atlas.py                # Atlas
python tools/build_dossier.py              # Dossier PDF + all checks (exit 1 on any problem)
python tools/check_links.py                # links (add --live after the site is published)
```
The dossier build fails on: page count ≠ 9, content overflowing a page / card / cell, overlapping glyphs,
a character missing from Source Sans 3 (font fallback), malformed tables, leaked markup, internal link targets
under 4 mm, or a missing safety string from `tools/required_strings.txt`.
Page previews are written to `preview/` when poppler (`pdftoppm`) or `pip install pypdfium2 pillow` is available.
Authoring shortcuts in `src/pages/*.html` (expanded at build time):
`<a class="test-link" data-atlas="slr">SLR</a>` · `<a class="info-icon" data-atlas="ces-triage"></a>` ·
`<a class="calc-badge" data-atlas="odi">Calc</a>` · `<a class="guide-badge" href="https://…">NICE NG59</a>`.
An unknown `data-atlas` id stops the build.

## Status
Draft cards under clinical review with open-access citations and video demonstrations.
