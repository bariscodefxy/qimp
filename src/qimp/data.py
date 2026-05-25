from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALLOWED_RISK_LEVELS = {"low", "medium", "high", "critical"}


@dataclass
class DatasetExample:
    instruction: str
    response: str
    context: str | None = None
    distro: str | None = None
    risk_level: str = "low"
    tags: list[str] | None = None
    commands: list[dict[str, Any]] | None = None
    source: str | None = None


def _normalize_commands(commands: Any) -> list[dict[str, Any]]:
    if commands is None:
        return []
    if not isinstance(commands, list):
        raise ValueError("commands must be a list")
    out: list[dict[str, Any]] = []
    for cmd in commands:
        if not isinstance(cmd, dict):
            raise ValueError("each command must be an object")
        text = cmd.get("cmd")
        if not isinstance(text, str) or not text.strip():
            raise ValueError("command entry must include non-empty 'cmd'")
        out.append(
            {
                "cmd": text.strip(),
                "destructive": bool(cmd.get("destructive", False)),
                "requires_confirmation": bool(cmd.get("requires_confirmation", False)),
                "notes": str(cmd.get("notes", "")).strip(),
            }
        )
    return out


def validate_example(raw: dict[str, Any]) -> DatasetExample:
    instruction = raw.get("instruction")
    response = raw.get("response")
    if not isinstance(instruction, str) or not instruction.strip():
        raise ValueError("instruction is required")
    if not isinstance(response, str) or not response.strip():
        raise ValueError("response is required")

    risk_level = str(raw.get("risk_level", "low")).lower()
    if risk_level not in ALLOWED_RISK_LEVELS:
        raise ValueError(f"risk_level must be one of {sorted(ALLOWED_RISK_LEVELS)}")

    tags = raw.get("tags")
    if tags is None:
        tags_list: list[str] = []
    elif isinstance(tags, list) and all(isinstance(t, str) for t in tags):
        tags_list = [t.strip() for t in tags if t.strip()]
    else:
        raise ValueError("tags must be a list[str]")

    return DatasetExample(
        instruction=instruction.strip(),
        response=response.strip(),
        context=(str(raw.get("context")).strip() if raw.get("context") else None),
        distro=(str(raw.get("distro")).strip() if raw.get("distro") else None),
        risk_level=risk_level,
        tags=tags_list,
        commands=_normalize_commands(raw.get("commands")),
        source=(str(raw.get("source")).strip() if raw.get("source") else None),
    )


def to_chat_messages(example: DatasetExample, system_prompt: str) -> list[dict[str, str]]:
    user_parts = [example.instruction]
    if example.context:
        user_parts.append(f"Context: {example.context}")
    if example.distro:
        user_parts.append(f"Distribution: {example.distro}")
    user_content = "\n\n".join(user_parts)

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_content},
        {"role": "assistant", "content": example.response},
    ]


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                yield i, json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at line {i}: {exc}") from exc


def prepare_dataset(raw_path: Path, processed_path: Path, system_prompt: str) -> int:
    processed_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with processed_path.open("w", encoding="utf-8") as out:
        for _, obj in iter_jsonl(raw_path):
            example = validate_example(obj)
            record = {
                "messages": to_chat_messages(example, system_prompt),
                "metadata": {
                    "risk_level": example.risk_level,
                    "distro": example.distro,
                    "tags": example.tags or [],
                    "commands": example.commands or [],
                    "source": example.source,
                },
            }
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1
    return count
