# ![RustyPipe](https://codeberg.org/ThetaDev/rustypipe/raw/branch/main/notes/logo.svg) YT-DLP-Botguard

[![Current PyPI version](https://img.shields.io/pypi/v/yt-dlp-get-pot-rustypipe.svg)](https://pypi.org/project/yt-dlp-get-pot-rustypipe)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=flat)](https://opensource.org/licenses/MIT)

`yt-dlp-get-pot-rustypipe` is a yt-dlp
[GetPOT](https://github.com/coletdjnz/yt-dlp-get-pot) token provider that uses
[rustypipe-botguard](https://codeberg.org/ThetaDev/rustypipe-botguard) to generate PO
tokens.

It supports all web-based YouTube clients (`web`, `web_safari`, `web_music`, `mweb`
`tv`, `tv_embedded`, `web_embedded`, `web_creator`).

## Installation

1. Download and extract the rustypipe-botguard binary from
   <https://codeberg.org/ThetaDev/rustypipe-botguard/releases> and place it either in
   the PATH or the current working directory.
2. Install the `yt-dlp-get-pot-rustypipe` plugin

**pipx**

```sh
pipx inject yt-dlp yt-dlp-get-pot-rustypipe
```

**pip**

```sh
pip install yt-dlp-get-pot-rustypipe
```

If installed correctly, you should see the `rustypipe-botguard` PO Token provider in the
`yt-dlp -v YOUTUBE_URL` output.

```txt
[debug] [GetPOT] PO Token Providers: rustypipe-botguard-0.1.0
```

## Options

The plugin can be configured using extractor arguments, for example
`--extractor-args 'youtube:rustypipe_bg_pot_cache=1;rustypipe_bg_bin=/path/to/rustypipe-botguard'`.

- `rustypipe_bg_bin`: Custom path to rustypipe-botguard binary.
- `rustypipe_bg_snapshot_file` Custom path to load/store a snapshot of the Botguard
  runtime.
- `rustypipe_bg_no_snapshot` Do not load/store a snapshot of the Botguard runtime
  (default: `false`).
- `rustypipe_bg_pot_cache` Reuse generated session PO tokens (default: `true`).
- `rustypipe_bg_user_agent` Set a custom user agent for fetching Botguard challenges.
