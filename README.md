# code-snippets
### Author: Soubhik Barari

Code snippets for data science (mostly) in Python, R, and other languages compiled over the years. Contains utilities to convert/transfer snippets to Sublime Text 3 and R Studio.

- `cp_<src>_to_<dest>.py`: copy snippets between locations (e.g. this directory, R Studio snippets location)
- `sync_github.sh`: default script to sync with GitHub repo
- `sync_snippets.py`: sync code snippets between different IDEs (e.g. R Studio and Sublime Text).
- `sync_snippets_local.sh`: copy `*.snippets` files from this directory to R Studio, and re-generate Sublime Text snippet files.

## Suggested Workflow

1. Pull to local machine.
2. Fill in path variables in `config.env`.
3. Edit snippet files in this directory as needed.
4. Run `sync_snippets_local.sh` to transfer local snippets to R Studio and Sublime Text.
