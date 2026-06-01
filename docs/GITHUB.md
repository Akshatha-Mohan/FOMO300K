# GitHub

```bash
export PATH="$HOME/.local/bin:$PATH"
gh auth login -h github.com -p https -w
cd /shared/home/akshatha/FOMO300K
./scripts/setup_github.sh
```

Creates [Akshatha-Mohan/FOMO300K](https://github.com/Akshatha-Mohan/FOMO300K) and pushes `main`.

Private repo: `gh repo create FOMO300K --private --source=. --remote=origin --push`
