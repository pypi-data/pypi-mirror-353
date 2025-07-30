# 🧠 git-ctx (`git` with `-k` for context)

> A context-aware Git CLI wrapper for multi-project repositories. Use `git -k ...` to activate!

---

## 💡 Why `git -k`?

In large research or dev repos, you often juggle multiple projects and subprojects. That makes your Git workflow chaotic:
- Unstructured branch names
- No clarity which branch belongs to which subproject
- Tedious checkouts and pushes

`git-ctx` introduces a **context system** using a `project.context` file. It wraps normal Git commands to:
- ✅ Automatically prefix branch names with project/subproject
- 🔍 Let you fuzzy-pick branches with `fzf`
- 🌳 Work smoothly inside worktrees
- 💥 Bypass with regular Git anytime

---

## 🚀 How It Works

You just add `-k` (or `--ctx`) to any `git` command to enable the context mode:
```bash
git -k checkout mybranch     # Resolves to: project/subproject/mybranch
git -k push                  # Pushes current context-prefixed branch
git -k branch                # Lists branches in current context
```

To fallback to normal git:
```bash
git status                   # Regular Git
git -k status                # Also regular Git (noop)
```

---

## 📂 Setup

### 🔁 Install in Dev Mode

```bash
git clone https://github.com/your-user/gitctx.git
cd gitctx
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Then, alias your local script as `git`:
```bash
alias git='python /path/to/git_ctx_k.py'
```

Or install globally with an entry point (`[project.scripts]`) in `pyproject.toml`.

---

## 📄 `project.context` Format

At the root of your repo, define the context:

```ini
[context]
project = vision
subproject = segmentation
```

If no subproject:
```ini
[context]
project = vision
```

Your branch names will automatically be prefixed:
- `vision/main`
- `vision/segmentation/feature-x`

---

## ⚙️ Supported Commands

```bash
git -k checkout feature/xyz        # Checkout branch in context
git -k checkout --pick             # Fuzzy pick
git -k create new-feature          # Create context branch
git -k push --force-with-lease     # Push current branch
git -k branch                      # List context branches
git -k fetch                       # Fetch remote branches under context
```

---

## 🔍 Requirements

- Python 3.8+
- `fzf` (for interactive mode)

---

## 🔬 Testing

```bash
pytest tests/
```

---

## 🧪 Future Features

- [ ] Commit squashing with autosquash
- [ ] `git -k squash` flow
- [ ] GitHub PR integration
- [ ] `git -k worktree add`
- [ ] Cross-context dashboard

---

## 📜 License

MIT © [AxOr](https://axiomsandorbits.xyz)

---

## ⭐️ Contribute

If you find this useful:
- Star the repo ⭐️
- Share it
- File issues and ideas 🧠
