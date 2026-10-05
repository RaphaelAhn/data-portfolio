# Weekly job driven data portfolio

This portfolio has a local Codex automation named **주간 채용 공고 기반 데이터 포트폴리오**. It runs on Mondays at 09:00 Asia/Seoul with **GPT-6 Sol**. The first scheduled run has not yet produced an industry dataset or analysis. The automation ID is `automation-2`.

## Destination

- Notion parent: [데이터 엔지니어 포트폴리오(공부용)](https://app.notion.com/p/3e3ae94086248087afefcdc16c50cbea).
- Automation index: [채용 공고 기반 산업별 데이터 프로젝트](https://app.notion.com/p/3f0ae940862481908486d6f08c5bd392). Completed and partial work is documented in dated child pages.
- Git remote confirmed by the user: `https://github.com/RaphaelAhn/data-portfolio.git`, branch `main`.

## Weekly workflow

1. Open public postings for data scientist, data engineer, and data analyst roles on the user-selected job sites. Record source URL, check date, role, industry, status, and a short list of skills. Exclude expired, closed, and duplicate postings from the active-skill count. Record inaccessible sites as unknown. Do not bulk scrape or republish posting text.
2. Choose one industry and one work problem from observed postings. A small next step in an existing portfolio project is preferable when it provides stronger evidence than starting a redundant project.
3. Set the data boundary before drafting: use **synthetic** data only, with a seed, schema, intentional defects, expected results, and tests. Never include customer, applicant, credential, or copied public-dataset records.
4. After Codex gathers the postings and chooses a scoped problem, use only the three locally responding Ollama models. The local runner is `C:\AleFrontier\scripts\ollama_portfolio_role.py`, invoked with `--role <build|explain|check> --input <prompt.txt> --output <result.json>`. Qwen 3.5 9B (`build`) drafts the synthetic-data schema, generator, transformation and analysis code. Gemma 4 12B (`explain`) receives the brief and Qwen draft, then drafts metric explanations, interpretation, limitations and beginner-friendly notes. Phi-4 Mini (`check`) receives both drafts and proposes independent edge cases, reconciliation checks and tests. Pass actual output forward; preserve each request and response. CPU/GPU execution is allowed and Ollama's NPU use is not claimed. Apertus and other models are excluded.
5. Codex checks each draft against the brief and the other drafts, then executes and verifies the stages in order: synthetic-data generation, input checks, cleaning, analysis or modeling, interpretation. A model's prose is not evidence. The final GPT-6 Sol review compares source pages, all three drafts, code, synthetic data, and execution output; errors are corrected and checked again. A failing model's stage remains incomplete after bounded retries rather than being silently replaced.
6. Write a detailed, beginner-friendly dated Notion child page with source links, data definitions, example rows, each model's role and actual output, commands, observed results, limitations, and next action. Fetch it after saving.
7. Commit and push only the newly verified files for this automation. Check `origin` and `main` against the confirmed destination, use an isolated worktree when possible, and never stage or discard unrelated changes. Verify the remote SHA and add the receipt to the dated Notion page. A failed verification or push remains explicitly incomplete.

## Current evidence boundary

The 2026-10-06 dated page records setup and a small source check. It does **not** claim that an industry dataset, analysis, GPT-6 Sol review, or project push was completed. Qwen 3.5, Gemma 4 and Phi-4 Mini each produced a short local role draft through the Ollama runner; content quality still requires review and a full weekly project run is untested. Earlier OpenVINO NPU tests remain historical evidence, not the current three-model workflow.
