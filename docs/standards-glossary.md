# Standards & Certifications Glossary

Reference lookup for the standards and certifications cited in RRCAT tenders.
Used with the **Standard Priority** rule in `SKILL.md` (Indian Standards take
precedence; use international standards only where no IS exists). This file is
a reference — it is not a mandate to cite every standard.

| Standard / Certification | Full name / scope | When to cite | Example equipment |
|---|---|---|---|
| **IS 2825** | Code for unfired pressure vessels (India) | Pressure vessels, air receivers, tanks | LN2 dewars, air receivers |
| **ASME BPVC Sec VIII Div 1** | Rules for construction of pressure vessels (US) | International equivalent for pressure vessels when IS 2825 not specified | Cryostats, vacuum vessels |
| **ISO 21029-1/-2** | Cryogenic vessels — transportable vacuum-insulated vessels | Transportable cryogenic containers | LN2 dewars, cryo containers |
| **IS 2062** | Hot-rolled medium/high tensile structural steel | Structural steel (MS) components | Frames, sheds, structures |
| **IS 1239 / IS 3589** | Carbon steel pipes (low pressure / welded) | Carbon steel piping | LEBT piping, water lines |
| **ASTM A240 / A312** | Stainless steel plate / seamless pipe specs | SS materials with IS/ASTM equivalent | SS 304/316 tanks, piping |
| **ISO 9001** | Quality management systems | Baseline quality certification (recommended default) | All equipment |
| **ISO 14001** | Environmental management systems | Environmental certification | Chillers, solar PV |
| **ISO 45001** | Occupational health & safety management | Safety certification | Cranes, fabrication works |
| **ISO/IEC 17025** | Competence of testing and calibration laboratories | Labs issuing test reports / COAs | Gas testing, material test labs |
| **IECEx / IS/IEC 60079** | Explosion protection of electrical equipment | Hazardous/classified areas | Explosion-proof motors, panels |
| **PESO** | Petroleum and Explosives Safety Organisation license (India) | Pressure vessels / gas storage under PESO rules | LN2 dewars, argon cylinders |
| **BIS** | Bureau of Indian Standards product certification (ISI mark) | ISI-marked catalogue items | Cables, fans, motors |
| **BEE** | Bureau of Energy Efficiency star rating (India) | Energy-consuming equipment | Chillers, motors, fans |
| **ALMM (MNRE)** | Approved List of Models and Manufacturers | Solar PV modules/inverters (mandatory evidence) | Solar PV tenders |
| **NABL** | National Accreditation Board for Testing and Calibration Laboratories | Accredited test labs (CMTRs, calibration) | Material test certificates |
| **CE marking** | EU conformity marking | Electrical/electronic items where accepted | Lab instruments |

## Notes

- **Standard Priority:** cite the IS version when one exists; add the
  international equivalent in parentheses when useful (e.g. "SS 304 per ASTM
  A240").
- **Always dated/verifiable:** prefer "ISO 9001:2015" over "ISO 9001", and
  require certificate numbers verifiable on the accreditation body's website
  (per ADR-005 defensive-writing patterns).
- **Per-equipment applicability:** the equipment-type detection helper in
  `SKILL.md` notes which certifications matter per equipment type (e.g. PESO
  for LN2 dewars, ALMM for solar).
