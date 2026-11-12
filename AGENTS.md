# Working instructions

This repository is an **in-development portfolio project** for a fictional DTC mattress retailer. Read README.md, PROJECT_BRIEF.md and PROGRESS.md before changes.

- Preserve existing work. Check Git status and remotes before changes; never overwrite work or force-push.
- Use `.venv/bin/python`. Initial setup uses Python 3.14.8 with no third-party dependencies. Check interpreter compatibility and binary availability before adding packages; record versions and run relevant checks.
- Do not connect accounts, activate paid services or push unless the user authorizes that work.
- Keep secrets, raw customer records and private exports out of Git. Use placeholder configuration and explicitly labeled synthetic samples. Review staged files and notebook outputs before every commit.
- No invented findings, business results, completed integrations or test outcomes. Distinguish planned, implemented and verified work.
- Validate data grain, join cardinality, duplicates, missingness, attribution, currency, time zone and revenue definitions. Reconcile purchases and revenue before recommending spend changes.
- AI-generated code, SQL and claims need independent execution or evidence review. Log assumptions, inputs, verification and limitations; never send private data to an AI service without explicit authorization.
- Keep changes within the requested milestone. Use meaningful checks appropriate to each change and document actual results in PROGRESS.md.
- Explain decisions in plain language suitable for an interview. Document blockers and the next concrete action.
