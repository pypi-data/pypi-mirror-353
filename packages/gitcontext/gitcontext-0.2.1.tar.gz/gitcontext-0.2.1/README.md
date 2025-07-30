# 🧠 gitx (`gitx` with `-k` for context)

> A context-aware Git CLI wrapper for multi-project repositories. Use `gitx -k ...` to activate!

---

## 💡 Why `gitx -k`?

In large research or dev repos, you often juggle multiple projects and subprojects. That makes your Git workflow chaotic:
- Unstructured branch names
- No clarity which branch belongs to which subproject
- Tedious checkouts and pushes

`gitx` introduces a **context system** using a `project.context` file. It wraps normal Git commands to:
- ✅ Automatically prefix branch names with project/subproject
- 🔍 Let you fuzzy-pick branches with `fzf`
- 🌳 Work smoothly inside worktrees
- 💥 Bypass with regular Git anytime

---

## 🚀 How It Works

You just add `-k` (or `--ctx`) to any `gitx` command to enable the context mode:
```bash
gitx -k checkout mybranch     # Resolves to: project/subproject/mybranch
gitx -k push                  # Pushes current context-prefixed branch
gitx -k branch                # Lists branches in current context
```

To fallback to normal git:
```bash
gitx status                   # Regular Git
gitx -k status                # Also regular Git (noop)
```

---

## 📂 Setup

### 🔁 Install in Dev Mode

```bash
git clone https://github.com/ax-or/gitcontext
cd gitcontext
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

Then, `gitx` is ready to use.
You can further make your git to point to gitx
```bash
alias git=gitx
```

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
gitx -k checkout feature/xyz        # Checkout branch in context
gitx -k checkout --pick             # Fuzzy pick
gitx -k create new-feature          # Create context branch
gitx -k push --force-with-lease     # Push current branch
gitx -k branch                      # List context branches
gitx -k fetch                       # Fetch remote branches under context
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
- [ ] `gitx -k squash` flow
- [ ] GitHub PR integration
- [ ] `gitx -k worktree add`
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