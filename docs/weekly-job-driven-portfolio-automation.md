# Weekly job driven data portfolio

This portfolio has a local Codex automation named **주간 채용 공고 기반 데이터 포트폴리오**. It runs on Mondays at 09:00 Asia/Seoul with **GPT-6 Sol**. The first scheduled run has not yet produced an industry dataset or analysis. The automation ID is `automation-2`.

## Destination

- Notion parent: [데이터 엔지니어 포트폴리오(공부용)](https://app.notion.com/p/3e3ae94086248087afefcdc16c50cbea).
- Automation index: [채용 공고 기반 산업별 데이터 프로젝트](https://app.notion.com/p/3f0ae940862481908486d6f08c5bd392). Completed and partial work is documented in dated child pages.
- Git remote confirmed by the user: `https://github.com/RaphaelAhn/data-portfolio.git`, branch `main`.

## Weekly workflow

1. Open public postings for data scientist, data engineer, and data analyst roles on the user-selected job sites. Record source URL, check date, role, industry, status, and a short list of skills. Exclude expired, closed, and duplicate postings from the active-skill count. Record inaccessible sites as unknown. Do not bulk scrape or republish posting text.
2. Choose one industry and one work problem from observed postings. A small next step in an existing portfolio project is preferable when it provides stronger evidence than starting a redundant project.
3. Generate **synthetic** data only. Publish a seed, generation command, schema, intentional defects, expected results, and tests. Never include customer, applicant, credential, or copied public-dataset records.
4. Execute and verify each stage in order: input checks, cleaning, analysis or modeling, interpretation. A model's prose is not evidence. Local Ollama Qwen may propose drafts; the final Codex review is performed by GPT-6 Sol using source pages and execution output.
5. Write a detailed, beginner-friendly dated Notion child page with source links, data definitions, example rows, commands, observed results, limitations, and next action. Fetch it after saving.
6. Commit and push only the newly verified files for this automation. Check `origin` and `main` against the confirmed destination, use an isolated worktree when possible, and never stage or discard unrelated changes. Verify the remote SHA and add the receipt to the dated Notion page. A failed verification or push remains explicitly incomplete.

## Current evidence boundary

The 2026-10-06 dated page records setup and a small source check. It does **not** claim that an industry dataset, analysis, GPT-6 Sol review, or project push was completed. The NPU test models are separate from this workflow; Ollama execution in the automation has not been verified to use the NPU.
