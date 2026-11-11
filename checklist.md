# Pre-launch checklist

Check every item. For each, record: status (Done / Partial / Not done), how it is done, and the evidence file.
"Common ways" are hints for spotting an implementation; other approaches count too.

| # | Check | Question to answer | Common ways |
|---|---|---|---|
| 1 | Access boundaries | Is what the program can reach limited? Who can see and change what? | Login, roles, an allowed folder, rejecting `../` paths, local-only server |
| 2 | Read-back after writes | After saving, or after the AI changes something, is the result read back and checked? | "Exactly one row changed" checks, re-reading after a write, checking markers or structure |
| 3 | Failure recovery | If something fails half-way, is data corrupted? Can it be retried? | Write to a temporary file then rename, database transactions, staging folders, undo on failure |
| 4 | Human confirmation | Do risky actions need a person to confirm? | Confirm dialogs, typing the exact ID, preview before apply, AI output kept as a draft |
| 5 | Input validation | Is data checked before it is stored? | Zod or similar schema libraries, regular expressions, hand-written checks |
| 6 | Data versions & migration | Does old data still work after the format changes? | Version field in stored data, migration scripts, adding missing columns at start-up |
| 7 | Automated tests | Is there an automatic way to check nothing broke? | Vitest, Jest, node:test, pytest; check the test config actually includes every test file |
| 8 | Privacy & secrets | Could passwords, keys or personal data end up on GitHub? | `.gitignore`, `.env` files, keeping user data outside the repository |
| 9 | Scope control | Is it written down what the project deliberately does not do? | A "not in scope" list in docs or AGENTS.md |
| 10 | Logging | When something goes wrong, can you find out what happened? | Log files, error monitoring services |
| 11 | Backup & rollback | If data is damaged or changed by mistake, can it be restored? | Git, scheduled database backups, a recycle bin |
| 12 | Audit trail | Can you see who changed what, and when? | An activity table, a change log |

## Adding a check

Add a row with the check, the question it answers and common ways. Good sources: interview questions, other people's incident write-ups, new concepts you have learned.
