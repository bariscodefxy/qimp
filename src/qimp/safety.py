from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass
class SafetyFinding:
    command: str
    risk: str
    reason: str


PATTERNS: list[tuple[re.Pattern[str], str, str]] = [
    (re.compile(r"\brm\s+-rf\b", re.IGNORECASE), "critical", "recursive deletion"),
    (re.compile(r"\bmkfs(\.|\s)"), "critical", "filesystem formatting"),
    (re.compile(r"\bdd\s+if=.*of=/dev/", re.IGNORECASE), "critical", "raw disk overwrite"),
    (re.compile(r"\b(userdel|deluser)\b", re.IGNORECASE), "high", "user deletion"),
    (re.compile(r"\b(chmod\s+777|chmod\s+-R\s+777)\b", re.IGNORECASE), "high", "permission weakening"),
    (re.compile(r"\b(ufw\s+disable|systemctl\s+stop\s+firewalld|iptables\s+-F)\b", re.IGNORECASE), "high", "firewall disable/reset"),
    (re.compile(r"\b(grub-install|update-grub|grub2-mkconfig)\b", re.IGNORECASE), "high", "bootloader modification"),
    (re.compile(r"\b(fdisk|parted|gdisk|cfdisk)\b", re.IGNORECASE), "high", "partition operation"),
    (re.compile(r"\b(systemctl\s+stop\s+(sshd|network|NetworkManager))\b", re.IGNORECASE), "high", "core service disruption"),
    (re.compile(r"\b(docker\s+system\s+prune\s+-a|podman\s+system\s+prune\s+-a)\b", re.IGNORECASE), "high", "destructive container prune"),
]


def assess_commands(text: str) -> list[SafetyFinding]:
    findings: list[SafetyFinding] = []
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    for line in lines:
        for pattern, risk, reason in PATTERNS:
            if pattern.search(line):
                findings.append(SafetyFinding(command=line, risk=risk, reason=reason))
                break
    return findings


def has_high_risk(text: str) -> bool:
    return any(f.risk in {"high", "critical"} for f in assess_commands(text))
