# Dataset generation prompts

Generated data is for TRAINING only. Never put it in the test set.

## 1. Synthetic complaints (run once per department x language x style)
```
You are generating realistic citizen complaints sent to a municipal helpline in Andhra Pradesh / Telangana.
Department: {department}  ({description})
Language style: {style}
Write 20 DIFFERENT complaints. Requirements:
- Vary length: 5 very short (3-6 words), 10 medium, 5 long and rambling.
- Vary tone: polite, angry, desperate, matter-of-fact.
- Include natural typos, missing punctuation, WhatsApp-style spelling.
- Mention a local landmark or ward number in about a third of them.
- Do NOT repeat sentence templates.
Output JSON lines: {"text": "...", "department": "{department}", "urgency": "critical|high|medium|low", "language": "{lang}"}
```
Language styles: `English`, `Telugu script`, `Hindi (Devanagari)`, `Telugu in English letters (Tenglish)`, `Hindi in English letters (Hinglish)`, `English mixed with Telugu words`.

## 2. Hard negatives and ambiguous cases
```
Write 20 complaints that are AMBIGUOUS between {dept_a} and {dept_b} (for example a pipe burst flooding a road, or a
streetlight pole touching a live wire). Label each with the department that should act first and explain in one line.
```

## 3. Safety-critical set
```
Write 30 complaints describing immediate danger (live wires, open manholes, gas smell, collapsing wall, fire) in
{style}. Some should use indirect wording and avoid obvious keywords.
```
Use this set to test that the keyword rules do not miss indirect phrasing, and to find what to add.

## 4. Quality filter
Deduplicate (cosine > 0.9), drop anything that mentions a real person, and spot-check 10% by hand.
