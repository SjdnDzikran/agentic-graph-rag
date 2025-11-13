# Local Environment Setup

Follow these steps to recreate the PDF-processing environment used in this
repository.

## 1. Prerequisites
- Python 3.12 (or a compatible Python 3.9+ interpreter)
- `pip` (ships with modern Python releases)

## 2. Create a Virtual Environment
```bash
python3 -m venv .venv
```

## 3. Activate the Environment
- **macOS / Linux**
  ```bash
  source .venv/bin/activate
  ```
- **Windows (PowerShell)**
  ```powershell
  .\.venv\Scripts\Activate.ps1
  ```
- **Windows (cmd.exe)**
  ```cmd
  .\.venv\Scripts\activate.bat
  ```

Your shell prompt will show `(.venv)` once the environment is active.

## 4. Install Dependencies
With the virtual environment activated:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Verify the Setup
Run a quick Python check to ensure `pypdf` is available:
```bash
python - <<'PY'
from pypdf import PdfReader
print("PyPDF ready with", PdfReader.__name__)
PY
```

## 6. Daily Workflow
1. Activate the environment (`source .venv/bin/activate` or Windows equivalent).
2. Work on the project.
3. When finished, exit the environment with:
   ```bash
   deactivate
   ```

> Tip: If new dependencies are added later, update `requirements.txt` with
> `pip freeze > requirements.txt` so everyone can stay in sync.
