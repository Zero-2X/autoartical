# Submission Packaging

Use this reference when assembling the final project deliverable for submission, archival, or record.

## Packaging goal

writing should not leave the final project scattered across many workflow folders.

Before packaging, consolidate the final deliverable into a clean release directory with three clear subfolders:

- `paper/` for LaTeX and paper-writing assets
- `code/` for runnable code and experiment scripts
- `docs/` for explanation and reproduction notes

Then package the whole release directory into a single zip archive.

## Required release layout

```text
release_submission/release_bundle/
  paper/
  code/
  docs/
```

## `paper/` rules

Put all final paper-writing assets here, including:

- main LaTeX source
- section `.tex` files
- bibliography
- figure and table assets used by the paper
- venue style files and checklist when needed
- compiled PDF if available

Do not leave final LaTeX spread only across raw workflow folders once writing packaging starts.

## `code/` rules

Put all code-side deliverables here, including:

- source code needed to run the method
- scripts needed to reproduce the reported experiments
- config files, launch scripts, and evaluation helpers
- lightweight README or entry instructions if needed

Exclude versioned prompts, secrets, and unnecessary cache or transient artifacts.

## `docs/` rules

This folder should make the release understandable to another operator.

Include clear documentation such as:

- `README.md` for top-level bundle explanation
- `paper-readme.md` describing the LaTeX layout and compile entrypoint
- `code-readme.md` describing how to run or reproduce code artifacts
- optional `repro-checklist.md` or `artifact-notes.md`

The writing should be brief, concrete, and operational.

## Zip packaging rule

After the release directory is organized, produce a single zip archive of the whole final bundle.

Recommended artifact:

- `release_submission/<project-slug>-submission-bundle.zip`

The zip should contain the structured release folder, not a flat dump of mixed files.

## Safety rules

Before zipping, exclude:

- `private/`
- provider keys and credentials
- raw versioned prompts
- hidden heuristics the user wants kept private
- caches, checkpoints, and oversized artifacts not needed for review or reproduction

## Manifest expectations

The submission manifest should explicitly record:

- paper folder path
- code folder path
- docs folder path
- zip archive path
- included paper assets
- included code assets
- included docs assets
- exclusions and compliance notes
