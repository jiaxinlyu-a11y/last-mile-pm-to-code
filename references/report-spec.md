# Report spec (input for `scripts/build_report.py`)

One JSON file. Everything is plain text; the script escapes it.

```json
{
  "lang": "en",
  "project": { "name": "My App", "summary": "One or two sentences on what the app is." },

  "flows": [
    {
      "id": "flow-a",
      "name": "Save a chapter",
      "scene": "You edit a chapter and click Save.",
      "steps": [
        {
          "title": "Send the text",
          "what": "Plain-words description of what happens.",
          "layer": "Interface",
          "tech": [["React", "What React does in this step"]],
          "files": [["src/ui/editor.tsx", "What the file is for", "saveChapter: what this function does here"]]
        }
      ],
      "note": "Optional note under the flow."
    }
  ],
  "other_flows_note": "Optional: one sentence covering simple create/edit/delete screens.",

  "tree": [[0, "my-app/", "Project root", true, ""], [1, "package.json", "Dependencies and commands", false, "Dev tools"]],

  "arch_mermaid": "flowchart TB ...",
  "dataflow_mermaid": "flowchart LR ...",

  "tech": [["SQLite", "A small database in one file", "Storage", "Stores projects and characters"]],
  "storage": [["data/app.db", "What is stored", "Why it is stored there"]],

  "checklist": [["Input validation", "done", "How it is done", "src/validation/form.ts"]],

  "quiz": [
    { "type": "Why data is stored this way", "question": "…", "answer": "…" },
    { "type": "What's missing for launch", "question": "…",
      "table": { "headers": ["#", "Feature", "Purpose", "Now", "Needed"], "rows": [["1", "…", "…", "…", "…"]] } }
  ],

  "findings": ["Optional list of surprises found in the code."]
}
```

Field notes:

- `lang`: `"en"` or `"zh"`; sets all headings and labels.
- `tree` rows: `[depth, name, description, is_folder, layer]`. Use an empty string for no layer tag.
- `files` rows: `[path, what the file is for, function or null]`.
- `checklist` status: `"done"`, `"partial"` or `"missing"`. Use `""` for evidence when there is none.
- Layers used so far: Interface, Application, Data access, Storage, Rules & validation, Dev tools, Docs, External AI.
- In the architecture diagram, list technologies and their role per layer; do not list file names (files belong in the tree).
