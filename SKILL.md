---
name: rrcat-tender
description: Generate RRCAT (Raja Ramanna Centre for Advanced Technology) procurement tender specifications following Indian government open-tendering rules. Use when user asks to create a tender specification, tender document, procurement spec, or mentions RRCAT, Raja Ramanna Centre, or Indore tender for atomic/research equipment.
version: 1.5
license: MIT
changelog: |
  ## 1.5 (2026-07-31)
  - Added compliance sheet instruction text section with exact reference text and style notes
  - Added colon to Acceptance Criteria title in formatting rules
  - Added ALMM Enlistment Letter as defensive pattern for solar/PV equipment
  - Added regulatory compliance subsection (2.3) to BQC section
  - Fixed compliance sheet quote style to match reference (single quotes, not double)
  - Fixed accessories table to 2 columns (Item | Specification) matching reference
  - Fixed Acceptance Criteria title to include colon per reference documents
  ## 1.4 (2026-07-31)
  - Rebuilt _template.docx with all 7 sections and pre-populated placeholder tables
  - Template now contains 6 tables ready to fill (was empty single-paragraph)
  - Updated SKILL.md template usage instructions
  ## 1.3 (2026-07-31)
  - Reorganized questionnaire to 7 sections matching tender structure
  - Split "Quality Assurance, Testing & Documentation" into "Bid Evaluation Criteria" and "Acceptance Criteria"
  - Added rejection warning question to Acceptance Criteria section
  - Updated Post-Generation Verification to reference 7 sections
  ## 1.2 (2026-07-31)
  - Added 2 new .docx reference documents (Solar_PV_20kWp_Civil.docx, Cold_Storage_Container_40ft.docx)
  - Updated Formatting Rules with Document Structure section (7-section layout)
  - Added BQC Format, Bid Evaluation List Format, and Acceptance Criteria Format sections
  - Added rejection warning paragraph requirement for Acceptance Criteria
  - Added equipment-type detection entries for solar PV and cold storage
  - Updated Learned Pattern Library with both new documents
  ## 1.1 (2026-07-31)
  - Fixed pandoc reference — officecli is now the sole .docx generation tool (Post-Generation Verification)
  - Normalized compliance sheet instruction text quoting to ASCII double quotes across 6 locations
  - Added AGENTS.md to installed skill distribution
  - Rewrote README.md to reflect OpenCode workflow (removed Gemini/pandoc references)
  ## 1.0 (2026-06-02)
  - Initial release
---

# rrcat-tender Skill

Generate watertight procurement tender specifications for RRCAT, Indore, following Indian government open-tendering rules.

**The real goal:** Eliminate loopholes that let spurious/unqualified bidders win. Protect public money. Get RRCAT exactly what it needs. Avoid retendering and wasted time.

## Prerequisites

### officecli (required)

This skill depends on `officecli` for .docx generation. **Do NOT use pandoc** — it does not preserve the required formatting.

**Install (if not present):**
```powershell
officecli install
```
This installs the binary, skills, and MCP for detected agents.

**Update (if outdated):**
```powershell
officecli --version          # check current version
officecli install            # re-run to update
```

**Verify installation:**
```powershell
officecli --version
officecli help
```

If `officecli` is not recognized, ensure it is in your PATH or run `officecli install` to set up.

### MarkItDown (for /tender-learn)

Miniconda Python with MarkItDown: `pip install 'markitdown[all]'`

## Quick Start

1. User requests tender spec for an equipment type.
2. **Do NOT generate yet.** Act as technical reviewer using the Mandatory Review Checklist below.
3. Ask questions **one at a time** from the checklist. For each question, provide a Recommended Answer (standard range or option) to help the user choose. Only proceed after user confirms or provides their own value.
4. Generate **only after** every checklist item has been explicitly confirmed.
5. Run **Post-Generation Verification** before presenting to user.
6. Use **officecli** to build the `.docx` from the RRCAT template. Do NOT use pandoc — it does not preserve the required formatting. Instead:
   a. Copy `_template.docx` (a blank RRCAT-formatted template) to the output filename.
   b. Use `officecli` to populate all content (tables, paragraphs, headings, bold text) following the **Formatting Rules** below.
   c. Close the file: `officecli close [file].docx`
   d. Verify with: `officecli view [file].docx outline`
7. Present the `.docx` to the user.
8. Run **Sync** between installed skill and workspace.

## Core Behavioral Rules

- **Vendor neutrality** — never use brand names or model numbers. Use generic descriptors (e.g. "High-Precision Multimeter").
- **Zero assumptions** — never auto-calculate safety margins, tolerances, or ratings. Every value from the user.
- **Mandatory clarification pause** — if any critical variable is missing or vague, STOP and ask.
- **Generate only when complete** — do not generate until user has confirmed all details.
- **Compliance sheet mandatory** — Section 7 (Vendor Compliance Sheet (Mandatory)) must be included in EVERY generated tender. Never omit it. Use the **4-column format** (Sr. No. | Parameter | Requirement | Vendor Compliance) with **section header rows** and **sequential numbering** as shown in the Output Template.
- **One question at a time** — present one checklist item, with a recommended answer range/option. Wait for response before proceeding.
- **Incomplete answer retry loop** — if user gives a vague / incomplete answer:
  - 1st time → restate the question with the recommended range, explain why the detail matters.
  - 2nd time → offer a concrete default value: "Shall I proceed with [default]? If not, please specify the exact value."
  - 3rd time → flag the block explicitly: "I cannot generate the tender without this detail. Please provide it or authorize me to use [default]."
  - If user still refuses or cannot provide → note the item as "To Be Confirmed by RRCAT" in the generated document and flag it in the cover note.
- **Defensive procurement writing** — every clause must make it harder for unqualified bidders to fake compliance. If a requirement can be bypassed with "Yes/No/Complied" without supporting evidence, rewrite it to demand verifiable proof (PO copies, completion certificates, OEM auth letters, photos, traceable part numbers).
- **Loophole scan** — before finalizing each generated section, actively look for loopholes a bad actor could exploit. Test each BQC criterion: "Could a low-quality vendor claim compliance here without actually having the capability?" If yes, tighten it.

## Mandatory Review Checklist

Ask every question in the order below. Each question **must** include a recommended answer (standard value, range, or option). Do not proceed to the next question until the current one is confirmed.

**Conditional branching:** Some questions have a "(Skip if...)" note. If the condition is met, skip to the next unskipped question. This avoids asking irrelevant items.

### 1. Basic Tender Metadata

| # | Question | Recommended Answer |
|---|---|---|
| 1.1 | What is the exact item description and quantity required? | User specifies |
| 1.2 | What is the intended application / end-use at RRCAT? | e.g. Cryogenic storage, precision measurement, gas distribution |

### 2. Scope of Supply

| # | Question | Recommended Answer |
|---|---|---|
| 2.1 | List all deliverable line items (main equipment + accessories + spares). | User specifies items, quantities |
| 2.2 | Are mandatory spares / consumables for 2 years operation required? *(Skip if: consumable or single-component item where spares not applicable)* | Yes / No (Recommended: Yes, 10% of critical parts) |
| 2.3 | Is installation, testing & commissioning (ITC) included? *(If No: skip ITC scope line)* | Yes / No (Recommended: Yes) |
| 2.4 | Is training (operator / maintenance) included? *(If No: skip training scope line)* | Yes, at RRCAT facility / No |
| 2.5 | Are civil / utility interface works included? *(If No: skip civil scope line)* | Yes / No (Recommended: No — vendor to provide interface requirements only) |

### 3. Bidder Qualification Criteria (BQC)

| # | Question | Recommended Answer |
|---|---|---|
| 3.1 | Minimum years of experience for the OEM? | 5+ years / 7+ years / 10+ years (Recommended: 5+ years) |
| 3.2 | Minimum number of similar-capacity installations? | 2 / 3 / 5 installations (Recommended: 3) |
| 3.3 | Required quality certifications? | ISO 9001 / ISO 14001 / ISO 45001 / ASME / CE marking (Recommended: ISO 9001 + domain-specific) |
| 3.4 | Is OEM authorization certificate required from bidder? | Yes / No (Recommended: Yes) |
| 3.5 | Are past performance certificates from government / PSU clients preferred? | Yes / No (Recommended: Yes) |

### 4. Technical Requirements

| # | Question | Recommended Answer |
|---|---|---|
| 4.1 | What are the primary capacity / rating specifications? | User specifies (e.g. capacity in L, kW, bar, °C, flow rate) |
| 4.2 | What are the material of construction requirements? | e.g. SS 304/316/316L, Carbon Steel, Aluminum, Copper — specify grade and IS/ASTM equivalent |
| 4.3 | What applicable standards must the equipment comply with? (See Formatting Rules — Standard Priority rule applies) | IS / ISO / IEEE / ASME / ASTM / IS:2825 / ASME Sec VIII / etc. (Recommended: match standard to equipment type) |
| 4.4 | What are the operating environment conditions? | e.g. Ambient 0–45°C, humidity up to 90%, outdoor/indoor installation |
| 4.5 | Are there specific interface / utility requirements? | e.g. Electrical: 415V 3-phase 50Hz, Cooling water: 25°C @ 3 bar, Compressed air: 6 bar |
| 4.6 | What is the acceptable tolerance / accuracy / uncertainty? *(Skip if: tolerance not critical, e.g. standard consumables)* | User specifies (e.g. ±1°C, ±0.5% FS) |
| 4.7 | What safety features are mandatory? | e.g. Overpressure relief, emergency stop, fire-rated, explosion-proof (IS/IECEx) |
| 4.8 | Are accessories / ancillaries required? *(If No: skip accessories subsection in technical requirements table)* | User specifies (e.g. filters, regulators, valves, fittings, control panels) |
| 4.9 | What finish / coating is required? *(Skip if: finish/coating not applicable, e.g. standard off-shelf items)* | e.g. Paint shade RAL 7035 light grey, SS passivation, hot-dip galvanized (specify DFT) |

### 5. Bid Evaluation Criteria

| # | Question | Recommended Answer |
|---|---|---|
| 5.1 | What technical parameters are evaluated in bid scoring? | e.g. Capacity compliance, efficiency, warranty, delivery timeline, past performance |
| 5.2 | What is the weightage for technical vs. commercial evaluation? | e.g. 70% technical / 30% commercial (Recommended: 70/30 for critical equipment) |
| 5.3 | Are there mandatory disqualification criteria? | e.g. Non-compliance with BQC, incomplete documentation, conditional bids |

### 6. Acceptance Criteria

| # | Question | Recommended Answer |
|---|---|---|
| 6.1 | What tests must be performed at the vendor facility (PDI)? | e.g. Hydrostatic test, performance test, pressure test, functional test |
| 6.2 | What tests must be performed at RRCAT after installation? | e.g. Site acceptance test, performance verification, calibration check |
| 6.3 | What is the acceptance pass/fail criteria? | e.g. ±X% of rated capacity, no leaks, within temperature tolerance, noise level |
| 6.4 | Are rejection warning paragraphs required? | Yes (Recommended: Yes — state that incomplete/unsigned sheets may be rejected) |

### 7. Delivery Terms

| # | Question | Recommended Answer |
|---|---|---|
| 6.1 | What is the required delivery timeline? | e.g. 8 weeks / 12 weeks / 16 weeks from PO (Recommended: 12 weeks) |
| 6.2 | What packaging standards apply? *(Skip if: standard commercial packaging acceptable)* | e.g. Marine-grade export packing, weatherproof, shock-proof as per IS:xxxx (Recommended: MIL-STD or IS:xxxx for transit) |
| 6.3 | What warranty period is required? | 12 months / 24 months / 36 months from final acceptance (Recommended: 12 months) |

Ask all questions from sections 1-7 before generating. Confirm each answer before moving to the next question.

## Post-Generation Verification (Run Before Presenting)

After generating the tender document, verify ALL of these:

- [ ] Every `[CONFIRMED_*]` placeholder has been **replaced** with the confirmed value
- [ ] No brand names or model numbers appear anywhere (vendor neutrality)
- [ ] All sections 1-7 are present and complete
- [ ] Section 7 (Compliance Sheet) is present — **never omit this section**
- [ ] Compliance sheet uses **4-column format**: Sr. No. | Parameter | Requirement | Vendor Compliance
- [ ] Compliance sheet instruction text is present: "Instructions: Bidders must indicate compliance clearly for every parameter. 'Yes/No/Complied' NOT ALLOWED." (bold on "Instructions:" and "'Yes/No/Complied' NOT ALLOWED.")
- [ ] Compliance sheet has signature / seal / date blocks (Signature, Name, Company Seal, Date, Place — **bold labels**)
- [ ] Section header rows use merged single cell spanning all 4 columns with equipment-group labels
- [ ] Sr. No. values are **sequential integers** (1, 2, 3, ... N) with NO gaps
- [ ] Tables have correct number of rows matching the confirmed scope
- [ ] Standards cited (IS, ISO, IEEE, ASME, ASTM) match what the user confirmed
- [ ] All quantities and units match what the user confirmed
- [ ] Units are SI (or SI equivalent shown in parentheses)
- [ ] **Anti-loophole check:** Scan every BQC criterion — can a spurious bidder claim compliance without evidence? If yes, tighten to require verifiable proof (PO copies, completion certs, OEM auth letters).
- [ ] **Ambiguity check:** Is "Yes/No/Complied" explicitly disallowed in the compliance sheet? Add the rejection-warning instruction if missing.
- [ ] **Evidence demand check:** Every compliance row requires specific supporting documentary evidence (not just a tick mark).
- [ ] **Gaps from examples checklist:** Scan learned patterns for the equipment type — does your tender include equivalent defensive clauses? (e.g. if Argon example had right-to-audit, does yours? If Microscope example blocked "spec copy as catalogue", does yours?)

If any check fails, fix before presenting.

**7. Convert to `.docx`:** After all checks pass, generate the `.docx` from the RRCAT template using officecli (see Quick Start step 6 for detailed workflow):
```
Copy-Item _template.docx [output].docx
officecli set [output].docx ... (populate all content per Formatting Rules)
officecli close [output].docx
officecli view [output].docx outline
```
Present the `.docx` to the user.

## Sync (Run After Every Operation)

Synchronize the installed skill (`~/.agents/skills/rrcat-tender/`) with the workspace (`project root`):

1. **Normalize encoding** — convert all `.md` files to UTF-8 without BOM to prevent tooling issues:
   ```powershell
   Get-ChildItem Examples/*.md | ForEach-Object {
       $c = [System.IO.File]::ReadAllText($_.FullName)
       [System.IO.File]::WriteAllText($_.FullName, $c, [System.Text.UTF8Encoding]::new($false))
   }
   ```
2. Copy `SKILL.md` from installed → workspace (overwrite)
3. Copy all `Examples/*.md` from workspace → installed (overwrite, since markitdown generates them in workspace)
4. Confirm: "Synced."

## Output Template (Fill-in-the-Blanks Skeleton)

Use this skeleton when generating the final document. Replace `[CONFIRMED_VALUE]` with user-confirmed values. Add/remove rows as needed. For each section, note the anti-loophole guidance.

> ⚠️ **Section 7 (Vendor Compliance Sheet (Mandatory)) is MANDATORY — never omit it.**

### Boilerplate Clauses (use as needed in generated text)

**Past Performance (BQC):** "The bidder must provide verifiable evidence (e.g. Purchase Orders, Completion Certificates) of having successfully supplied similar equipment of [CONFIRMED_CAPACITY_TYPE] or higher in the past five (5) years."

**Material/Finish:** "Material/Surface preparation shall conform to [CONFIRMED_STANDARD], including [CONFIRMED_FINISH] (Minimum parameter/DFT: [CONFIRMED_VALUE])."

**PDI:** "A [CONFIRMED_TEST_NAME] must be performed prior to dispatch. This test must be physically witnessed by an RRCAT engineer at the vendor's manufacturing facility. The vendor shall provide a minimum of two (2) weeks advance notice prior to the test."

**Warranty:** "The complete assembly and all supplied hardware/software must carry a comprehensive replacement warranty against design defects, material flaws, and workmanship for a minimum period of 12 months from the date of final acceptance at the RRCAT facility."

---

# TENDER SPECIFICATION FOR [EQUIPMENT NAME]

**Tender Ref.:** RRCAT/[YEAR]/PUR/[XXX] | **Date:** [DD/MM/YYYY] *(`[XXX]` = sequential number, e.g. 001)*

---

### 1. Scope of Supply

Procurement of [EQUIPMENT NAME] for [PURPOSE] at RRCAT, Indore.

| Item No. | Category | Item Description | Key Specifications | Qty |
|:---|:---|:---|:---:|---:|
| 1 | Main Equipment | [CONFIRMED_DESCRIPTION] | [CONFIRMED_KEY_SPEC] | [CONFIRMED_QTY] |
| 2 | Accessories | [CONFIRMED_DESCRIPTION] | [CONFIRMED_KEY_SPEC] | [CONFIRMED_QTY] |
| 3 | Mandatory Spares | [CONFIRMED_DESCRIPTION] | [CONFIRMED_KEY_SPEC] | [CONFIRMED_QTY] |
| 4 | Documentation | O&M Manuals, Test Certificates | As per Section 4 | [CONFIRMED_QTY] sets |

*[Include ITC / Training / Civil lines only if confirmed Yes in checklist]*

---

### 2. Bidder Qualification Criteria (BQC)

**2.1 Main Equipment Manufacturer:**
- The OEM must have minimum [CONFIRMED_YEARS] years of experience in manufacturing similar equipment.
- Must have supplied at least [CONFIRMED_COUNT] units of similar capacity to government / PSU / reputed organizations in the past 5 years.
- Must hold valid ISO [CONFIRMED_STANDARD] certification.

**2.2 Accessories / Subcomponents Sourcing:**
- Subcomponents must be sourced from ISO-certified manufacturers.
- Bidder must submit OEM authorization certificate for main equipment.

**2.3 Regulatory Compliance (if applicable):**
- For solar/PV: Bidder shall submit a copy of the valid ALMM Enlistment Letter issued by MNRE at the time of bid. The letter must verify that the specific Model Numbers and Manufacturing Unit address proposed for this project are enlisted in ALMM List-I. The validity of the enlistment must cover the entire scheduled supply period.
- For other equipment: Include any mandatory government registration/certification (e.g. PESO, BIS, BEE).

---

### 3. Technical Requirements

**3.1 Main Equipment**

| Parameter | Specification | Standard |
|:---|:---|:---:|
| [CONFIRMED_PARAM] | [CONFIRMED_VALUE] | [CONFIRMED_STANDARD_REF] |
| [CONFIRMED_PARAM] | [CONFIRMED_VALUE] | [CONFIRMED_STANDARD_REF] |
| Material of Construction | [CONFIRMED_GRADE] | [CONFIRMED_STANDARD_REF] |
| Operating Conditions | [CONFIRMED_RANGE] | — |
| Finish / Coating | [CONFIRMED_FINISH] | [CONFIRMED_STANDARD_REF] |
| Safety Features | [CONFIRMED_FEATURES] | [CONFIRMED_SAFETY_STANDARD] |

**3.2 Accessories & Ancillaries** *[Include only if confirmed Yes]*

| Item | Specification | Standard |
|:---|:---|:---:|
| [CONFIRMED_ACCESSORY] | [CONFIRMED_SPEC] | [CONFIRMED_STANDARD_REF] |
| [CONFIRMED_ACCESSORY] | [CONFIRMED_SPEC] | [CONFIRMED_STANDARD_REF] |

---

### 4. Bid Evaluation Criteria

The bidder must provide following documents/information for bid evaluation:

a) Vendor Compliance Sheet (signed & sealed)
b) Make & Model Nos of each component. The make & model number must be verifiable from OEM website/catalogue.
c) Technical Datasheets (all equipment)
d) OEM Authorization Letters ([EQUIPMENT_SPECIFIC])
e) GA Drawings ([EQUIPMENT_SPECIFIC])
f) [Any other document specific to equipment, e.g. Solar Yield Simulation Report]

---

### 5. Acceptance Criteria

| System | Test Protocol | Acceptance Criteria |
|:---|:---|---:|
| [SYSTEM_NAME] | [TEST_PROTOCOL] | [ACCEPTANCE_CRITERIA] |
| [SYSTEM_NAME] | [TEST_PROTOCOL] | [ACCEPTANCE_CRITERIA] |

---

### 6. Delivery Terms

| Term | Detail |
|:---|:---|
| Delivery Timeline | [CONFIRMED_WEEKS] weeks from Purchase Order date |
| Packaging | Standard commercial packing |
| Warranty | [CONFIRMED_MONTHS] months from final acceptance against design defects, material flaws, and workmanship for complete assembly and all supplied hardware/software |

---

### 7. Vendor Compliance Sheet (Mandatory)

> **Instructions:** Bidders must indicate compliance clearly for every parameter. **"Yes/No/Complied" NOT ALLOWED.** Attach supporting documents for each claim. Bids with incomplete or unsigned sheets may be summarily rejected. Supporting documents shall be attached for each claim as applicable.

Table: **4 columns** — Sr. No. | Parameter | Requirement | Vendor Compliance (use Table Grid style)

Rows are organized by **section header groups**. Each group starts with a merged single-cell bold row spanning all 4 columns:

| Sr. No. | Parameter | Requirement | Vendor Compliance |
|:---|:---|:---|---:|
| 1 | OEM Make and Model Number | Provide Make and Model number of all components (shall be verifiable from OEM website) | |
| 2 | ISO 9001 Certification | Valid certificate | |
| 3 | OEM Authorization | All components shall be sourced from OEM or OEM authorized dealers (OEM Authorization shall be attached along with the bid) | |
| **Main Equipment Group** _(single merged cell, bold)_ |
| 4 | [Equipment-specific param 1] | [Requirement] | |
| 5 | [Equipment-specific param 2] | [Requirement] | |
| ... | ... | ... | |
| **Accessories / Civil Group** _(single merged cell, bold, if applicable)_ |
| N | [Accessory param 1] | [Requirement] | |
| ... | ... | ... | |
| **Delivery Terms** _(single merged cell, bold)_ |
| N | Installation and Testing and Commissioning | Complete Integration of all components and working demonstration | |
| N+1 | Delivery Timeline | [CONFIRMED_WEEKS] weeks from PO | |
| N+2 | Warranty | [CONFIRMED_MONTHS] months from final acceptance | |

**Signature of Bidder:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Name & Designation:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Company Seal:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Date:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

**Place:** \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_

---

## RRCAT Template (`_template.docx`)

A pre-populated RRCAT-formatted template (`_template.docx`) is bundled with this skill. It contains all 7 sections with placeholder tables ready to fill:

1. **Scope of Supply** — 5-column table (Item No., Category, Description, Key Specs, Qty)
2. **BQC** — Bold label format (2.1 Main Equipment, 2.2 Accessories)
3. **Technical Requirements** — 3-column tables (Parameter, Specification, Standard)
4. **Bid Evaluation Criteria** — Numbered list (a-f)
5. **Acceptance Criteria** — 3-column table (System, Test Protocol, Acceptance Criteria)
6. **Delivery Terms** — 2-column table (Term, Detail)
7. **Vendor Compliance Sheet** — 4-column table (Sr. No., Parameter, Requirement, Vendor Compliance)

**Always start from this template when generating a new tender document.**

To use:
```
Copy-Item _template.docx [output].docx
officecli open [output].docx
... (find and replace [CONFIRMED_*] placeholders using officecli)
officecli close [output].docx
```

### OfficeCLI Command Reference

#### File Lifecycle

| Command | Pattern | Notes |
|---|---|---|
| **Open** | `officecli open [file].docx` | Start resident process for fast edits |
| **Save** | `officecli save [file].docx` | Flush changes to disk (resident stays warm) |
| **Close** | `officecli close [file].docx` | Save + release file (required before external read) |

#### Read & Query

| Content Type | Command Pattern | Notes |
|---|---|---|
| **View structure** | `officecli view [file].docx outline` | Heading hierarchy + table structure |
| **View annotated** | `officecli view [file].docx annotated` | Every paragraph with style + font info |
| **View text** | `officecli view [file].docx text` | Plain text content only |
| **Get element** | `officecli get [file].docx /body/p[N]` | Read single paragraph or cell |
| **Get JSON** | `officecli get [file].docx /body/p[N] --json` | Machine-readable with style/props |
| **Query find** | `officecli query [file].docx "p:contains('text')"` | Find paragraph containing text |
| **Query selector** | `officecli query [file].docx "tbl tr tc"` | CSS-like selector for elements |

#### Modify Content

| Content Type | Command Pattern | Notes |
|---|---|---|
| **Headings** | `officecli set [file].docx /body/p[N] --style Heading1 --text "text"` | Use `Heading1`, `Heading3` per style table |
| **Paragraphs** | `officecli set [file].docx /body/p[N] --style "Body Text" --text "text"` | Style names: `FirstParagraph`, `Body Text`, `Compact`, `Block Text`, `Normal` |
| **Bold text** | `officecli set [file].docx /body/p[N] --bold-range START,END --text "full text"` | START/END are character offsets (0-indexed) |
| **Font size** | `officecli set [file].docx /body/p[N] --prop size=14` | Size in pt (not half-points) |
| **Alignment** | `officecli set [file].docx /body/p[N] --prop align="center"` | Values: `left`, `center`, `right`, `justify` |
| **Page break** | `officecli set [file].docx /body/p[N] --page-break-before` | Insert before major sections (3, 5, 7) |

#### Modify Tables

| Content Type | Command Pattern | Notes |
|---|---|---|
| **Table cell** | `officecli set [file].docx /body/tbl[T]/tr[R]/tc[C] --text "content"` | T=table, R=row, C=col (1-based) |
| **Add row** | `officecli add [file].docx /body/tbl[T] --type row` | Append empty row to table |
| **Remove cell** | `officecli remove [file].docx /body/tbl[T]/tr[R]/tc[C]` | Delete cell (use for column reduction) |
| **Merged header** | `officecli set [file].docx /body/tbl[T]/tr[R]/tc[C] --merge-span COLS --text "Header"` | COLS = columns to span (e.g., 4) |
| **Bold label in cell** | `officecli set [file].docx /body/tbl[T]/tr[R]/tc[C] --bold --text "Label:"` | For signature labels, BQC prefixes |
| **Column widths** | `officecli set [file].docx /body/tbl[T] --prop colWidths="1257,7174,811"` | Comma-separated dxa values |

#### Add & Remove Elements

| Content Type | Command Pattern | Notes |
|---|---|---|
| **Add paragraph** | `officecli add [file].docx /body --type paragraph --props text="...",style="..."` | Insert new paragraph at end of body |
| **Add after** | `officecli add [file].docx /body/p[N] --type paragraph --props text="..."` | Insert after specific paragraph |
| **Remove element** | `officecli remove [file].docx /body/p[N]` | Delete paragraph or table |

#### Batch Operations

| Content Type | Command Pattern | Notes |
|---|---|---|
| **Batch** | `officecli batch [file].docx --commands '[{"command":"set","path":"/body/p[1]","props":{"text":"Hi"}}]'` | Multiple ops in one pass |
| **Dump** | `officecli dump [file].docx /body` | Serialize to replayable batch script |
| **Validate** | `officecli validate [file].docx` | Check OpenXML schema compliance |

#### Tips

- **Quote paths** — most shells expand `[brackets]`: `officecli get doc.docx "/body/p[1]"`
- **Resident mode** — keep file open with `officecli open` for faster sequential edits
- **Style not found** — if a style doesn't exist in template, officecli warns but applies reference; define style in template first or use inline formatting
- **Path syntax** — use `/body/tbl[N]/tr[R]/tc[C]` for table cells (not `/body/table[T]/cell[R,C]`)

## Formatting Rules

These rules are sourced from the reference documents `Solar_PV_20kWp_Civil.docx` and `Cold_Storage_Container_40ft.docx` and MUST be followed for every generated tender.

### Page Layout

| Property | Value |
|:---|:---|
| Page Size | A4 (21.59 cm × 27.94 cm) |
| Margins | Top/Bottom/Left/Right: 2.54 cm |
| Header/Footer margin | 1.27 cm |
| Columns | 1 |
| Default Tab Stop | 1.27 cm |

### Fonts & Theme

| Property | Value |
|:---|:---|
| Theme | Office Theme |
| Major Font (headings) | Aptos Display |
| Minor Font (body) | Aptos |
| Default Body Size | 12 pt |
| Language (Latin) | en-US |
| Language (Complex Script) | hi-IN |

### Document Structure (7 Sections)

Every generated tender MUST have exactly 7 sections in this order:

| Section | Title | Style |
|:---:|:---|:---:|
| 1 | Scope of Supply | `heading 3` (14pt) |
| 2 | Bidder Qualification Criteria (BQC) | `heading 3` (14pt) |
| 3 | Technical Requirements | `heading 3` (14pt) |
| 4 | Bid Evaluation Criteria | `heading 3` (14pt) |
| 5 | Acceptance Criteria | `heading 3` (14pt) |
| 6 | Delivery Terms | `heading 3` (14pt) |
| 7 | Vendor Compliance Sheet (Mandatory) | `heading 3` (14pt) |

### Paragraph Styles

| Style Name | Usage | Formatting |
|:---|:---|:---|
| `Heading1` | Document title (centered, top) | Aptos Display, **20 pt**, Color #0F4761, Center aligned, SpaceBefore=18pt, SpaceAfter=4pt, KeepNext, KeepLines |
| `Heading3` | Section titles (1. / 2. / 3. ...) | Aptos (minor), **14 pt**, Color #0F4761, SpaceBefore=8pt, SpaceAfter=4pt, KeepNext, KeepLines |
| `FirstParagraph` | Scope intro, BQC first paragraph | Aptos 12 pt, Justify, SpaceBefore=9pt, SpaceAfter=9pt |
| `Body Text` | BQC body text, acceptance criteria labels, signature labels | Aptos 12 pt, SpaceBefore=9pt, SpaceAfter=9pt |
| `Compact` | Bid evaluation list items (a), (b), (c)... | Aptos 12 pt, SpaceBefore=1.8pt, SpaceAfter=1.8pt, Numbered lowerLetter `%1)` format with indent 21.3pt |
| `Block Text` | Compliance sheet instructions (quoted block) | Aptos 12 pt, **Bold**, Indent Left=480, Indent Right=480, SpaceBefore=5pt, SpaceAfter=5pt |
| `Normal` | Empty separator paragraphs | Aptos 12 pt |

### BQC Format (Section 2)

BQC items follow this exact pattern from both reference documents:

```
2.1 Equipment Manufacturer: Only [OEM TYPE] or their authorized dealers are allowed to bid in this tender.
2.2 Quality Certifications: - The OEM must hold valid ISO 9001 certification.
```

- **Bold label prefix** ("2.1 Equipment Manufacturer:") using `FirstParagraph` style
- **Bold label prefix** ("2.2 Quality Certifications:") using `Body Text` or `FirstParagraph` style
- Dash separator (" - ") between label and body text (when present)
- Key values bolded: **ISO 9001**, **OEM authorization certificate**, etc.

### Bid Evaluation List Format (Section 4)

Use `Compact` style with lowercase letter numbering:

```
The bidder must provide following documents/information for bid evaluation:
a) Vendor Compliance Sheet (signed & sealed)
b) Make & Model Nos of each component. The make & model number must be verifiable from OEM website/catalogue.
c) Technical Datasheets (solar module and Inverter)
d) OEM Authorization Letters (modules, inverter)
e) GA Drawings (shed, foundation)
f) Solar Yield Simulation Report (PVSyst)
```

### Acceptance Criteria Format (Section 5)

Both reference documents include a **rejection warning paragraph** before the acceptance criteria table:

```
Failing to the below acceptance criteria will result in rejection of the delivered product. RRCAT will not bear any cost associated with the rejected product, including transportation, freight, handling, or return shipment charges.
```

- Title format: `5. Acceptance Criteria:` (with colon — both reference docs include it)
- Warning paragraph uses `Normal` style (bold italic in Solar doc)
- This warning MUST appear in every generated tender before the acceptance criteria table

### Compliance Sheet Instruction Text

The compliance sheet instruction paragraph uses `Block Text` style in reference documents. If `Block Text` is not defined in the target template, use `Normal` style with bold formatting on key phrases.

Exact text from reference:
```
Instructions: Bidders must indicate compliance clearly for every parameter. 'Yes/No/Complied' NOT ALLOWED. Attach supporting documents for each claim. Bids with incomplete or unsigned sheets may be summarily rejected. Supporting documents shall be attached for each claim as applicable.
```

- "Instructions:" → bold
- "'Yes/No/Complied' NOT ALLOWED." → bold
- Rest is normal weight

### Bold Text Usage

The following content MUST be rendered in **bold** in the document:

- BQC label prefixes ("2.1 Equipment Manufacturer:", "2.2 Quality Certifications:")
- Key values within BQC text (e.g. "**5 years**", "**ISO 9001**", "**OEM authorization certificate**")
- Section 3.2 heading "3.2 Accessories"
- Compliance sheet instruction text: "Instructions:" and **"'Yes/No/Complied' NOT ALLOWED."**
- Signature labels: "Signature of Bidder:", "Name & Designation:", "Company Seal:", "Date:", "Place:"
- Acceptance criteria warning keywords: "**below**", "**delivered product**", "**product**"

### Table Style

| Property | Value |
|:---|:---|
| Table Style | **Table Grid** (single border all sides, 4pt) |
| Cell Margins | Top=0, Left=108dxa (5.4pt), Bottom=0, Right=108dxa |
| tblLook | 0020 (firstRow, bandedRows, bandedCols enabled) |

### Table Column Layouts

| Table Type | Columns | Alignment | Notes |
|:---|:---:|:---|:---|
| **Scope of Supply** | 3 (Sr.No, Description, Qty) | Sr.No=left, Description=left, Qty=center | Header row with bold labels |
| **Technical Specs** | 3 (Parameter, Specification, Standard) | Parameter=left, Spec=left, Standard=center | Header row, spacer rows use merged single cell |
| **Accessories** | 2 (Item, Specification) | Both left | Header row |
| **Acceptance Criteria** | 3 (System, Test Protocol, Acceptance Criteria) | All left | Multi-line cells in Criteria column |
| **Commercial Terms** | 2 (Term, Detail) | Both left | Header row |
| **Compliance Sheet** | 4 (Sr.No, Parameter, Requirement, Vendor Compliance) | All left | Section-header rows use merged single cell |

### Section Header Rows in Compliance Table

Section header rows (e.g. "Main Equipment Group", "Accessories Group", "Delivery Terms") use a **single merged cell spanning all 4 columns** with height 490dxa. These are NOT numbered rows — they are category dividers. Name them according to the equipment type (e.g. "40 ft ISO Dry Shipping Container", "Solar Power Plant", "Civil Work").

### Compliance Sheet Numbering

Sr. No. values MUST be sequential integers (1, 2, 3, ... N) with NO gaps. Do not carry over original numbering from reference examples if rows are removed or reordered.

### Bid Evaluation List

Use lower-letter numbered list format `a)`, `b)`, `c)` etc. with:
- Style: `Compact`
- Number format: `lowerLetter` with `%1)` pattern
- Indent: 21.3pt from left
- Start: 1

### Page Breaks

Insert page breaks before major section transitions:
- Before Section 3 (Technical Requirements) — after BQC section
- Before Section 5 (Acceptance Criteria) — after Bid Evaluation
- Before Section 7 (Compliance Sheet) — after Commercial Terms

### Document-level Properties

| Property | Value |
|:---|:---|
| Compatibility Mode | 12 (Word 2016+) |
| Char Spacing Control | doNotCompress |
| Embed System Fonts | true |
| Default Tab Stop | 1.27 cm |
| Tender Ref Format | `RRCAT/[YEAR]/PUR/[XXX]` (`[XXX]` = 3-digit sequential number, e.g. 001) |

### Units

Prefer SI. If mixed/imperial used, show SI equivalent in parentheses (e.g. "150 bar (15 MPa)").

### Standard Priority

Indian Standards (IS) take precedence over international standards. Use IS wherever available. Only use international standards (ISO, IEEE, ASME, ASTM, IEC) if no corresponding IS exists for the specific requirement.

### Off-the-shelf Verification

For all standard catalogued / off-the-shelf items, require make & model number verifiable from the manufacturer's website. Add this to the bid documents requirement and to the compliance sheet row.

## Equipment-Type Detection Helper

When the user requests a tender, use this lookup table to quickly identify the closest example and study it for defensive clauses:

| Keywords | Closest Example | Key Lessons to Study |
|---|---|---|
| LN2, dewar, cryogenic container, transportable | Technical_Specifications_485.md | anti-sloshing baffles, vacuum/leak acceptance criteria, PESO certification |
| twin dewar, interconnected, vaporizer | Twin_Dewar_Specs.md | interconnected design prevents substitution, separate D1/D2 spec rows, Y-strainer locked into scope |
| cryostat, cryogenic vessel, 4K, superconducting | TechSpec-Nidhin-Cryostate_Optimized.md | OEM-only gate, in-house facility list, 18 BOI annexures, factory access clause, NDA |
| cryomodule, vacuum vessel, strongback, thermal shield | Procurement_Specification_HBCM_TEC_24_Apr_2026.md | structured pre-qual questionnaire, MRR+SAR sequential reviews, CMM/laser tracker inspection |
| rail system, precision rail, assembly rail | Technical_Specs_of_CARS_V5_12_DEC.md | facility visit right (4×), 8-stage hold points, MDED, mandatory questionnaire, bought-out item traceability |
| VJ hose, vacuum jacketed, flexible, cryogenic hose | Flexible_Super_Insulated_Vacuum_Jacketed_Flexible.md | ⚠️ NEGATIVE EXAMPLE — no BQC section, no compliance sheet. Study gaps to avoid |
| LN2 container, self-pressurized, cryogenic gas | Specification_Self_Pressurised_LN2_Container_INOX_Microcyl_Complied.md | ⚠️ NEGATIVE EXAMPLE — no formal BQC structure, no compliance sheet |
| PUF container, insulated container, fabrication | Rev_Technical_Specifications_for_Container.md | OEM gate, 3-year lock guarantee, PUF conductivity test |
| TMP, vacuum pump, turbo molecular | Technical_Specifications-TMP-Final_Optimized.md | OEM auth cert on letterhead, export restriction clause, compliance sheet mandatory |
| vacuum gauge, gauging system | Technical_Specifications-Gauge_R1_Optimized.md | same template as TMP, make/model + catalogue copy per item |
| DTL tank, drift tube linac, vacuum vessel | DTL-Tank-TechnicalSpecifications&Drawings_Optimized.md | 4-stage PDI, CNC/CMM/CMM facilities, material test certs from NABL lab |
| LEBT piping, SS pipeline, cryogenic piping | LEBTPiping-Specifications-Final_Optimized.md | TIG welding only, ER 308L consumables, no free issue material, 5 reference figures |
| EOT crane, overhead crane, double girder | DraftPO_15_Ton_EOT_Crane.md | design approval before fabrication, QAP submission, PBG |
| chiller, water chiller, cooling, laser cooling | Tender_Spec_Chiller_20kW.md | make/model traceable on OEM website, compliance sheet with clause ref IDs, no PDI at vendor |
| argon, UHP gas, gas supply, cylinder | Argon_Gas_Specification_RRCAT.md | COA per delivery, standard-wise failure table, plant visit right, PESO certification |
| microscope, optical instrument | Modified_specifications_20260513.md | signed spec copy NOT accepted as catalogue, traceable part numbers, product catalogue mandatory |
| lens, mirror, optical coating, laser optics | technical_specifications_for_lenses_and_mirrors.md | ⚠️ NEGATIVE EXAMPLE — no BQC section. Acceptance by RRCAT lab testing is de facto gate |
| cryogenic PPE, safety gears, gloves, face shield | Technical_Specification_for_Cryogenic_Safety_Gears.md | "Yes/No/Complied NOT ALLOWED", LN2 temperature receipt inspection, EN/IS standards |
| DC fan, axial fan, cooling fan | DC_axial_fans_for_automotive_use.md | exact values required in compliance sheet, make/model mandatory |
| solar, PV, solar panel, solar module, on-grid, photovoltaic | Solar_PV_20kWp_Civil.docx | ALMM Enlistment Letter mandatory, PVSyst simulation report, 25-yr performance warranty, civil works in scope, rejection warning paragraph |
| cold storage, container, refrigeration, 40 ft, insulated container | Cold_Storage_Container_40ft.docx | container modification scope explicitly defined, acceptance criteria with rejection warning, OEM or authorized dealers only |

**How to use:** Match the user's equipment description to the keywords column. Read the closest example. Study its defensive clauses (not its table format — that may differ). Ensure equivalent protections appear in your generated tender.

## Reference Examples

This skill bundles real RRCAT tender specs in `Examples/`. Both formats available:
- `*.md` — text-extracted Markdown (readable by the agent during generation)
- `*.pdf` — original PDFs (human reference for formatting/layout)

**Purpose of these examples (critical to understand):**

These examples are NOT templates to copy. They exist to teach the AI:

1. **Communication style** — how RRCAT communicates with bidders: precise, formal, leaving no room for misinterpretation
2. **Defensive specification writing** — how to write specs that block spurious/unqualified bidders by requiring verifiable evidence (PO copies, completion certs, OEM auth letters, ISO certs, client lists with contact details)
3. **Anti-loophole clauses** — phrases like "signed & sealed spec copy NOT accepted as catalogue", **"Yes/No/Complied" NOT ALLOWED**, "RRCAT reserves right to physically visit plant", "part numbers verifiable on OEM website"
4. **Guidelines to supplier** — clear statements of what the supplier must provide, by when, and what happens if they don't
5. **Protecting public money** — PBG, strict acceptance criteria, warranty terms that prevent retendering

**Negative examples:** Some real RRCAT specs in `Examples/` lack a compliance sheet, BQC section, contain brand names (vendor neutrality violation), or omit other mandatory elements (noted in the Pattern Library). These serve as counter-examples — study them to understand what gaps look like, then ensure your generated tender closes those gaps.

Examples cover:
- Cryogenic equipment (dewars, VJ hoses, cryostats, cryomodules)
- Gas supply (UHP Argon)
- PUF containers & EOT cranes
- Vacuum systems (TMP modules, gauging, DTL tanks, LEBT piping)
- Precision equipment (microscopes, laser optics, rail systems)
- Safety gears & axial fans
- Water chillers
- Solar PV systems with civil works (20 kWp, mounting shed, ALMM)
- Cold storage containers (40 ft, 4 TR, refrigeration)

**How to learn from examples during generation:**
1. Read the Example whose equipment type is closest to the user's request.
2. You **may** adopt its table format, BQC phrasing, and layout — that's useful consistency.
3. But the **primary** thing to learn is the *defensive clauses*: how it phrases requirements to eliminate ambiguity, demands verifiable evidence, blocks spurious compliance, and protects RRCAT's interests. Emulate that *clarity and rigor* above all.
4. Study the **anti-loophole strategies** (right to audit, document verification, rejection warnings, evidence requirements) and ensure equivalent protections appear in your generated tender.
5. Consult the **Learned Pattern Library** for quick reference on which gatekeeping strategies and defensive mechanisms apply to which equipment types.

## Auto-Learn Command (/tender-learn)

Run when user adds a new PDF to `Examples/` and says `/tender-learn`.

### Prerequisite

Miniconda Python with MarkItDown: `pip install 'markitdown[all]'`

### Procedure

1. **Scan** `Examples/` for `*.pdf` files.
2. For each PDF, check if a matching `*.md` exists (e.g. `Foo.pdf` → `Foo.md`).
3. Find the **first PDF without a matching `.md`**. Present to user:
   > "Found new PDF: `[Name].pdf`. Process it?"
   - User says **Yes** → proceed.
   - User says **No** → ask: skip this file or process a different one?
   - User says **Skip** → move to next unmatched PDF.
4. **Convert** the PDF to Markdown using MarkItDown:
   ```
   markitdown "Examples/[OriginalName].pdf" > "Examples/[OriginalName].md"
   ```
   (Requires Miniconda Python with `pip install markitdown[all]` installed at `~/Miniconda3/python.exe`)
4.5 **Normalize encoding** — convert all `.md` files to UTF-8 without BOM to prevent tooling issues:
   ```powershell
   Get-ChildItem Examples/*.md | ForEach-Object {
       $c = [System.IO.File]::ReadAllText($_.FullName)
       [System.IO.File]::WriteAllText($_.FullName, $c, [System.Text.UTF8Encoding]::new($false))
   }
   ```
   (Run from workspace root. Ensures consistency regardless of what markitdown or other tools produce.)
5. Read the generated `.md` to review quality and fix any extraction issues.
6. **Analyze** the new example for learned patterns:
   - Determine the equipment type / category.
   - Identify BQC phrasing style used.
   - Note the technical table format (column layout).
   - Extract any unique/notable clauses (warranty, EMD, LD, standards).
7. **Add a new row** to the **Learned Pattern Library** table below with the extracted data.
8. **Update** the "Examples cover:" line in the **Reference Examples** section — append the new equipment type.
8.5 **Validate Learned Pattern Library row** — Re-read the Learned Pattern Library table. Verify the new row has all 5 columns populated (Example name, equipment type, BQC strategy, anti-loophole clauses, defensive mechanisms). If any column is empty, fill it with "TBD — requires analysis" before proceeding.
8.75 **Validate Examples count** — Count the rows in the Reference Examples "Examples cover" line and verify it matches the actual number of `.md` files in `Examples/`. If mismatch, update the count.
9. **Confirm**:
   > "Learned from `[Name].md`. Pattern Library and Reference Examples updated."
10. **Repeat** — ask if user wants to process the next unmatched PDF.

### Sync between workspace and installed skill

The skill is installed at `~/.agents/skills/rrcat-tender/` and the workspace is at the project root. **Sync after every operation** (generation and /tender-learn):

| Direction | Files |
|---|---|
| Installed → Workspace | `SKILL.md` |
| Workspace → Installed | `Examples/*.md` |

**Sync procedure (run after every operation):**
1. Copy `SKILL.md` from installed → workspace (overwrite workspace copy)
2. Copy all `Examples/*.md` from workspace → installed (overwrite, since markitdown generates them in workspace)
3. **Verify sync integrity:**
   - Compare SHA256 hashes of `SKILL.md` (installed vs workspace) and `_template.docx` (installed vs workspace). Report mismatch if found.
   - Count `Examples/*.md` in both locations; report if counts differ.
   - Check that `AGENTS.md` exists in installed directory.
4. Confirm: "Synced — all files verified."

## Learned Pattern Library (anti-loophole patterns learned from examples)

This table grows with every `/tender-learn` run. It captures **what actually prevents spurious bidders** — BQC gatekeeping strategies, mandatory evidence requirements, and rejection-language clauses — for each equipment type. During generation, consult it to ensure equivalent protections appear in your output.

**Column purpose:**
- `Vulnerability Type` → category of loophole this example exposes: `evidence-gap`, `bypass-risk`, `ambiguity-trap`, `missing-rejection`, `missing-bqc`, `weak-bqc`, `vendor-neutrality-violation`
- `BQC Strategy` → how the original tender blocked unqualified bidders (NOT the format — the *gatekeeping mechanism*)
- `Anti-Loophole Clauses` → key phrases that eliminate ambiguity / prevent exploitation
- `Defensive Mechanisms` → warranty, EMD, PBG, acceptance testing, audit rights, delivery penalties

| Example | Equipment Type | Vulnerability Type | BQC Strategy (gatekeeping) | Anti-Loophole Clauses | Defensive Mechanisms |
|---|---|---|---|---|---|
| Argon_Gas_Specification_RRCAT.md | UHP Argon Gas N6.0 (50 × 47L cylinders) | evidence-gap, bypass-risk | OEM only with in-house purification + testing; ISO/IEC 17025 + ISO 9001/14001/45001; RRCAT right to audit plant | "RRCAT reserves right to physically visit OGM plant"; COA required on each delivery; standard-wise failure table with consequences | PESO certification; 12-mo cylinder/valve warranty; Rejection if COA not matching spec |
| DC_axial_fans_for_automotive_use.md | 24V DC Axial Fans (545 cfm, 20 Nos) | ambiguity-trap | Vendor fills compliance sheet with actual values; make/model traceable on mfr website | "Yes/No/OK not allowed — exact values required"; "Make & model mandatory" — prevents generic compliance blurf | EMD implied by tender rules; Delivery 2 months fixed |
| Flexible_Super_Insulated_Vacuum_Jacketed_Flexible.md | Flexible VJ Hose for LN2 (1/2" ID, 16 Nos) ⚠️ NEGATIVE EXAMPLE | missing-bqc, missing-rejection | **No BQC section** (gap) — no OEM gate, no past-performance filter | Helium leak test at 1×10⁻⁸ atm·cc/s explicitly stated; Vacuum retention 24-48h monitoring period | Pneumatic test at 1.1× design pressure; Heat in-leak <1 W/m; **Missing: compliance sheet, BQC section, signature blocks** |
| Rev_Technical_Specifications_for_Container.md | 20' PUF Insulated Container (2 Nos, fabrication) | bypass-risk | OEM only with in-house welding/cutting/bending; ≥1 same-size PUF chamber in last 3 years | "Trouble-free lock guarantee — 3 years" (unusual — clear warranty language); Forklift pocket spec prevents handling damage | PUF thermal conductivity test mandatory; Air leak test per ISO 1496-2 |
| Specification_Self_Pressurised_LN2_Container_INOX_Microcyl_Complied.md | Self-Pressurized LN2 Container (≥230L, 2 Nos) ⚠️ NEGATIVE EXAMPLE | missing-bqc, missing-rejection | OEM or Auth Certificate; mention make/model of regulator | Static evap rate "verified at RRCAT" on receipt — prevents inflated claims; spring-loaded auto-resetting PRV + rupture disc both required | Evap rate ≤2%/day verified post-delivery; **Missing: compliance sheet, formal BQC structure, signature blocks** |
| Technical_Specification_for_Cryogenic_Safety_Gears.md | Cryogenic PPE (-196°C): gloves 10 pr, face shields 10, aprons 10 | evidence-gap | OEM or authorized agent only; valid ISO 9001 | **"Yes/No/Complied" NOT ALLOWED** — forces bidder to state exact compliance; EN/IS standards explicitly listed for each gear type | LN2 temperature receipt inspection (practical test); Multiple EU/IS safety standards enforced |
| Technical_Specifications_485.md | PESO Certified Transportable Horizontal LN2 Dewar (500L, 4 Nos) | evidence-gap | OEM or authorized rep; documents to be enclosed (open-ended) | Anti-sloshing baffles "≥3" (explicit min count prevents single-baffle shortcuts); PDI acceptance criteria: vacuum ≤10⁻³ mbar, leak ≤10⁻⁶ mbar·L/s | ASME BPVC Sec VIII Div 1 / ISO 21029-1 design; PESO cert mandatory |
| Twin_Dewar_Specs.md | Twin Vacuum Insulated Horizontal LN2 Dewars (D1:330L + D2:150L) w/ external vaporizer (2 sets) | bypass-risk | OEM or authorized dealer; relevant docs required | Interconnected design explicitly specified (prevents two standalone dewars being delivered); anti-sloshing baffles "≥2 vertical" | Cryogenic Y-strainer 100µ + solenoid valve 24V DC locked into scope; D1 & D2 requirements listed separately to avoid confusion |
| final_specifications.md | 10 TR Air Cooled Water Chiller (supply + ITC) ⚠️ NEGATIVE EXAMPLE | vendor-neutrality-violation, missing-bqc | OEM or authorized rep; ISO 14001:2015 + UL cert; proven record in last 3 years; CLIENT LIST WITH CONTACT DETAILS | **Contains brand names (Danfoss/Emerson, Grundfoss) — violates vendor neutrality rule**; "Client list with contact details" — enables RRCAT to verify claims independently; "BOM with part numbers and datasheets" forces supplier to commit to specific components | 24-month extended warranty; Commissioning cert; Fault diagnosis checklist; P-I and wiring diagrams mandatory; **Missing: compliance sheet, signature blocks** |
| Modified_specifications_20260513.md | Portable Long Working Distance Digital Microscope (8MP, 10X-140X, 1 No) | evidence-gap | Vendor must specify mfr name, model, catalogue; part numbers verifiable on OEM website | **"Signed spec copy NOT accepted as catalogue"** — classic loophole closer; traceable part numbers prevent bait-and-switch | Product catalogue mandatory; No warranty clause (weak — would strengthen in generation) |
| technical_specifications_for_lenses_and_mirrors.md | Hard Dielectric Coated Lenses (26 pcs) and 45° Bending Mirrors (4 pcs) for 1064 nm laser | missing-bqc, weak-bqc | **No BQC section** (original gap — weak); Acceptance via RRCAT lab testing (de facto gate) | Acceptance by "RRCAT lab testing" — final say rests with RRCAT, not vendor self-certification; MIL-C-675A coating adhesion standard | Laser damage threshold: ≥5 J/cm² (lenses), ≥20 J/cm² (mirrors); 1-yr warranty |
| Procurement_Specification_HBCM_TEC_24_Apr_2026.md | HB650 Cryomodule Components Kit (Vacuum Vessel + Strongback + Magnetic Shield + Thermal Shield + MLI + Cryo Piping + more) for PIP-II/FNAL | evidence-gap | OEM only; 4K cryostat experience ≥500L in last 10 yrs; ASME U-stamped vessel; ISO/IEC 17025 third-party cert; WPQ certs; Facility visit right | "Mandatory Questionnaire (Section 14)" — structured pre-qual screening; MRR (Manufacturing Readiness Review) + SAR-1 sequential reviews | CMM/Laser tracker inspection; 20-month delivery; 40-yr life at 2K; DAP shipping to FNAL |
| DraftPO_15_Ton_EOT_Crane.md | 15 Ton Double Girder EOT Crane, Duty Class M7, 17.5m span, 84m travel | evidence-gap | Design approval by RRCAT (gate before fabrication); QAP submission required; PBG | "Design approval before fabrication" — prevents building wrong configuration; PBG ensures performance bond | Load cell with display + pendant + wireless remote; PDI + commissioning at RRCAT; 6 months delivery incl. installation |
| Technical_Specs_of_CARS_V5_12_DEC.md | Cryomodule Assembly Rail System (CARS) — ~33m precision rail system for HB650 cryomodule assembly | bypass-risk | OEM or authorized rep ONLY; QAP submission; list of fabrication/inspection facilities; RRCAT right to visit and REJECT; independent QC team; WPQ certs (TUV/BV/IoW); CNC machine with ~4m stroke; sub-contractor disclosure; bought-out items traceable on OEM website; same OEM for all bought-out items | "RRCAT reserves right to inspect facilities and reject bid in case of incompetency" (appears 4×); "Make and model traceable from website of OEM"; "Bought out items from same OEM for compatibility"; MDED (Manufacturer Drawing Exception Document) — deviations not listed = vendor responsibility; Annexure-I Mandatory Questionnaire — "Responses with 'All compliance' or similar will not be considered"; 8-stage Hold Point system (Table 4) | MRR before fabrication; 12-month warranty from commissioning; PBG required; 12+2 month delivery; PDI + SAT with quantified acceptance (pulling force <2kg for 100kg load); Vendor liable for transit damage; 3 sets hardbound documentation |
| TechSpec-Nidhin-Cryostate_Optimized.md | SWLS Cryostat (hybrid 4K cryostat for superconducting wavelength shifter, 1 set, fabrication + assembly + ITC) | evidence-gap | OEM only (cryostats/cryogenic vessels/vacuum vessels) with ISO cert; must have designed/manufactured/supplied high vacuum (≤1×10⁻⁵ mbar) vessel ≥500L for cryogenic application with MLI in last 10 yrs; mandatory in-house facilities: ASME design verification, TIG welding, brazing, He leak detector, LN2 handling, EOT crane; documentary evidence with photos | "In the absence of unambiguous reply with proper supporting documents... offer shall be summarily treated as technically not suitable"; 18 BOI annexures with make/model approval pre-procurement; FIM process loss <10%; Factory access clause; NDA required | 12-month warranty from final acceptance; FAT + SAT; He leak test ≤1×10⁻⁷ mbar·L/s at site; Design verification per ASME before fabrication; 9-month delivery; EMD via Bharatkosh + PSDBG; ASME BPVC Sec VIII Div 1 design; WPQ per ASME Sec IX |
| Technical_Specifications-TMP-Final_Optimized.md + Technical_Specifications-Gauge_R1_Optimized.md | TMP Modules + Vacuum Gauging System (2 files, same template) | missing-rejection | OEM or authorized rep only; OEM authorization cert on letterhead; proven supply record for UHV/vacuum; standard catalogued product; OEM authorized service centre in India | "Completed compliance sheet with signature is mandatory — liable for rejection if absent or incomplete"; "Export of equipment out of India for servicing not acceptable"; make/model + catalogue copy required per item | 12-month warranty from acceptance; OEM certification before dispatch; Testing at RRCAT for final acceptance; Operation manual mandatory |
| DTL-Tank-TechnicalSpecifications&Drawings_Optimized.md | DTL Tank Assembly (precision-machined SS304/304L vacuum vessel, OD 610mm, ID 577mm, L 1500mm, for drift tube linac, 1 set) | evidence-gap | ISO 9001 certified bidder; mandatory in-house facilities: CNC/VMC, CMM (≥1000mm), surface roughness measurement, He mass spectrometer leak detector; documentary evidence required | 4-stage acceptance at supplier site (material → weld → pre-finish → finish); Material test certs from NABL/ISO lab only; Ultrasonic testing per ASTM from NABL/ISO lab; Welding per ASME Sec IX; RT of all weld joints; Leak rate ≤1×10⁻⁹ mbar·L/s | 4-stage PDI; SAT at RRCAT (dimensional + surface finish + leak test); 6-month delivery; Guarantee/warranty; Compliance sheet with signature mandatory |
| LEBTPiping-Specifications-Final_Optimized.md | LEBT Piping System (SS304L low conductivity water pipe line, 2" schedule 10, 50 line items incl. pipes/bends/flanges/valves/fasteners/hoses, 1 set, fabrication + supply + installation + testing) | evidence-gap | Min 3 years experience in SS pipeline supply, erection, commissioning & leak testing; client list + PO copies as evidence; no OEM requirement (fabrication/installation contract) | "Only TIG welding allowed"; ER 308L consumables per ASME/AWS A5.10; Argon shielding ≥99.99% purity; Hydro-test cert for Argon cylinder ≤5 yrs old; "No free issue material from RRCAT" — prevents scope creep; 5 reference figures for configuration; Material test reports required | Leak test at 10 bar + dye penetrant test; Ball valves per ANSI Class IV; Compliance sheet with qualification criteria; Cost comparison on total cost (material + fabrication + installation) |
| Tender_Spec_Chiller_20kW.md | Re-circulating Chiller, 20 kW cooling capacity for laser cooling (1 No + accessories) | evidence-gap | OEM with ≥2 similar-capacity (20 kW+) chillers supplied to govt/PSU in last 3 yrs verifiable via PO/cert; ISO 9001:2015 + ISO 14001:2015; OEM auth cert; make/model traceable on OEM website | **'"Yes/No/Complied" NOT ALLOWED'** — exact compliance per parameter; "Incomplete or unsigned sheets may be summarily rejected"; "Make and model verifiable from manufacturer's website"; Warranty clock starts at "final acceptance at purchaser facility" | No PDI — acceptance & testing only at purchaser site (risk shifted to vendor); 12-mo warranty from final acceptance; FOR pricing; Compliance sheet with traceable clause ref IDs (BQC-x/TECH-x/COM-x) |
| Solar_PV_20kWp_Civil.docx | 20 kW On-Grid Solar PV System with Civil Works (mounting shed + foundation + concrete flooring) | evidence-gap, bypass-risk | OEM or authorized dealers only; ISO 9001 certification; ALMM Enlistment Letter from MNRE mandatory | "ALMM Enlistment Letter" — prevents non-enlisted modules; make/model verifiable from OEM website; PVSyst simulation report required | 12-month workmanship warranty + 25-year linear performance warranty for PV modules; Rejection warning paragraph before acceptance criteria |
| Cold_Storage_Container_40ft.docx | Cold Storage Container (4 TR, 4°C, 40 ft dry container modified) | evidence-gap | OEM or authorized dealers only; ISO 9001 certification | "The bidder has to modify a standard 40 ft dry shipping container" — scope explicitly defined; make/model verifiable from OEM website | Acceptance criteria table with specific parameters; Rejection warning paragraph before acceptance criteria |
