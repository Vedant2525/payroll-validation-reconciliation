# Prompt History and AI Contribution Log

**Purpose:** This document makes the AI-assisted development process auditable. It distinguishes user prompts that are preserved in the conversation context from reconstructed engineering prompts used to describe the work stages. Reconstructed entries are **not claimed to be verbatim messages** and should not be represented as a complete transcript.

## A. Preserved user requests

### A1. Initial end-to-end payroll validation brief

**Record type:** Summary of the initial long specification (not a verbatim transcript).

**Request, summarized:** Design and implement a synthetic payroll validation workflow covering employee, pay-group and pay-period master data; time entries, leave records, allowances and deductions; payroll inputs; validation rules; exceptions; approvals; export records; and audit history. Generate three months of reproducible synthetic data for 3,000 employees and approximately 100,000 source transactions. Plant specified anomalies (including excessive hours, duplicate allowances, unapproved time, duplicate leave deductions and reconciliation mismatches), keep a separate ground-truth file, and provide CSV/JSON/SQL data, schema, data dictionary, README and verification evidence. Use synthetic/lawful data and do not expose planted anomaly labels in operational input features.

**Resulting work:** Relational data model, seeded generator, operational datasets, separate ground-truth data, validation rules and project documentation.

### A2. Request to expand the project

**Date in conversation context:** 2026-10-26.

**User prompt (verbatim):** “give complete project”

**Resulting work:** Expanded Python package with generation, validation, SQLite loading, command-line entry points, reporting, dashboard scaffolding, tests and documentation.

### A3. Submission criteria

**Date in conversation context:** 2026-10-27.

**User prompt (verbatim excerpt):**

> 01 MAKE IT RUN
>
> Submit working, executable code. Include clear steps so another person can install dependencies, configure the project, run it, and verify key behavior.
>
> 02 SHOW YOUR WORK
>
> Use a public GitHub repository. Make the evolution of your work understandable through the code, meaningful commits, and supporting context.
>
> 03 USE LLMs TRANSPARENTLY
>
> LLM tools are allowed. Submit your prompt history and explain where AI accelerated your work, where you relied heavily on it, and what you personally reviewed, changed, or validated.
>
> 04 MAKE YOUR REASONING VISIBLE
>
> Help reviewers understand the problem, assumptions, key decisions, trade-offs, testing approach, limitations, and how you know the solution works.

**Resulting work:** Submission checklist, AI-use disclosure, design decisions, GitHub publication guide, CI configuration and reproducibility/verification notes.

---

## B. Reconstructed engineering prompt map

The entries below are a **workflow-level reconstruction** from the requirements and artifacts. They make the technical progression legible; they are not a claim that each sentence was separately sent to the model. Keep this distinction if submitting the log for assessment.

### B1. Convert the business brief into a testable design

**Engineering prompt represented:**

> Turn the payroll-validation brief into a concrete implementation plan. Identify entities, primary and foreign keys, relationships, transaction volumes, business rules, planted anomalies, outputs and acceptance criteria. Separate assumptions from requirements, and define what must be true for a payroll batch to be exportable.

**Why this matters:** Prevents the implementation from becoming a pile of unrelated CSVs and gives the test suite explicit acceptance criteria.

**AI contribution:** Drafted the domain model and a first pass at validation and output requirements.

**Review needed:** Confirm field semantics and policy assumptions against the actual assignment; the schema is a demonstration model, not a legal payroll specification.

### B2. Design deterministic synthetic data

**Engineering prompt represented:**

> Build a seeded synthetic-data generator for 3,000 employees and three pay periods, with approximately 100,000 source transactions. Use stable identifiers and realistic relationships between employees, periods, time, leave, allowances, deductions and payroll inputs. Make repeated runs with the same seed reproducible, and write CSV/JSON outputs plus a manifest.

**Why this matters:** Reviewers need a dataset large enough to exercise the workflow while being able to reproduce the result locally.

**AI contribution:** Drafted generation logic, identifiers, output writing and seed handling.

**Review needed:** Verify row-count semantics, uniqueness, referential integrity and whether the generated distributions are appropriate for the intended scenario.

### B3. Plant anomalies without leaking the answers

**Engineering prompt represented:**

> Plant a known set of payroll defects—such as excessive hours, duplicate allowance, unapproved time, duplicate leave deduction and reconciliation mismatch—so they can be tested. Store expected anomaly labels only in a separate ground-truth artifact. Do not add issue labels or ground-truth flags to operational source tables, and make the validator detect defects from business data and keys instead.

**Why this matters:** If a validator reads an `issue_type` label from its input, it is using the answer key rather than detecting a defect.

**AI contribution:** Helped revise the data model and duplicate-detection approach so operational inputs do not carry ground-truth labels.

**Review performed in the build:** Source-table checks confirmed that `TimeEntry`, `LeaveRecord`, `Allowance`, `Deduction` and `PayrollInput` do not include `issue_type` or `ground_truth` columns. This is a programmatic check, not a substitute for human review of the rules.

### B4. Implement validation as explicit rules

**Engineering prompt represented:**

> Implement deterministic payroll checks for required employee/payroll data, valid time and amount ranges, approval state, duplicate business records and reconciliation consistency. Return actionable exceptions tied to the relevant record, and prevent invalid or unapproved payroll inputs from being exported. Keep the rules understandable and testable.

**Why this matters:** A useful validator should explain what failed and why, rather than merely produce a pass/fail total.

**AI contribution:** Drafted rule evaluation and exception-generation scaffolding.

**Review needed:** Validate rule severity, tolerances, duplicate definitions and export-blocking behavior against the assignment's policy. These choices are configurable business assumptions, not universal payroll law.

### B5. Persist the workflow in SQLite

**Engineering prompt represented:**

> Add a relational SQL schema and a loader for the generated data. Enforce primary/foreign-key relationships where applicable, load tables in dependency order, and report row counts and foreign-key violations so the database can be independently inspected.

**Why this matters:** A database build tests whether the proposed entities and relationships work beyond flat-file generation.

**AI contribution:** Drafted schema and loading logic.

**Verification recorded:** Database build completed with zero reported foreign-key violations. The generated database contained 3,000 employees, three pay periods, 9,000 payroll inputs and the expected operational workflow tables.

### B6. Provide a repeatable command-line workflow

**Engineering prompt represented:**

> Expose generation, validation, database creation and report generation as documented CLI commands. Use explicit arguments for output location, dataset size and random seed; fail clearly on validation errors; and make the happy path runnable from a fresh environment.

**Why this matters:** The evaluator should not need to reverse-engineer notebook state or manually call internal functions.

**AI contribution:** Drafted CLI entry points and run instructions.

**Review needed:** Execute the README instructions in a clean environment and verify dependency versions on the evaluator's platform.

### B7. Test invariants and planted defects

**Engineering prompt represented:**

> Add automated tests for the workflow and validate important invariants: primary keys, selected foreign keys, dates, amounts, payroll arithmetic, export gating, planted anomaly detection and ground-truth separation. Include a clear summary of checks passed and failed.

**Why this matters:** Example output alone does not establish correctness; the project needs repeatable checks.

**AI contribution:** Drafted tests and a validation command.

**Verification recorded:** `python -m unittest discover -s tests -v` passed two workflow tests; the dataset validator reported 50/50 checks passed. These are the project's current tests, not exhaustive proof of correctness.

### B8. Check same-seed reproducibility

**Engineering prompt represented:**

> Generate the same dataset twice with the same seed and compare output checksums. Record the seed, scale and result so a reviewer can reproduce the comparison.

**Why this matters:** Random data is useful for testing only if a reviewer can recreate the same test fixture when debugging a failure.

**AI contribution:** Drafted the checksum comparison workflow and reproducibility note.

**Verification recorded:** The same-seed comparison recorded `same_seed_checksums_match=True` for seed `20261022`, 3,000 employees and approximately 100,000 source transactions.

### B9. Produce reviewable reporting and documentation

**Engineering prompt represented:**

> Add a human-readable validation report, data dictionary, relationship notes and business-rule documentation. Explain how to run the project, how to inspect outputs, which assumptions were made, and what is not production-ready.

**Why this matters:** Reviewers should be able to understand the outputs and limitations without reading every implementation detail first.

**AI contribution:** Drafted documentation and an HTML report generator.

**Review needed:** Check that report labels and totals match the generated artifacts and that documentation does not imply capabilities the prototype does not implement.

### B10. Prepare the submission honestly

**Engineering prompt represented:**

> Organize the deliverables around the rubric: runnable code and verification instructions; a public-repository workflow with meaningful commits; a transparent AI-use disclosure and prompt history; and design notes covering assumptions, trade-offs, tests and limitations. Do not claim a GitHub repository or human review exists unless it actually does.

**Why this matters:** A polished package is not the same thing as a published repository or independently reviewed submission.

**AI contribution:** Drafted submission documentation, CI configuration and a publication checklist.

**Current status:** Source packages and publication instructions were prepared, but this log does not claim that a public GitHub repository was created or pushed. The submitter must create the repository, make real commits, run the workflow and record their own review accurately.

---

## C. Verification snapshot associated with this log

The following results were recorded during the package build and should be re-run by the submitter before final submission:

- Dataset generation: 3,000 employees across three pay periods; approximately 100,000 source transactions.
- Dataset validator: 50/50 checks passed.
- Database load: zero reported foreign-key violations.
- Unit tests: two tests passed.
- Reproducibility: same-seed CSV checksum comparison matched.
- Ground-truth separation: no `issue_type` or `ground_truth` fields in the listed operational input tables.

Commands and environment assumptions are documented in `README.md` and `REPRODUCIBILITY_CHECK.txt`.

## D. AI-use and authorship note

ChatGPT was used heavily for initial scaffolding, Python modules, schema, tests and documentation. The generated code should not be described as wholly hand-written. The submitter is responsible for understanding it, running it, checking the outputs and making their own changes. `PERSONAL_REVIEW_CHECKLIST.md` should be completed only for work actually performed. This file is not a full conversation export and contains no hidden model reasoning trace.
