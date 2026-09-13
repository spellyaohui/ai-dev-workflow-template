from __future__ import annotations

from dataclasses import dataclass
from fnmatch import fnmatchcase
import json
from pathlib import Path


@dataclass(frozen=True)
class RiskResult:
    level: str
    reasons: tuple[str, ...]


def _load_config(config_path: str) -> dict:
    return json.loads(Path(config_path).read_text(encoding="utf-8"))


def effective_risk(
    spec_risk: str | None,
    pr_risk: str | None,
    verifier_risk: str | None,
    changed_paths: list[str],
    categories: list[str] | None = None,
    config_path: str = ".github/ai-governance.yml",
) -> RiskResult:
    config = _load_config(config_path)
    reasons: list[str] = []

    declared = {
        "spec": spec_risk,
        "pr": pr_risk,
        "verifier": verifier_risk,
    }
    for source, value in declared.items():
        if value not in {"LOW", "HIGH"}:
            reasons.append(f"{source} risk is missing or invalid")
        elif value == "HIGH":
            reasons.append(f"{source} risk is HIGH")

    for path in changed_paths:
        for pattern in config.get("high_risk_paths", []):
            if fnmatchcase(path, pattern):
                reasons.append(f"high-risk path: {path}")
                break

    configured_categories = set(config.get("high_risk_categories", []))
    for category in categories or []:
        if category in configured_categories:
            reasons.append(f"high-risk category: {category}")

    level = "HIGH" if reasons else "LOW"
    return RiskResult(level=level, reasons=tuple(reasons))
