# 🧠 git-ctx

> A context-aware Git CLI tool for multi-project research repositories.

**`git-ctx`** helps you manage Git branches across multiple projects and subprojects using a smart prefixing system. It wraps common Git commands with context from a `project.context` file, letting you organize branches, worktrees, and workflows efficiently — all while giving you fuzzy selection, squash support, and custom push options.

---

## 🔧 Why `git-ctx`?

Managing a single monorepo with several parallel research or development projects often leads to chaos:

- Unstructured branch names
- No context on what belongs to which subproject
- Tedious git commands when juggling multiple trees
- Hard to discover or switch branches

`git-ctx` fixes this by introducing:

✔️ Context-based branch prefixing  
✔️ Clean worktree integration  
✔️ Fuzzy branch checkout  
✔️ Optional commit squashing  
✔️ Custom push flags (`--force`, `--no-verify`, etc.)  
✔️ Configurable with a simple `project.context` file  
✔️ Full passthrough to regular `git` via `--git` flag

---

## 📦 Installation

### 🔁 Clone and Install (Editable Dev Mode)

```bash
git clone https://github.com/ax-or/gitcontext.git
cd gitcontext
python -m venv venv
source venv/bin/activate
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
```

> 🛠️ `click`, `pytest`, `ruff`, `black`, and `pre-commit` will be installed if you use `[dev]`.

---

## 📂 `project.context` Format

At the root of your Git repo, add:

```ini
[context]
project = vision
subproject = segmentation
```

If you don't have a subproject:

```ini
[context]
project = vision
```

This will prefix your branches like:
- `vision/main`
- `vision/segmentation/feature-x`

---

## 🚀 Usage

### 🧱 Branch Management

```bash
git-ctx create feature/transformer-rewrite         # Creates vision/segmentation/feature/transformer-rewrite
git-ctx checkout bugfix/loss-calc                  # Checks out vision/segmentation/bugfix/loss-calc
git-ctx checkout --pick                            # Pick interactively using fzf
git-ctx branch                                     # List all local branches under current context
git-ctx fetch                                      # Fetch only branches under current context
```

### 📤 Pushing with Flags

```bash
git-ctx push --force-with-lease
git-ctx push --no-verify
```

Supports all dynamic flags: `--force`, `--tags`, `-o ci.skip`, etc.

### 🧩 Git Override Mode

Need to bypass `git-ctx` and run raw git commands?

```bash
git-ctx --git status
git-ctx --git log --oneline
```

This is equivalent to running `git status` or `git log --oneline`, and ignores all context logic.

Perfect when you just want normal git behavior without switching tools.

---

## 🧼 Squash Support (Coming Soon)

```bash
git-ctx squash --base main --autosquash --push --force-with-lease
```

Allows selective squashing of commits before pushing or PR. Ideal for keeping research commits clean and minimal.

---

## 🌳 Worktree-Friendly

`git-ctx` works seamlessly inside Git worktrees. Just navigate into any worktree, and it’ll resolve context and branches as expected.

---

## 🧪 Testing

### Run all tests:

```bash
pytest -v tests/
```

### Structure:
- `tests/test_cli.py`: unit tests for prefix logic, branch creation, error handling, etc.
- Uses `pytest` and `click.testing.CliRunner`
- Simulates fake `.git` repos and project contexts

---

## 🎯 Linting & Dev Workflow

```bash
ruff git_ctx
black git_ctx
pre-commit run --all-files
```

Pre-commit hooks are available if you install via `[dev]`.

---

## 🔌 Integration with `fzf`

Fuzzy branch selection relies on [fzf](https://github.com/junegunn/fzf):

```bash
# Install on macOS:
brew install fzf

# On Ubuntu:
sudo apt install fzf
```

---

## 🔐 Permissions & Safe Defaults

- Only works inside a Git repo with `project.context`
- Prevents accidental checkout or push outside scope
- Outputs all Git commands it runs

---

## 📁 Example Branch Structure

If you're working on:

```ini
[context]
project = nlp
subproject = textgen
```

Then branches will look like:

```
nlp/textgen/main
nlp/textgen/feature/streaming
nlp/textgen/bugfix/gpu-crash
```

No more guessing where a branch belongs. 🍷

---

## 🤖 Planned Features

- [ ] Interactive squash flow
- [ ] Worktree manager: `git-ctx worktree add --branch xxx`
- [ ] Dashboard: `git-ctx status` across contexts
- [ ] Cross-context search and branch management
- [ ] GitHub PR integration (open PR from CLI)

---

## 🛠 Developer Setup

```bash
pip install -e ".[dev]"
pre-commit install
pytest -v
```

> Want to contribute? Open an issue or drop a PR with your idea 💡

---

## 📜 License

MIT © [AxOr](https://axiomsandorbits.xyz)  
Built for clarity, context, and collaborative chaos management 🧠⚙️

---

## ⭐️ Contribute & Share

If you find this tool useful:
- Star 🌟 the repo
- Share it with your team
- File feature requests or bug reports

Together, we can make Git suck less for research work. 😎
