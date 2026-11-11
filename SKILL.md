---
name: last-mile-pm-to-code
description: Explain a software project (especially one built with AI help, "vibe coding") to a non-developer, such as a product manager. Covers the technologies used, what each file does, how data moves through each user action, and what is missing before launch, then produces a single-file HTML report with a self-test. Use when the user asks to understand, explain or document how their own app works ("help me understand this project", "explain the structure / tech / data flow", "make a project report"). Not for line-by-line code tutoring, bug hunting or code review.
---

# The Last Mile: PM to Code

The reader can use the product but cannot read the code. The goal is that they can **understand and explain** their own project: in a review, an interview, or a conversation with engineers. This is not a programming lesson.

## Hard rules

1. **The code is the source of truth.** README and other docs are hints only. When a doc and the code disagree, follow the code and list the mismatch in the report.
2. **Every claim has evidence.** Name the file; name the function when describing behaviour. Leave out anything you cannot point to.
3. **Never overstate.** Mark things "Not done" or "Partial". Do not invent features or incidents.
4. **Stop at "technology + file + function".** No line-by-line walkthroughs. If the reader wants more, they can ask in a new conversation.
5. **Plain words.** The first time a technology appears, explain it with one everyday comparison (e.g. "SQLite: a small database stored in a single file, like a local Excel workbook").
6. **Say what you could not read.** If a file cannot be opened, say so in the report and mark any statement that depends on it as inferred.

## Language

Before starting, ask once: **"Report language: English (default) or 中文?"** Use the answer for the whole report and for the self-test. If the user does not answer, use English.

## Steps

### 1. Take stock

- List the folder tree. Skip generated folders (`node_modules/`, `.next/`, `.git/`, `dist/`, build output).
- Read `package.json` (or the equivalent dependency file), config files and the README to list the tech stack.
- Find the **frontend / backend boundary** and say how to tell them apart (e.g. in Next.js, files starting with `"use client"` run in the browser; files starting with `"use server"` run only on the server).
- Find every **place data is stored**: database, files, cloud services, browser storage.

### 2. Trace the user flows

- Start from what a user can do: buttons, forms, pages. List the main actions.
- For each flow, follow the code from "user clicks X" to "data is stored in Y". Each step has:
  - **What happened**: one or two plain sentences.
  - **Technologies used**: what each one did in this step.
  - **Files**: path → what the file is for → the function used in this step.
- Simple create / edit / delete screens that follow the same pattern get one sentence, not a full flow.
- Point out features that exist in the code but have no visible entry point.

### 3. Run the pre-launch checklist

Go through every item in `checklist.md`. For each: status (Done / Partial / Not done), how it is done (which technology), evidence file.

### 4. Write the self-test

Write 5–7 questions. The question types are fixed; the questions themselves come from this project. Label each with its type:

| Type | Example |
|---|---|
| Frontend vs backend | After clicking X, how does the screen reach the backend? How can you tell which files run in the browser? |
| Why data is stored this way | Why is this kept in files and that in a database? |
| What if something fails | What happens if the power goes out during a save, or two places edit the same thing? |
| How the AI is constrained | How do we make sure the AI only changed what it was allowed to? |
| What's missing for launch | What would many users online need that one local user doesn't? |

Answer "What's missing for launch" with a table: feature, purpose, now (local, one user), needed (online, many users).

### 5. Build the HTML report

Write a JSON spec following `references/report-spec.md`, then run:

```
python scripts/build_report.py report.json project_report_<name>.html
```

The script produces one self-contained page with a fixed structure: side table of contents → 1. User flows → 2. Folder structure (each file tagged with its layer) → 3. Technologies (layered architecture diagram + table with a plain-words column) → 4. Data flow diagram → 5. Where data is stored → 6. Pre-launch checklist with totals → 7. Self-test (answers collapsed) → 8. Surprises found in the code (optional). Diagrams are Mermaid: rendered to inline SVG when the Mermaid CLI (`mmdc`) is installed, otherwise rendered in the browser.

For large projects (more than about 60 source files), group the tree by folder and list only the files that appear in a flow.

### 6. Check before saying it's done

- Confirm that every file path and function name in the report exists in the code.
- Confirm that every checklist item has an evidence file or is marked "Not done".
- Open the report in a browser at desktop and phone width, in light and dark mode. Nothing should scroll sideways.

### 7. Quiz the user

After sharing the report, ask the user to answer 3 of the questions **without looking**. Mark the answers against the report: what was right, what was missing. Record it as a baseline so progress can be compared next time.

## Output

- File: `project_report_<project-name>.html`
- Reply in a few sentences: how many flows, the checklist totals, and any surprises (features without an entry point, docs that disagree with the code, tests that never run).
