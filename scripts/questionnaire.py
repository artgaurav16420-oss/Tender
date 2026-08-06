#!/usr/bin/env python3
"""questionnaire.py - Default tender answers and equipment-type detection.

Part of the rrcat-tender skill. Provides:
  - detect_equipment_type(keyword): maps an equipment keyword to a type name
    and a list of defensive pattern clauses for that equipment class.
  - get_answers(equipment_keyword): returns a dict of CONFIRMED_* placeholder
    values (defaults derived from the keyword), plus equipment-type specific
    extra entries (ALMM_ENLISTMENT, etc.).
  - make_answers_json(equipment_keyword, output_path): writes the answers dict
    to a UTF-8 JSON file (byte-safe, ensure_ascii=False).

Placeholder keys match the [CONFIRMED_*] tokens found in _template.docx
(18 distinct tokens, enumerated by officecli dump /body).
"""

import json
from pathlib import Path

# ---------------------------------------------------------------------------
# Equipment-type detection table (Task 7)
# keyword triggers -> (type_name, defensive pattern clauses)
# ---------------------------------------------------------------------------
EQUIPMENT_TYPES = {
    "solar": (
        "Solar PV System",
        [
            "- ALMM Enlistment Letter (MNRE) mandatory for PV modules; only ALMM-enlisted modules shall be accepted.",
            "- PVSyst simulation report (with system losses and performance ratio) to be submitted along with the bid.",
            "- 25-year linear performance warranty on PV modules; 12-month workmanship warranty on complete system.",
        ],
    ),
    "chiller": (
        "Re-circulating Chiller",
        [
            "- OEM must have supplied at least 2 similar-capacity units to government/PSU organisations in the last 3 years (verifiable purchase orders / certificates).",
            "- Performance demonstration / PDI to be carried out at purchaser site only.",
            "- Warranty period to commence from date of final acceptance at purchaser facility.",
        ],
    ),
    "container": (
        "Cold Storage Container",
        [
            "- Scope explicitly includes modification of a standard 40 ft dry shipping container.",
            "- Bidder to be an OEM authorised dealer for the offered equipment.",
            "- Bids not meeting the acceptance criteria shall be rejected; RRCAT shall not bear any cost associated with the rejected product.",
        ],
    ),
    "vacuum": (
        "Vacuum System",
        [
            "- Leak rate not to exceed 1x10^-9 mbar-l/s at site (mass spectrometer leak detection).",
            "- Design and fabrication as per ASME Boiler and Pressure Vessel Code; welding as per ASME Section IX (WPQ).",
            "- Multi-stage PDI: material, weld, pre-finish and final finish inspection at supplier works.",
        ],
    ),
    "cryogenic": (
        "Cryogenic System / Cryostat",
        [
            "- Only OEM to bid; bidder must have in-house fabrication, testing and cryogenic facility.",
            "- Confidentiality: NDA and BOI annexures mandatory.",
            "- FAT at supplier works and SAT at RRCAT to be carried out as per agreed protocol.",
        ],
    ),
    "piping": (
        "Piping System",
        [
            "- Only TIG welding allowed; 308L filler consumables conforming to ASME/AWS A5.10.",
            "- Argon shielding gas purity 99.99 percent; argon cylinder not older than 5 years.",
            "- Hydro-static testing and dye-penetrant testing as per specification; no free-issue material from RRCAT.",
        ],
    ),
}

# Keyword trigger -> type key (checked in order; first match wins)
TYPE_TRIGGERS = [
    ("solar", ["solar", "pv", "photovoltaic"]),
    ("chiller", ["chiller", "cooling"]),
    ("container", ["cold storage", "container"]),
    ("vacuum", ["vacuum", "uhv", "leak"]),
    ("cryogenic", ["cryogenic", "cryostat", "cryo"]),
    ("piping", ["piping", "pipeline", "pipe"]),
]

# Per-type display names used for CONFIRMED_DESCRIPTION
TYPE_DISPLAY_NAMES = {key: info[0] for key, info in EQUIPMENT_TYPES.items()}


def detect_equipment_type(keyword):
    """Map an equipment keyword to (type_name, patterns_list).

    Returns ("generic", []) when no trigger matches. Matching is case-
    insensitive substring matching over the first applicable trigger group.
    """
    kw = (keyword or "").strip().lower()
    for type_key, triggers in TYPE_TRIGGERS:
        for trig in triggers:
            if trig in kw:
                return type_key, EQUIPMENT_TYPES[type_key][1]
    return "generic", []


def _display_name(keyword):
    """A sensible equipment display name derived from the keyword."""
    type_key, _ = detect_equipment_type(keyword)
    if type_key != "generic":
        return TYPE_DISPLAY_NAMES[type_key]
    name = (keyword or "").strip()
    if not name:
        return "Equipment"
    # Title-case the keyword as a short system name
    return " ".join(w.capitalize() for w in name.split())


def get_answers(equipment_keyword):
    """Return a dict of CONFIRMED_* placeholder values for the keyword.

    Defaults follow RRCAT-style values: 3 years, 1 unit, ISO 9001:2015,
    equipment name as DESCRIPTION, '1 No' as QTY. Equipment-type defensive
    patterns are injected as extra entries (ALMM_ENLISTMENT, OEM_TRACK_RECORD,
    etc.) AND returned separately via detect_equipment_type() for paragraph
    injection by tender_gen.py.
    """
    kw = (equipment_keyword or "").strip()
    name = _display_name(kw)
    type_key, patterns = detect_equipment_type(kw)

    answers = {
        "CONFIRMED_YEARS": 3,                       # OEM experience (years)
        "CONFIRMED_COUNT": 1,                       # similar units supplied
        "CONFIRMED_STANDARD": "ISO 9001:2015",      # bidder certification
        "CONFIRMED_DESCRIPTION": name,              # equipment name
        "CONFIRMED_KEY_SPEC": "As per technical specifications detailed in Section 3",
        "CONFIRMED_QTY": "1 No",
        "CONFIRMED_MONTHS": 12,                     # warranty (months)
        "CONFIRMED_WEEKS": 16,                      # delivery (weeks)
        # Acceptance criteria table rows 2-3 (Parameter / Value)
        "CONFIRMED_PARAM_1": "Cooling Capacity",
        "CONFIRMED_PARAM_2": "Temperature Stability",
        "CONFIRMED_VALUE_1": "20 kW",
        "CONFIRMED_VALUE_2": "+/-0.5 deg C",
        # Technical requirements table (rows 2-5) standard references
        "CONFIRMED_STANDARD_REF_1": "IEC 61215",
        "CONFIRMED_STANDARD_REF_2": "IEC 61730",
        "CONFIRMED_STANDARD_REF_3": "IS 14705:1999",
        "CONFIRMED_STANDARD_REF_4": "MNRE Guidelines",
        "CONFIRMED_GRADE": "SS 304",
        "CONFIRMED_RANGE": "0 to 40 deg C",
        "CONFIRMED_FINISH": "Powder coated (RAL 7035)",
        "CONFIRMED_FEATURES": "Digital control panel with data logging and remote monitoring",
        "CONFIRMED_SAFETY_STANDARD": "IEC 61010-1",
        # Accessories / spec rows
        "CONFIRMED_ACCESSORY_1": "Spare fuse kit with holder",
        "CONFIRMED_ACCESSORY_2": "Operator tool kit",
        "CONFIRMED_SPEC_1": "As per manufacturer datasheet",
        "CONFIRMED_SPEC_2": "As per Section 3",
    }

    # --- Equipment-type defensive pattern injection (Task 7) ---
    pattern_labels = {
        "solar": ["ALMM_ENLISTMENT", "PVSYST_REPORT", "PERFORMANCE_WARRANTY"],
        "chiller": ["OEM_TRACK_RECORD", "PDI_PURCHASER_SITE", "WARRANTY_FINAL_ACCEPTANCE"],
        "container": ["SCOPE_CONTAINER_MOD", "OEM_AUTHORISED_DEALER", "REJECTION_WARNING"],
        "vacuum": ["LEAK_RATE_SPEC", "ASME_DESIGN_WPQ", "MULTI_STAGE_PDI"],
        "cryogenic": ["OEM_ONLY", "NDA_BOI", "FAT_SAT"],
        "piping": ["TIG_ONLY_308L", "ARGON_PURITY", "HYDRO_TEST_NO_FREE_ISSUE"],
    }
    labels = pattern_labels.get(type_key, [])
    for i, (label, clause) in enumerate(zip(labels, patterns)):
        # strip leading "- " for the extra dict entry
        answers[label] = clause.lstrip("- ").strip()

    # Repeated-token values (template has multiple occurrences per token)
    answers["CONFIRMED_PARAM"] = answers["CONFIRMED_PARAM_1"]
    answers["CONFIRMED_VALUE"] = answers["CONFIRMED_VALUE_1"]
    answers["CONFIRMED_STANDARD_REF"] = answers["CONFIRMED_STANDARD_REF_1"]
    answers["CONFIRMED_ACCESSORY"] = answers["CONFIRMED_ACCESSORY_1"]
    answers["CONFIRMED_SPEC"] = answers["CONFIRMED_SPEC_1"]

    return answers


def make_answers_json(equipment_keyword, output_path):
    """Write get_answers() result to a UTF-8 JSON file. Returns the dict."""
    answers = get_answers(equipment_keyword)
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)
    return answers


if __name__ == "__main__":
    import sys
    kw = sys.argv[1] if len(sys.argv) > 1 else "solar"
    out = sys.argv[2] if len(sys.argv) > 2 else "answers.json"
    answers = make_answers_json(kw, out)
    type_key, patterns = detect_equipment_type(kw)
    print(f"equipment: {kw}")
    print(f"type: {type_key} ({len(patterns)} patterns)")
    print(f"answers keys: {len(answers)}")
    print(f"wrote: {out}")
