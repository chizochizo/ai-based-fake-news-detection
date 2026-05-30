import os
import zipfile

OUTPUT_TXT = "FULL_PROJECT.txt"
OUTPUT_ZIP = "FULL_PROJECT.zip"

# Added "venv" to completely lock out library internal codes
EXCLUDED_FOLDERS = {
    "venv",
    "checker_env",
    "__pycache__",
    ".git",
    ".cache",
    ".gradio",
    "cache"
}

# Explicitly filter out meta files, bundles, and environment files
EXCLUDED_EXTENSIONS = {
    ".txt",
    ".zip",
    ".env",
    ".pyc",
    ".pyo"
}

# ==========================================================
# BUILD LEGIT PROJECT SNAPSHOT ONLY
# ==========================================================

with open(OUTPUT_TXT, "w", encoding="utf-8") as out:
    for root, dirs, files in os.walk("."):

        # --------------------------------------------------
        # SKIP VIRTUAL ENVIRONMENTS AND INTERNAL CACHES
        # --------------------------------------------------
        dirs[:] = [d for d in dirs if d not in EXCLUDED_FOLDERS]

        for file in files:
            # Skip if file has an excluded extension (like requirements.txt or .env)
            if any(file.endswith(ext) for ext in EXCLUDED_EXTENSIONS):
                continue

            # Only target your actual Python source code files
            if not file.endswith(".py"):
                continue

            path = os.path.join(root, file)
            separator = "=" * 80

            out.write(f"\n\n{separator}\n")
            out.write(f"FILE: {path}\n")
            out.write(f"{separator}\n\n")

            try:
                with open(path, "r", encoding="utf-8") as f:
                    out.write(f.read())
            except Exception as e:
                out.write(f"\nERROR READING FILE: {e}\n")

# ==========================================================
# CREATE CLEAN ZIP
# ==========================================================
with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zipf:
    zipf.write(OUTPUT_TXT)

print("\nDONE!")
print(f"Created clean snapshot: {OUTPUT_TXT}")
print(f"Created clean zip archive: {OUTPUT_ZIP}")
