# Friday: a note for the QuickHyre team

## What I noticed on your product
- Your homepage shows **Friday, "Your AI Career Copilot"**, marked *coming soon*, with a clear promise: tailored recommendations, "why you're a fit", interview prep, ATS resume help and career guidance.
- The job feed on the public page appears to **repeat listings**. At portal scale, duplicates hurt trust and apply rates.
- [CANDIDATE TO REVIEW: add 2-3 observations only you can make after using the product as a real job seeker (signup flow, search quality, mobile experience, filters). Be specific and kind.]

## What I built and why
I built a working slice of Friday on synthetic data (no scraping), to test whether the promise holds up when measured:
- **Grounded search:** Friday may only mention jobs the search tool returned, always with an ID. It says "I don't have that" for funding, salary and news instead of guessing.
- **Deterministic fit score:** the 0-100 number comes from code, so it is explainable and testable. The LLM only narrates evidence.
- **Honest resume help:** the ATS check treats missing keywords as gaps to learn, and rewrites use `[X]` placeholders instead of invented numbers.
- **Duplicate handling:** near-duplicate listings are collapsed in results.
- **32 automated evals**, so a change to the prompt or model can't silently break trust.

## Results
Overall pass rate 97% and grounding 100%. Full run, including the failures I found and fixed: [EVAL_REPORT.md](../EVAL_REPORT.md).

## What I'd do in the first 30 days
- **Week 1:** learn your data and stack; map real listing fields onto the `search_jobs` schema.
- **Week 2:** ship Friday search on real listings to a small internal group, with the eval suite running on every change.
- **Week 3:** add resume upload with a privacy review, and instrument where users drop off.
- **Week 4:** measure recommendation quality (apply rate per recommendation) and fix the top three failure types.

I'd love to hear where this misses what real users need.

Nakshatra Thange
nakshatrathange@gmail.com
