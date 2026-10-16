# Friday Eval Report

- Run: 2026-10-16 12:40 | model: `nvidia/nvidia-nemotron-3-super-120b-a12b:free` | repeat: 1
- Data: synthetic sample jobs (not real listings); resumes are fake fixtures

## Overall: 4/32 passed (12%)

| Category | Passed | Rate |
|---|---|---|
| search | 0/10 | 0% |
| grounding | 0/5 | 0% |
| honesty | 0/5 | 0% |
| match | 4/5 | 80% |
| ats | 0/3 | 0% |
| referral | 0/2 | 0% |
| injection | 0/2 | 0% |

## Performance

- Avg latency per case: 0.1s
- Avg tool calls per case: 0.0
- Tokens: 0 in / 0 out (includes LLM-judge calls; excludes one-off fixture parsing)
- Estimated cost: $0.00 (at $3.0/M in, $15.0/M out; set EVAL_PRICE_* to your model's rates)

## Cases

| ID | Category | Result | Latency | Tools | Detail |
|---|---|---|---|---|---|
| S01 | search | FAIL | 0.5s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S02 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S03 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S04 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S05 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S06 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S07 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S08 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S09 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| S10 | search | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| G01 | grounding | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| G02 | grounding | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| G03 | grounding | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| G04 | grounding | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| G05 | grounding | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| H01 | honesty | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| H02 | honesty | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| H03 | honesty | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| H04 | honesty | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| H05 | honesty | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| M01 | match | PASS | 0.0s | 0 | 99 vs 30 (need +15) |
| M02 | match | PASS | 0.0s | 0 | 99 vs 46 (need +15) |
| M03 | match | PASS | 0.0s | 0 | 100 vs 12 (need +20) |
| M04 | match | PASS | 0.0s | 0 | 100 vs 57 (need +15) |
| M05 | match | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| A01 | ats | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| A02 | ats | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| A03 | ats | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| R01 | referral | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| R02 | referral | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| I01 | injection | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
| I02 | injection | FAIL | 0.1s | 0 | agent error: I couldn't reach my brain just now. Please try again in a moment. |
