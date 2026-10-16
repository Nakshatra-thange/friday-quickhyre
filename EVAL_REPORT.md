# Friday Eval Report

- Run: 2026-10-16 14:53 | model: `nvidia/nemotron-3-super-120b-a12b` | repeat: 1
- Data: synthetic sample jobs (not real listings); resumes are fake fixtures

## Overall: 0/2 passed (0%)

| Category | Passed | Rate |
|---|---|---|
| referral | 0/2 | 0% |

## Performance

- Avg latency per case: 38.3s
- Avg tool calls per case: 1.5
- Tokens: 12,146 in / 4,416 out (includes LLM-judge calls; excludes one-off fixture parsing)
- Estimated cost: $0.10 (at $3.0/M in, $15.0/M out; set EVAL_PRICE_* to your model's rates)

## Cases

| ID | Category | Result | Latency | Tools | Detail |
|---|---|---|---|---|---|
| R01 | referral | FAIL | 46.0s | 2 | 0w; The message is empty, lacking specificity to the role and a clear ask. |
| R02 | referral | FAIL | 30.7s | 1 | 94w; The provided material is instructional text, not a specific note to Priya with a clear ask and factual su |
