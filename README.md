# boilercrib-scraper

---

## Setup

Python 3.14+ is required

### With [uv](https://docs.astral.sh/uv/)

```bash
uv sync
```

### With [pip](https://pypi.org/project/pip/)

```bash
python -m venv .venv
source .venv/bin/activate  # .venv\Scripts\activate on Windows
pip install -e .
```

If `pip install --group dev .` doesn't work on your pip version (<25.1), install the dev dependencies manually:

```bash
pip install pytest ruff black
```

### Verify it worked

```bash
pytest
```

or

```bash
uv run pytest
```

Should report "no tests ran".
