#!/usr/bin/env python3
"""Assemble a local repo-ready Maverick package without publishing it."""

from __future__ import annotations

import hashlib
import json
import shutil
import time
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
APP_DIR = ROOT / "factory" / "active" / "maverick-cockpit"
GLOBAL_REPO_DIR = APP_DIR / "global-repo"
PACKAGE_DIR = GLOBAL_REPO_DIR / "package"
ASSEMBLY_LOCK_DIR = GLOBAL_REPO_DIR / ".assembly.lock"
ASSEMBLY_MANIFEST_PATH = GLOBAL_REPO_DIR / "assembly-manifest.json"
REPO_CONTRACT_PATH = GLOBAL_REPO_DIR / "repo-contract.json"
GLOBAL_REPO_ASSEMBLED_AT = "2026-06-14T16:42:36-04:00"
ASSEMBLY_LOCK_TIMEOUT_SECONDS = 15.0


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_file(source: Path, target: Path) -> dict[str, Any]:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return {
        "source": str(source.relative_to(ROOT)),
        "target": str(target.relative_to(PACKAGE_DIR)),
        "bytes": target.stat().st_size,
        "sha256": _sha256(target),
    }


def _copy_tree_files(source_dir: Path, target_dir: Path, patterns: list[str]) -> list[dict[str, Any]]:
    copied = []
    for pattern in patterns:
        for source in sorted(source_dir.glob(pattern)):
            if source.is_file():
                copied.append(_copy_file(source, target_dir / source.relative_to(source_dir)))
    return copied


class _AssemblyLock:
    """Serialize package rebuilds across validators and export runners."""

    def __enter__(self) -> "_AssemblyLock":
        deadline = time.monotonic() + ASSEMBLY_LOCK_TIMEOUT_SECONDS
        while True:
            try:
                ASSEMBLY_LOCK_DIR.mkdir(parents=True)
                return self
            except FileExistsError:
                if time.monotonic() >= deadline:
                    raise TimeoutError(f"timed out waiting for assembly lock: {ASSEMBLY_LOCK_DIR}") from None
                time.sleep(0.05)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        shutil.rmtree(ASSEMBLY_LOCK_DIR, ignore_errors=True)


def assemble_package(observed_at: str = GLOBAL_REPO_ASSEMBLED_AT) -> dict[str, Any]:
    with _AssemblyLock():
        contract = _load_json(REPO_CONTRACT_PATH)
        if PACKAGE_DIR.exists():
            shutil.rmtree(PACKAGE_DIR)
        PACKAGE_DIR.mkdir(parents=True)

        copied = []
        copied.append(_copy_file(ROOT / contract["standalone_readme"], PACKAGE_DIR / "README.md"))
        copied.append(_copy_file(ROOT / contract["confirmation_request"], PACKAGE_DIR / "CONFIRMATION_REQUEST.md"))
        copied.append(_copy_file(GLOBAL_REPO_DIR / "netlify.toml", PACKAGE_DIR / "netlify.toml"))

        copied.extend(_copy_tree_files(ROOT / "docs", PACKAGE_DIR / "docs", ["maverick-*.md"]))
        copied.extend(_copy_tree_files(APP_DIR / "dashboard", PACKAGE_DIR / "cockpit", ["*.html", "*.css", "*.js", "*.svg", "*.webmanifest", "data/*.json"]))
        copied.extend(_copy_tree_files(APP_DIR, PACKAGE_DIR / "contracts", ["*.json", "adapters/*.json", "samples/*.json"]))
        for source in [
            APP_DIR / "write-gates" / "write-gate-contract.json",
            APP_DIR / "global-repo" / "repo-contract.json",
            APP_DIR / "global-repo" / "package-manifest.json",
        ]:
            copied.append(_copy_file(source, PACKAGE_DIR / "contracts" / source.relative_to(APP_DIR)))
        copied.extend(_copy_tree_files(ROOT / "factory", PACKAGE_DIR / "scripts", ["maverick_*.py", "validate_maverick.py"]))
        copied.append(_copy_file(ROOT / "factory" / "schemas" / "maverick-workplace.schema.json", PACKAGE_DIR / "schemas" / "maverick-workplace.schema.json"))

        manifest = {
            "generated_at": observed_at,
            "package_dir": str(PACKAGE_DIR.relative_to(ROOT)),
            "repo_contract": str(REPO_CONTRACT_PATH.relative_to(ROOT)),
            "suggested_repo_name": contract["suggested_repo_name"],
            "publish_gate": contract["publish_gate"],
            "export_gate": contract["export_gate"],
            "external_mutation_attempted": False,
            "external_mutation_allowed": False,
            "file_count": len(copied),
            "files": copied,
        }
        ASSEMBLY_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        return manifest


def main() -> int:
    manifest = assemble_package()
    print(json.dumps({
        "assembly_manifest": str(ASSEMBLY_MANIFEST_PATH.relative_to(ROOT)),
        "package_dir": manifest["package_dir"],
        "file_count": manifest["file_count"],
        "external_mutation_attempted": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
