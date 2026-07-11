# Abstracts (reviewer input)

Drop **real** paper abstracts here so the reviewer works on source text, not just the
title and metadata. The system never fabricates an abstract — if a file is missing, the
reviewer proceeds on metadata alone and flags `needs_full_text_confirmation`.

## How to add one

Create a plain-text (`.txt`) or Markdown (`.md`) file named after the paper's **gold_id**,
**PMID** or **DOI** (replace `/` with `_`). The first match wins, in that order.

Examples for the curated Gold Standard entries:

```
sources/abstracts/GOLD-PRP-001.txt      # by gold_id
sources/abstracts/32302218.txt          # by PMID (Belk 2021)
sources/abstracts/10.1177_0363546520909397.txt   # by DOI (/ -> _)
```

Paste the abstract text (copied from the journal / PubMed) into the file and save. Then:

```bash
./kra benchmark --model claude
```

The reviewer will now review the real abstract. Keep these files to what you are entitled
to use; they are inputs for your personal research, not redistributed content.
