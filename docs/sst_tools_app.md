<!-- NEXT: tools: explain functions -->

# How to launch tools app

## Folder Scanner

- Compile multiple files into 1

### Launch inside Project, Target outside

- Approach 1

```sh
export TARGET_ROOT=~/lsco-summary
uv run python -m sstcore.cli.launch scanner -r $TARGET_ROOT
```

- Approach 2

```sh
export TARGET_ROOT=~/lsco-summary
uv run sst scanner -r $TARGET_ROOT
```

### Install from inside Project, global on System

```sh
uv tool install --force -e ".[cli]"
```
