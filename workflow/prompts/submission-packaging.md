# release Prompt - Submission Packaging

Assemble the final project into a clean, operator-friendly submission bundle.

## Core Goal
- Stop treating the final paper, code, and documentation as scattered workflow residues.
- Consolidate them into one release bundle.
- Package the final bundle as a single zip archive.

## Required Release Layout

Create and populate:

- `release_submission/release_bundle/paper/`
- `release_submission/release_bundle/code/`
- `release_submission/release_bundle/docs/`

## Packaging Rules

### `paper/`
Put all paper-writing and LaTeX deliverables here:
- main `.tex` entrypoint
- section `.tex` files
- bibliography
- figures and tables used by the paper
- venue style files and checklist
- compiled PDF when available

### `code/`
Put all code deliverables here:
- method source code
- training, inference, and evaluation scripts
- config files and run helpers
- minimal reproduction-facing assets

### `docs/`
Put clear explanation documents here:
- `README.md`
- `paper-readme.md`
- `code-readme.md`
- `repro-checklist.md`

The docs should be concise, concrete, and useful to a new operator.

## Zip Rule

After the release bundle is organized, create a single zip archive for the whole bundle.

Recommended target:
- `release_submission/<project-slug>-submission-bundle.zip`

## Safety Rules

Exclude:
- `private/`
- provider keys and credentials
- raw versioned prompts
- caches and unnecessary transient artifacts
- hidden heuristics the user wants kept private

## Outputs
- `submission-manifest.json`
- `release-manifest.json`
- `checklist.md`
- `template-notes.md`
- `export-notes.md`
- `release_bundle/`
- final submission zip archive
