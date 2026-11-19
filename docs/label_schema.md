# Label schema

## Departments (8)
| id | Handles | Boundary rules |
|---|---|---|
| water_supply | No water, low pressure, dirty tap water, pipe burst | A pipe burst flooding a road is still water_supply |
| roads | Potholes, broken roads, missing speed breakers, damaged bridges | Footpath blocked by shops is encroachment, not roads |
| sanitation | Garbage not collected, overflowing bins, street sweeping | Dead animals go to stray_animals |
| drainage | Blocked drains, sewage overflow, open manholes | Rainwater logging counts as drainage |
| electricity | Power cuts, fallen wires, transformer faults | A broken streetlight pole is streetlights |
| streetlights | Lights not working, leaning poles, flickering | Live wire on a pole is electricity (critical) |
| stray_animals | Dog bites, stray cattle, dead animals | |
| encroachment | Illegal construction, footpath occupation, hawkers | |

## Urgency
| level | Meaning | SLA |
|---|---|---|
| critical | Immediate danger to life (live wire, open manhole, fire) | 4 h |
| high | Health or injury risk, or a service outage hitting many people | 24 h |
| medium | Real nuisance, no immediate danger | 72 h |
| low | Cosmetic or long-term | 7 days |

## Labelling rules
1. One department per complaint: the one that must act first.
2. Urgency reflects the worst credible outcome, not the author's tone.
3. Mask phone numbers and names before labelling.
4. Mark `language` as one of: en, hi, te, hi-latn, te-latn (mixed text gets the dominant language).
5. Two people label an overlapping 300-row subset. Report Cohen's kappa.
