# Feature: Timestamped Outputs

**Branch:** `feature/timestamped-outputs`
**Type:** Simple feature

## What it does

Each run of `mask.py` now saves its 144 attention diagrams in its own folder,
`outputs/<YYYY-MM-DD_HH-MM-SS>/`, instead of writing them to the working
directory. The path of the folder is printed when the diagrams are generated.

## Why

Previously every run overwrote the `Attention_Layer*_Head*.png` files of the
previous run, so results from different sentences could not be compared or
kept.

## How it works

- `visualize_attentions` creates the folder
  `BASE_DIR / "outputs" / <timestamp>` and prints its path.
- The folder is passed to `generate_diagram` through the new optional
  `output_dir` parameter.
- If `output_dir` is not given, `generate_diagram` falls back to `BASE_DIR`,
  so existing callers keep working.
- `outputs/` is listed in `.gitignore`.

## How to test

```bash
python mask.py
```

```
Text: We turned down a narrow lane and passed by a small [MASK].
```

Check that:

1. The terminal prints `Saving attention diagrams to: .../outputs/<timestamp>`.
2. That folder contains 144 files named `Attention_Layer{N}_Head{M}.png`.
3. Running the program a second time creates a second folder and leaves the
   first one untouched.