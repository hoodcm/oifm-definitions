# Bernardo AI Concordance Project: Context Document

**Created:** 2025-01-22
**Updated:** 2025-01-22
**Purpose:** Capture all context from discussions about Bernardo's AI concordance scoring project and how the IPL/OIFM work fits in.

---

## Project Overview

Bernardo (leader of MGB's AI initiatives) is developing an **"AI Concordance Score"** to evaluate how well chest X-ray AI foundation models perform compared to radiologist interpretations.

### Core Goal
Compare AI-generated CXR findings against radiologist reports to determine:
- What AI is good at detecting
- What AI misses or gets wrong
- Whether AI captures all clinically relevant attributes (size, severity, location, etc.)
- Strengths and weaknesses by finding type

### Data Assets
- **AI outputs:** Draft reports from 6 CXR foundation models (including Harrison.ai)
- **Radiologist reports:** ~300-500 CXR reports from ~4 sites (mainly MGB)
- **Metadata:** DICOM metadata, demographics, etc.
- **Harrison.ai taxonomy:** 241 actionable CXR findings organized by anatomic category

### Timeline
- Target: ~2 months for initial results
- Immediate goal: Annotate ~200 CXR reports using OIFM codes

### Future Applications
- **Assess AI monitoring:** Site dashboard to flag meaningful discrepancies between AI and radiologist
- **Draft report co-pilots:** Leverage this work for another workstream (details TBD)

---

## The Concordance Workflow

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  AI Foundation Model Output      Radiologist Report                 │
│  (6 models, already structured)  (narrative text)                   │
│         │                               │                           │
│         │                               ▼                           │
│         │                      ┌─────────────────┐                  │
│         │                      │ LLM Extraction  │                  │
│         │                      │ → OIFM JSON     │                  │
│         │                      └────────┬────────┘                  │
│         │                               │                           │
│         │                               ▼                           │
│         │                      ┌─────────────────┐                  │
│         │                      │ Fellow Review   │                  │
│         │                      │ (validation)    │                  │
│         │                      └────────┬────────┘                  │
│         │                               │                           │
│         ▼                               ▼                           │
│  ┌─────────────────┐          ┌─────────────────┐                  │
│  │ AI Findings     │          │ Validated Rad   │                  │
│  │ (model-specific │          │ Findings        │                  │
│  │  taxonomy)      │          │ (OIFM codes)    │                  │
│  └────────┬────────┘          └────────┬────────┘                  │
│           │                            │                            │
│           └──────────┬─────────────────┘                            │
│                      ▼                                              │
│      ┌──────────────────────────────────────┐                      │
│      │  CROSSWALK: AI taxonomy ↔ OIFM       │                      │
│      │  (Common vocabulary for comparison)  │                      │
│      └──────────────────────────────────────┘                      │
│                         │                                           │
│                         ▼                                           │
│           ┌─────────────────────────────┐                          │
│           │ Finding-by-Finding          │                          │
│           │ Concordance Scoring         │                          │
│           │ • Detection match?          │                          │
│           │ • Attributes complete?      │                          │
│           │ • Location correct?         │                          │
│           │ • Weighted by criticality   │                          │
│           └─────────────────────────────┘                          │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Harrison.ai Finding Taxonomy (Bernardo's Spreadsheet)

Bernardo shared an Excel spreadsheet containing Harrison.ai's 241 CXR finding types.

### Structure
- **Columns:** Category, Finding, CDE Codes, Characteristics, Chronicity, Temporality, Location, Stability, Size, Criticality, Actionable vs. Non-actionable Finding
- **CDE Codes column:** Empty (0/241 filled) — needs OIFM mapping
- **Attribute columns:** Sparsely populated (13.7% have characteristics, 2.9% have chronicity)

### Categories and Counts
| Category | Finding Count |
|----------|---------------|
| Lines, Tubes, Devices | 61 |
| Chest Walls | 57 (+7 in variant spelling) |
| Bones | 44 |
| Lungs | 40 |
| Abdomen | 15 |
| Pleura | 10 |
| Technical Factors | 7 |
| **Total** | **241** |

### Sample Findings by Category

**Lungs (40):** air space opacity, aspiration, atelectasis, bronchiectasis, bullous disease, cavitating mass, consolidation, emphysematous changes, fibrosis, hilar lymphadenopathy, hyperinflation, interstitial thickening, lobar collapse, lung nodule, mass, pneumonia, pulmonary contusions, pulmonary edema, pulmonary hemorrhage, scarring, etc.

**Bones (44):** clavicle fracture, rib fracture, scapula fracture, humerus fracture, compression deformity, degenerative change, DISH, osteopenia, scoliosis, bone lesion, shoulder dislocation, etc.

**Chest Walls (57+7):** cardiomegaly, aortic calcification, cardiac silhouette enlargement, emphysema, mediastinal mass, pericardial effusion, pneumomediastinum, pulmonary artery enlargement, pulmonary embolus, tracheal deviation, etc.

**Lines, Tubes, Devices (61):** central venous catheter, chest tube, endotracheal tube, nasogastric tube, pacemaker, ICD, LVAD, ECMO catheter, tracheostomy tube, various surgical hardware, etc.

**Pleura (10):** pleural effusion, pneumothorax, pleural thickening, pleural mass, loculated effusion, hydrothorax, etc.

### Attributes with Existing Values
- **Characteristics:** Defined for ~33 findings (e.g., cardiac silhouette → "enlarged, dilated"; tubes → "in position, suboptimal")
- **Chronicity:** Defined for 7 findings (fractures → "acute, chronic"; consolidation → "acute, chronic")
- **Location:** Defined for 4 findings
- **Stability:** Defined for 1 finding

---

## What Michael/Tarik Bring to the Table

### 1. OIFM Code Registry
- **Location:** `github.com/openimagingdata/findingmodels`
- **Content:** 2000+ finding definitions in `defs/*.fm.json`
- **Schema:** `schema/finding_model.schema.json`
- **Tools:** 
  - `findingmodel` Python package
  - `Index.search()` / `Index.get()` for lookup
  - `create_info_from_name()` for AI-generated descriptions
  - `add_ids_to_model()` for minting new codes with org prefix (e.g., `OIFM_MGB_######`)

### 2. LLM Extraction Methodology
- Sentence-by-sentence extraction from narrative reports
- Near-deterministic fidelity (refined over several months)
- Outputs OIFM-structured JSON with text provenance
- Two-layer architecture: extraction (deterministic) → validation (human review)

### 3. Sample Data / Demo
- Imaging Problem List demo: `imaging-problem-list.pages.dev`
- Sample CXR report + corresponding JSON: `github.com/openimagingdata/imaging-problem-list/tree/main/sample_data/example2`
- Sentence-to-finding highlight function in viewer

### 4. Existing CXR OIFM Code Coverage
From sample JSON, codes already exist for:
- cardiomegaly (OIFM_GMTS_022537)
- pneumonia (OIFM_CDE_000076)
- pneumothorax (OIFM_GMTS_023339)
- pleural effusion (OIFM_GMTS_015972)
- clavicle fracture (OIFM_OIDM_842151)
- rib fracture (OIFM_MGB_944849)
- DISH (OIFM_OIDM_990401)
- mitral annular calcification (OIFM_OIDM_159498)
- coronary artery calcifications (OIFM_MSFT_430810)
- osteopenia (OIFM_GMTS_010762)
- vertebral compression fracture (OIFM_GMTS_009850)
- And many more...

Estimated coverage: 60-70% of Harrison.ai's 241 findings already have OIFM codes; remainder needs creation (mostly device-specific findings).

---

## Bernardo's Questions (Pre-Meeting)

### Q1: CSV → Viewer Format Script
**Question:** Do you have a script to convert CSV (MRN, ACC, Report) into the viewer's folder structure?

**Answer:** No published script exists. Trivial to create (~30 lines of Python). The viewer folder structure is `patients/{id}/exams/{id}/report.txt`. Not required for annotation workflow—can work directly from CSV.

### Q2: OIFM Code Definitions Location
**Question:** Where are codes stored? How to edit/add?

**Answer:** 
- Canonical source: `github.com/openimagingdata/findingmodels`
- Definitions: `defs/*.fm.json`
- Schema: `schema/finding_model.schema.json`
- To add: Create `.fm.json` file → run validator → submit PR
- Programmatic: Use `findingmodel` package to mint new IDs with org prefix

### Q3: LLM Extractor Status
**Question:** Was demo data manual or LLM-extracted? Is there a working extractor?

**Answer:** Working extractors exist with high fidelity. [Clarify demo data provenance in meeting.]

### Q4: Annotation Interface
**Question:** Is there a tool to encode 200 CXR reports into OIFM codes? Prefers report-level annotation over LLM extraction validation.

**Answer:** No dedicated interface. Options:
- **Spreadsheet:** Fast to build, familiar to fellows
- **LLM pre-extraction + validation:** Faster than de novo annotation (3-5x)
- **Parallel paths:** Fellow manually annotates subset (gold standard) + LLM extracts all → compare outputs

---

## Annotation Workflow Options

### Option A: Pure Manual Annotation (Bernardo's Stated Preference)
- Fellow reads raw report → assigns OIFM codes manually
- No LLM in the loop
- Cleaner ground truth, but slower
- Interface: Structured spreadsheet with constrained attribute values

### Option B: LLM Extraction + Validation
- LLM extracts findings from reports → outputs OIFM-structured JSON
- Fellow reviews/corrects extractions
- Faster (validation vs. creation from scratch)
- Potential concern: LLM bias in ground truth

### Option C: Parallel Paths (Recommended)
- Fellow manually annotates subset (~50 reports) as pure gold standard
- LLM extracts all 200 reports
- Compare manual annotations to LLM extractions
- **Benefits:**
  - Creates gold standard ground truth
  - Validates LLM extraction methodology on CXR specifically
  - Gives Bernardo comparison data (manual vs. automated accuracy)
  - Showcases extraction capability

---

## Division of Responsibilities

### Michael/Tarik Provide:
- OIFM code mapping for 241 Harrison.ai findings
- New OIFM codes for findings not yet in registry
- Attribute schema with constrained values per finding type
- LLM extraction capability (if desired)
- CSV ingestion script (trivial)
- Annotation spreadsheet template design

### Bernardo Provides:
- 300-500 CXR reports from ~4 sites
- AI outputs from 6 foundation models
- Fellow annotation time
- Concordance scoring methodology and weights
- Criticality/actionability classifications
- Assess AI monitoring framework design

### Shared Outcome:
- Validated extraction methodology for CXR reports
- Ground truth dataset for AI concordance evaluation
- Publication-worthy multi-model comparison
- Foundation for Assess AI monitoring component

---

## Key Decisions to Confirm in Meeting

1. **Annotation approach:** Manual only (Option A) vs. LLM-assisted (Option B) vs. parallel paths (Option C)?

2. **Scope of OIFM mapping:** Just Harrison.ai's 241 findings, or expand to include additional findings from OIFM registry?

3. **Attribute schema depth:** Which attributes matter most for concordance scoring? (Criticality, actionability, size, location, chronicity?)

4. **Validation interface:** Spreadsheet sufficient, or need something more structured?

5. **Timeline alignment:** What's the critical path for 2-month delivery?

6. **Data sharing:** When can Michael receive sample reports to test extraction?

---

## Strategic Value for Michael

### Immediate Benefits
- Real-world validation of extraction methodology on CXR reports
- Collaboration with MGB AI leadership
- Potential co-authorship on concordance study

### Longer-Term Benefits
- OIFM adoption within MGB AI infrastructure
- Connection to Assess AI monitoring platform
- Foundation for draft report co-pilot work
- Demonstrates extraction capability to key stakeholders

### Competitive Positioning
- Bernardo expressed concern about LLM extraction fidelity—unaware of Michael's refined methodology
- Opportunity to demonstrate near-deterministic extraction quality
- Establishes Michael as the extraction expert within MGB ecosystem

---

## Open Questions

1. What is the exact provenance of the demo data (manual vs. LLM-extracted)?

2. How much of the 241 Harrison.ai findings already have OIFM codes? (Estimated 60-70%, needs verification)

3. What org prefix should be used for new MGB-specific codes?

4. Does Bernardo want to use the IPL viewer, or just the underlying data structures?

5. What format are the 6 foundation model outputs in? Do they use Harrison.ai's taxonomy or something different?

6. How will the concordance weights be determined? (Clinical consensus? Literature-based? Data-driven?)

---

## OIFM Infrastructure: Two-Repository Architecture

The OIFM ecosystem consists of two separate repositories that work together:

### Repository 1: `findingmodel` (Python Library)

**Location:** `/Users/michael/GitHub/findingmodel/` (this workspace)

**Purpose:** Python 3.11+ library for working with Open Imaging Finding Models

**Key Components:**

| Directory | Contents |
|-----------|----------|
| `src/findingmodel/` | Core package (models, tools, config, CLI) |
| `src/findingmodel/tools/` | LLM workflows for finding model creation |
| `test/` | pytest tests + fixtures |
| `notebooks/` | Demo notebooks |

**Core Modules:**
- `finding_model.py` — Pydantic models (`FindingModelBase`, `FindingModelFull`, `ChoiceAttribute`, `NumericAttribute`)
- `finding_info.py` — Finding information container
- `index.py` — DuckDB-based index with ID generation and search
- `tools/` — AI-assisted workflows for creating/enriching finding models

**OIFM Code Generation** (in `src/findingmodel/index.py`):
```python
# ID Patterns
OIFM_{SOURCE}_{6_DIGITS}      # Model ID (e.g., OIFM_MSFT_932618)
OIFMA_{SOURCE}_{6_DIGITS}     # Attribute ID (e.g., OIFMA_MSFT_463871)
OIFMA_{SOURCE}_{6_DIGITS}.{N} # Value code (e.g., OIFMA_MSFT_463871.0)

# Key methods in DuckDBIndex class:
generate_model_id(source: str) -> str           # Line ~1508
generate_attribute_id(source: str) -> str       # Line ~1556
add_ids_to_model(model, source: str) -> FindingModelFull  # Line ~1632
```

**Finding Creation Pipeline** (in `src/findingmodel/tools/`):
1. `create_info_from_name(finding_name)` → `FindingInfo` with description/synonyms
2. `create_model_stub_from_info(info, tags)` → `FindingModelBase` with standard attributes
3. `add_ids_to_model(model, source)` → `FindingModelFull` with all OIFM codes
4. `add_standard_codes_to_model(model)` → Adds RadLex/SNOMED index codes

### Repository 2: `findingmodels` (Data Registry)

**Location:** `/Users/michael/GitHub/findingmodels/`

**Purpose:** Canonical collection of 2,149 OIFM finding definitions

**Key Components:**

| Directory | Contents |
|-----------|----------|
| `defs/` | 2,149 finding model JSON files (`*.fm.json`) |
| `text/` | 2,150 auto-generated markdown docs |
| `schema/` | JSON schema + documentation |
| `lists/` | Curated finding lists and gamuts |
| `scripts/` | Validator and processing scripts |
| `conflicts/` | Merge staging area |

**Schema Location:** `schema/finding_model.schema.json`

**Example Finding Model** (`defs/abdominal_abscess.fm.json`):
```json
{
  "oifm_id": "OIFM_GMTS_004244",
  "name": "abdominal abscess",
  "description": "A localized collection of pus in the abdomen",
  "synonyms": ["intra-abdominal abscess"],
  "tags": ["CT", "US", "abdomen"],
  "contributors": [
    {"name": "Radiology Gamuts Ontology", "code": "GMTS", "url": "https://gamuts.net/"}
  ],
  "attributes": [
    {
      "oifma_id": "OIFMA_GMTS_384452",
      "name": "presence",
      "type": "choice",
      "values": [
        {"value_code": "OIFMA_GMTS_384452.0", "name": "absent"},
        {"value_code": "OIFMA_GMTS_384452.1", "name": "present"},
        {"value_code": "OIFMA_GMTS_384452.2", "name": "indeterminate"}
      ]
    }
  ],
  "index_codes": [
    {"system": "SNOMED", "code": "705057003", "display": "Presence (property)"}
  ]
}
```

**OIFM ID Sources in Registry:**
- `OIFM_GMTS_*` — Radiology Gamuts Ontology (2,100+ findings)
- `OIFM_MSFT_*` — Microsoft-contributed findings
- `OIFM_CDE_*` — ACR/RSNA Common Data Elements
- `OIFM_OIDM_*` — Open Imaging Data Model custom definitions
- `OIFM_MGB_*` — MGB-specific findings

**Validation Workflow:**
```bash
# In findingmodels repo
uv run scripts/validator.py  # Validates JSON, generates markdown, updates indices
```

---

## CXR Finding Lists Comparison

Three distinct CXR finding lists exist that need reconciliation:

### List 1: Bernardo's Harrison.ai Taxonomy (241 findings)

**Source:** `chest_xr_structured_findings(Findings) (1).xlsx`

| Category | Count | Examples |
|----------|-------|----------|
| Lines, Tubes, Devices | 61 | ETT, NGT, chest tube, pacemaker, ECMO, LVAD, ICD |
| Chest Walls | 57+ | cardiomegaly, aortic calcification, pneumomediastinum |
| Bones | 44 | rib fracture, clavicle fracture, scoliosis, DISH |
| Lungs | 40 | consolidation, atelectasis, nodule, mass, edema |
| Abdomen | 15 | hiatus hernia, free gas, distended bowel |
| Pleura | 10 | effusion, pneumothorax, thickening |
| Technical Factors | 7 | rotated, underexposed, underinflation |
| **Total** | **241** | |

**Columns in spreadsheet:**
- `Category` — anatomic/functional grouping
- `Finding` — finding name
- `CDE Codes` — **EMPTY (0/241)** ← needs OIFM mapping
- `Characteristics` — sparse (13.7% populated)
- `Chronicity` — sparse (2.9% populated, e.g., "acute, chronic")
- `Temporality`, `Location`, `Stability`, `Size` — very sparse
- `Criticality`, `Actionable vs Non-actionable` — clinical priority

**Key insight:** Bernardo needs the `CDE Codes` column populated with OIFM codes.

### List 2: Hood-Curated CXR Findings (~170 findings)

**Source:** `CXR complete findings (Hood curated)/`

| File | Count | Focus |
|------|-------|-------|
| `lung_CXR_findings.md` | 61 | Parenchymal, airspace, nodules |
| `osseous_CXR_findings.md` | 46 | Ribs, spine, shoulder |
| `mediastinal_CXR_findings.md` | 30 | Cardiac, aortic, hilar |
| `technique_CXR_findings.md` | 24 | Positioning, exposure, artifacts |
| `stripes_CXR_findings.md` | 16 | Mediastinal lines/stripes |
| `softtissue_CXR_findings.md` | 8 | Soft tissue, breast |
| **Total** | **~185** | |

**Sample findings (lung):**
- Clear lungs, Lobar consolidation, Diffuse consolidation
- Multifocal airspace opacities, Focal airspace opacity
- Reticulonodular opacity, Interstitial thickening
- Pulmonary nodule, Solitary pulmonary nodule, Multiple pulmonary nodules
- Kerley A lines, Kerley B lines, Air bronchograms
- Lobectomy, Pneumonectomy, Wedge resection

**Sample findings (stripes):**
- Normal/Abnormal azygoesophageal line
- Normal/Abnormal right/left paratracheal stripe
- Normal/Abnormal posterior/anterior junction line
- Normal/Abnormal right/left paraspinal line

### List 3: Existing OIFM Registry CXR Coverage

**Source:** `findingmodels/defs/*.fm.json` (2,149 total, subset CXR-relevant)

Known CXR codes already in registry:
- cardiomegaly (`OIFM_GMTS_022537`)
- pneumonia (`OIFM_CDE_000076`)
- pneumothorax (`OIFM_GMTS_023339`)
- pleural effusion (`OIFM_GMTS_015972`)
- clavicle fracture (`OIFM_OIDM_842151`)
- rib fracture (`OIFM_MGB_944849`)
- DISH (`OIFM_OIDM_990401`)
- mitral annular calcification (`OIFM_OIDM_159498`)
- coronary artery calcifications (`OIFM_MSFT_430810`)
- osteopenia (`OIFM_GMTS_010762`)
- vertebral compression fracture (`OIFM_GMTS_009850`)

**Estimated coverage:** 60-70% of Harrison.ai findings likely have existing OIFM codes.

### Comparison Matrix

| Aspect | Bernardo (Harrison.ai) | Hood-Curated | OIFM Registry |
|--------|------------------------|--------------|---------------|
| **Total findings** | 241 | ~185 | 2,149 (all) |
| **Device coverage** | Comprehensive (61) | Minimal (8) | Moderate |
| **Lung findings** | General (40) | Granular (61) | Good |
| **Mediastinal stripes** | None | Comprehensive (16) | Unknown |
| **Technique findings** | Basic (7) | Detailed (24) | Minimal |
| **Attributes defined** | Sparse (13.7%) | None | Full schema |
| **OIFM codes** | Empty | None | Complete |

### Key Differences

1. **Bernardo's list** emphasizes devices (61 items) — Hood's list has minimal device coverage
2. **Hood's list** includes mediastinal stripes/lines (16 items) — unique to CXR interpretation
3. **Hood's list** is more granular (e.g., "lobar consolidation" vs "diffuse consolidation")
4. **Bernardo's list** has attribute hints in columns (characteristics, chronicity) — useful for schema design

---

## Recommended Path Forward

### Priority 1: Map Bernardo's 241 Findings to OIFM Codes

**Goal:** Populate the empty `CDE Codes` column in Bernardo's spreadsheet

**Steps:**
1. Export Bernardo's 241 finding names
2. Search existing OIFM registry (`findingmodels/defs/`) for matches
3. For matches: assign existing OIFM code
4. For gaps: generate new OIFM codes using `findingmodel` library with `OIFM_MGB_*` prefix

**Estimated breakdown:**
- ~145 findings (60%) — likely have existing OIFM codes
- ~60 findings (25%) — need new codes (mostly devices)
- ~36 findings (15%) — may need review/consolidation

### Priority 2: Generate Missing OIFM Codes

**Focus areas (highest gap likelihood):**
- Lines, Tubes, Devices (61 items) — many device-specific findings
- Technical Factors (7 items) — limited coverage in registry

**Code generation approach:**
```python
from findingmodel import DuckDBIndex

index = DuckDBIndex()
new_model = index.add_ids_to_model(finding_model_base, source="MGB")
# Returns FindingModelFull with OIFM_MGB_XXXXXX
```

### Priority 3: Reconcile Hood-Curated List (Later)

**Decision:** Hood's list becomes supplementary

**Rationale:**
- Bernardo has immediate need with 2-month timeline
- His list already defines the scope (241 findings)
- Hood's unique contributions (stripes, granular lung findings) can be added to registry separately
- Hood's list valuable for future comprehensive CXR coverage

### Next Steps

1. **Immediate:** Match Bernardo's 241 findings against existing OIFM registry
2. **Generate:** Create new OIFM codes for unmatched findings
3. **Deliver:** Updated spreadsheet with populated `CDE Codes` column
4. **Later:** Merge Hood-curated findings for comprehensive CXR coverage

---

## File Locations Reference

### In `findingmodel` (library) workspace:
- Bernardo's spreadsheet: `chest_xr_structured_findings(Findings) (1).xlsx`
- Hood-curated lists: `CXR complete findings (Hood curated)/*.md`
- This context doc: `bernardo-ai-concordance-context.md`
- OIFM code generation: `src/findingmodel/index.py`
- Finding creation tools: `src/findingmodel/tools/`

### In `findingmodels` (data) repository:
- Finding definitions: `defs/*.fm.json` (2,149 files)
- JSON schema: `schema/finding_model.schema.json`
- Schema docs: `schema/finding_model_schema.md`
- ID mapping: `ids.json`
- Index: `index.md`
- Validator: `scripts/validator.py`
- Gamuts data: `lists/gamuts_jsonl/*.jsonl`

---

## Work Session: 2026-01-22 - OIFM Code Mapping Progress

### What Was Done

1. **Extracted all 241 findings from Bernardo's spreadsheet** (`chest_xr_structured_findings(Findings) (1).xlsx`)
   - Saved to `harrison_findings.json`
   - Categories: Lines/Tubes/Devices (61), Chest Walls (57+7), Bones (44), Lungs (40), Abdomen (15), Pleura (10), Technical Factors (7)

2. **Built OIFM registry lookup** from 2,149 existing finding models
   - Extracted all names and synonyms (4,199 total searchable terms)
   - Saved to `oifm_registry.json` and `oifm_name_lookup.json`

3. **Performed automated matching** (exact + fuzzy with 80% threshold)
   - Initial results: 40 exact matches, 35 fuzzy matches, 166 no matches

4. **Refined with manual mappings** for common findings
   - Added mappings for atelectasis, fibrosis, nodule, etc.
   - Resulted in 69 matched, 172 needing new codes

5. **Reviewed matches and moved low-confidence items**
   - Flagged 21 items as questionable (wrong anatomic region, too specific, different entities)
   - Final high-confidence matches: **48 findings** (19.9%)
   - Needing new codes: **193 findings** (80.1%)

### Key Insight / Decision Point

**The existing OIFM registry is a poor fit for Bernardo's use case.**

Reasons:
- Only 48 out of 241 findings (20%) have reliable matches
- Many existing codes are too specific (e.g., "lobar atelectasis" vs general "atelectasis")
- Existing codes often represent different concepts (e.g., "diaphragmatic hernia" ≠ "hiatus hernia")
- Device/tube coverage is minimal in existing registry (Lines/Tubes/Devices is the largest category needing codes)

**Recommended approach: Create fresh OIFM codes for all 241 Harrison.ai findings**

This ensures:
- Exact semantic match to Bernardo's taxonomy
- Consistent naming conventions across the set
- No confusion from partial/approximate matches
- Clean crosswalk between Harrison.ai taxonomy and OIFM

### Files Created This Session

| File | Contents |
|------|----------|
| `harrison_findings.json` | All 241 findings extracted from Excel |
| `oifm_registry.json` | 2,149 OIFM codes with names/synonyms |
| `oifm_name_lookup.json` | 4,199 name→ID mappings for search |
| `harrison_matching_results.json` | Initial matching results |
| `harrison_final_categorization.json` | Final categorization (48 matched, 193 needs creation) |

### Next Steps (When Resuming)

1. **Decision needed:** Create fresh codes for all 241 findings, or use the 48 high-confidence matches?

2. **If creating fresh codes for all 241:**
   - Use `OIFM_HAI_*` prefix (Harrison.ai) or `OIFM_MGB_*` prefix?
   - Generate FindingModelBase for each finding
   - Add standard attributes (presence, laterality where applicable, etc.)
   - Assign OIFM IDs using `DuckDBIndex.add_ids_to_model()`

3. **Deliverable:** Updated spreadsheet with `CDE Codes` column populated

### Matching Results Summary

```
Category              | Matched | Needs Code | Total
----------------------|---------|------------|------
Lines, Tubes, Devices |    6    |     55     |   61
Chest Walls           |   18    |     46     |   64
Bones                 |    8    |     36     |   44
Lungs                 |    6    |     34     |   40
Abdomen               |    6    |      9     |   15
Pleura                |    4    |      6     |   10
Technical Factors     |    0    |      7     |    7
----------------------|---------|------------|------
TOTAL                 |   48    |    193     |  241
```

### High-Confidence Matches (48 findings)

These are the findings where existing OIFM codes are semantically equivalent:

**Abdomen (6):** enlarged liver, enlarged spleen, gallstones, liver calcification, pneumobilia, spleen calcification

**Bones (8):** cervical rib, clavicle fracture, DISH, humerus fracture, osteopenia, rib fracture, rib notching, scoliosis

**Chest Walls (18):** breast implant, cardiomegaly, dextrocardia, emphysema, mastectomy, mediastinal shift, mitral annular calcification, pectus carinatum, pectus excavatum, pericardial calcification, pneumomediastinum, pneumopericardium, pulmonary artery enlargement, pulmonary embolus (x3), tracheal mass, tracheomegaly

**Lines/Tubes/Devices (6):** coronary stent, left ventricular assist device, loop recorder, peripherally inserted central catheter, PFO closure device, tracheostomy tube

**Lungs (6):** bronchiectasis, calcified granuloma, hilar lymphadenopathy, pneumonia, pulmonary edema, wedge resection

**Pleura (4):** pleural effusion, pleural mass, pleural thickening, pneumothorax

---

## Work Session: 2026-01-22 (Continued) - Batch OIFM Creation Plan

### Decisions Made

1. **Source code**: `MGB` → IDs will be `OIFM_MGB_NNNNNN`
2. **Output format**: JSON + individual `.fm.json` files for registry submission
3. **Empty attributes**: Add category-specific default attributes

### Batch Creation Script Created

Created `scripts/create_harrison_oifm.py` with:

**Standard Attributes (all findings):**
- `presence`: absent, present, indeterminate (required)
- `change from prior`: new, unchanged, increased, decreased, resolved

**Category-Specific Default Attributes:**

| Category | Additional Attributes |
|----------|----------------------|
| Abdomen (15) | Standard only |
| Bones (44) | laterality, chronicity (for fractures) |
| Chest Walls (64) | laterality, severity (for effusions/enlargement) |
| Lines/Tubes/Devices (61) | position (in position, suboptimal, malpositioned), laterality |
| Lungs (40) | laterality, distribution, location_zone |
| Pleura (10) | laterality, size |
| Technical Factors (7) | severity |

**Finding-Specific Attributes:**
- Parses comma-separated values from harrison_findings.json columns
- characteristics, chronicity, location, stability → converted to ChoiceAttribute

### Files Created

| File | Purpose |
|------|---------|
| `scripts/create_harrison_oifm.py` | Batch creation script |
| `.venv/` | Virtual environment with findingmodel installed |

### Next Steps (When Resuming)

1. **Run the batch script**: `.venv/bin/python scripts/create_harrison_oifm.py`
2. **Verify outputs**:
   - `harrison_oifm_defs/` - 241 individual .fm.json files
   - `harrison_oifm_crosswalk.json` - name → OIFM ID mapping
   - `harrison_findings.json` - updated with cde_codes field
3. **Validate**: Check that all models load correctly and have proper attribute structure
4. **Review**: Spot-check 5-10 findings for semantic accuracy

### Plan File Location

Full implementation plan saved at: `/Users/michael/.claude/plans/dazzling-dreaming-globe.md`
