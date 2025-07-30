# scripts/write_version.py
import re
import pathlib

def extract_version():
    with open("pyproject.toml", "r", encoding="utf-8") as f:
        content = f.read()
    match = re.search(r'version\s*=\s*"([^"]+)"', content)
    return match.group(1) if match else "unknown"

def write_version_file(version: str):
    version_file = pathlib.Path("src/rongcloud_server_mcp/version.py")
    version_file.write_text(f'__version__ = "{version}"\n', encoding="utf-8")

if __name__ == "__main__":
    version = extract_version()
    write_version_file(version)
    print(f"✅ Version written: {version}")
