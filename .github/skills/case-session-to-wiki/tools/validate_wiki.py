#!/usr/bin/env python3
"""Read-only, offline checks for an explicitly declared, approved wiki bundle."""

from __future__ import annotations

import argparse
from bisect import bisect_right
import hashlib
import ipaddress
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from itertools import islice
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


SCHEMA_VERSION = 1
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_ARTICLES = 32
MAX_SOURCES = 256
MAX_CLAIMS = 512
MAX_TEXT_CHARS = 4096
MAX_HEADINGS = 2048
MAX_CITATIONS = 4096
MAX_CLAIM_OCCURRENCES = 64
LIMITATIONS = [
    "source-authenticity-not-verified",
    "regex-redaction-not-proof",
    "claim-map-completeness-not-verified",
    "semantic-support-not-independently-verified",
    "reviewer-identity-not-authenticated",
    "no-execution-or-publication-authorization",
]
HEADINGS = {
    "qa": [
        "Topic and scope", "Questions and answers", "Open questions and limitations",
        "References and original excerpts", "Review checklist",
    ],
    "how-to": [
        "Goal and success criteria", "Prerequisites and concepts", "Step-by-step procedure",
        "End-to-end verification", "Troubleshooting and rollback",
        "Open questions and limitations", "References and original excerpts", "Review checklist",
    ],
    "break-fix": [
        "Problem and applicability", "Confirm this is the same issue", "Cause and confidence",
        "Resolution or workaround", "Verification", "Escalation and prevention",
        "Open questions and limitations", "References and original excerpts", "Review checklist",
    ],
}
SOURCE_FIELDS = {
    "id", "kind", "title", "publisher", "origin", "locator", "version",
    "inspection_status", "text", "excerpt_handling",
}
SOURCE_MARKDOWN_FIELDS = [
    "Source type", "Evidence record", "Title", "Publisher or source role", "Origin",
    "Exact location", "Version or revision", "Access", "Verification", "Inspected on",
    "Supports", "Excerpt handling", "Original excerpt", "Interpretation and limits",
]
METADATA_VALUES = {
    "wiki_type": set(HEADINGS),
    "status": {"draft"},
    "review_status": {"pending-engineer-review"},
    "source_kind": {"current-session", "provided-transcript", "local-session"},
    "source_coverage": {
        "partial", "complete-for-provided-transcript", "complete-for-selected-visible-events",
    },
    "content_mode": {"documentation-enriched", "extraction-only"},
    "reference_status": {"incomplete", "mechanically-checked", "complete"},
}
OUTCOMES = {
    "qa": {},
    "how-to": {
        "procedure_status": {"unverified", "documented-not-tested", "verified-in-source"},
    },
    "break-fix": {
        "root_cause_status": {"unknown", "suspected", "confirmed"},
        "resolution_status": {"unverified", "reported", "verified"},
    },
}
PROVENANCES = {"observed-in-session", "documentation-enriched", "adapted-from-documentation"}
EXECUTION_VALIDATIONS = {"not-run", "syntax-only", "lab-tested"}
SAFE_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]{0,99}\.(?:md|json)\Z")
SOURCE_ID = re.compile(r"S[1-9][0-9]{0,5}\Z")
CLAIM_ID = re.compile(r"C[1-9][0-9]{0,5}\Z")
CITATION = re.compile(r"\[(S[1-9][0-9]*)\]\(#(s[1-9][0-9]*)\)")
FIELD = re.compile(r"^\*\*([^*\n]+):\*\*(?:[ \t]*(.*))?$", re.MULTILINE)
LINK = re.compile(r"!?\[([^\[\]\n]*)\]\(([^()\n]*)\)")
HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*#*\s*$", re.MULTILINE)
SUSPICIOUS = {
    "guid": re.compile(r"(?i)(?<![0-9a-f])[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}(?![0-9a-f])"),
    "case-shaped-id": re.compile(r"(?<![A-Za-z0-9])\d{13,20}(?![A-Za-z0-9])"),
    "email": re.compile(r"(?i)(?<![a-z0-9.!#$%&'*+/=?^_`{|}~-])[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+"),
    "user-path": re.compile(r"(?i)(?:[a-z]:[\\/]+users[\\/]|/(?:home|users)/|file://|\\\\[a-z0-9_.-]+\\)"),
    "private-key": re.compile(r"-----BEGIN (?:[A-Z0-9 ]* )?PRIVATE KEY-----"),
    "bearer": re.compile(r"(?i)\bbearer\s+\S+"),
    "credential": re.compile(
        r"(?i)\b(?:access[_-]?token|refresh[_-]?token|api[_-]?key|client[_-]?secret|"
        r"password|accountkey|sharedaccesssignature)\s*[:=]\s*['\"]?\S+"
    ),
    "signed-url": re.compile(r"(?i)[?&](?:sig|signature|token|access_token|code|key|x-amz-[\w-]+|x-goog-[\w-]+)="),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
}


@dataclass(frozen=True)
class Issue:
    code: str
    location: str
    domain: str = "mechanical"

    def as_dict(self) -> dict[str, str]:
        return {"code": self.code, "location": self.location, "domain": self.domain, "severity": "error"}


class ValidationError(ValueError):
    """An error with a static code, never an input-derived message."""


@dataclass
class Section:
    level: int
    title: str
    start: int
    end: int
    content_start: int


@dataclass
class Article:
    name: str
    raw: bytes
    metadata: dict[str, Any]
    body: str
    visible: str
    sections: list[Section]
    location: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValidationError("json-duplicate-key")
        result[key] = value
    return result


def _constant(_: str) -> None:
    raise ValidationError("json-nonfinite-number")


def _finite_float(value: str) -> float:
    number = float(value)
    if not math.isfinite(number):
        raise ValidationError("json-nonfinite-number")
    return number


def strict_json_loads(text: str) -> Any:
    """Parse JSON without duplicate keys, NaN/Infinity, BOMs or unpaired surrogates."""
    try:
        text.encode("utf-8")
        value = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant, parse_float=_finite_float)
        for _, string in _strings(value):
            string.encode("utf-8")
        return value
    except ValidationError:
        raise
    except (ValueError, RecursionError, UnicodeError):
        raise ValidationError("json-malformed") from None


def normalize_excerpt(text: str) -> str:
    """Normalize CRLF only. Spaces, punctuation and paragraph breaks remain significant."""
    return text.replace("\r\n", "\n")


def scan_sensitive(text: str, location: str, deny_terms: Iterable[str] = ()) -> list[Issue]:
    """Conservative leak heuristics; reports categories/line numbers, never matched values."""
    found: list[tuple[int, str]] = []
    for code, pattern in SUSPICIOUS.items():
        found.extend((match.start(), "sensitive-" + code) for match in pattern.finditer(text))
    for match in re.finditer(r"(?<![\w.])(?:\d+\.){3,}\d+(?![\w.])", text):
        candidate = match.group()
        prefix = text[max(0, match.start() - 24):match.start()]
        if candidate.count(".") != 3 or re.search(r"(?i)(?:\bversion|\brevision|\boid)\s*[:=]?\s*$", prefix):
            continue
        try:
            ipaddress.IPv4Address(candidate)
            found.append((match.start(), "sensitive-ip-address"))
        except ValueError:
            pass
    for match in re.finditer(r"(?<![\w:])[0-9A-Fa-f:]*:[0-9A-Fa-f:.]+(?:%[A-Za-z0-9]+)?", text):
        try:
            ipaddress.IPv6Address(match.group())
            found.append((match.start(), "sensitive-ip-address"))
        except ValueError:
            pass
    folded = text.casefold()
    for term in deny_terms:
        if term:
            offset = folded.find(term.casefold())
            if offset >= 0:
                found.append((offset, "sensitive-deny-term"))
    newlines = [match.start() for match in re.finditer("\n", text)]
    return [
        Issue(code, f"{location}:line:{bisect_right(newlines, offset) + 1}")
        for offset, code in sorted(set(found))
    ]


def _strings(value: Any, location: str = "$") -> Iterable[tuple[str, str]]:
    if isinstance(value, str):
        yield location, value
    elif isinstance(value, dict):
        for index, (key, item) in enumerate(value.items()):
            yield f"{location}.key[{index}]", key
            yield from _strings(item, f"{location}.value[{index}]")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _strings(item, f"{location}[{index}]")


def _object(value: Any, fields: set[str], location: str, issues: list[Issue]) -> bool:
    if type(value) is not dict:
        issues.append(Issue("schema-object-required", location))
        return False
    if set(value) != fields:
        issues.append(Issue("schema-fields-mismatch", location))
        return False
    return True


def _text(value: Any, location: str, issues: list[Issue], limit: int = MAX_TEXT_CHARS) -> bool:
    if type(value) is not str or not value.strip() or len(value) > limit:
        issues.append(Issue("schema-text-invalid", location))
        return False
    if any(ord(char) < 32 and char not in "\r\n\t" for char in value) or "\r" in value.replace("\r\n", ""):
        issues.append(Issue("schema-control-character", location))
        return False
    try:
        value.encode("utf-8")
    except UnicodeError:
        issues.append(Issue("schema-text-invalid", location))
        return False
    return True


def _enum(value: Any, allowed: set[str], location: str, issues: list[Issue]) -> bool:
    if type(value) is not str or value not in allowed:
        issues.append(Issue("schema-enum-invalid", location))
        return False
    return True


def _list(value: Any, location: str, issues: list[Issue], maximum: int, nonempty: bool = True) -> bool:
    if type(value) is not list or len(value) > maximum or (nonempty and not value):
        issues.append(Issue("schema-list-invalid", location))
        return False
    return True


def _id_list(value: Any, location: str, issues: list[Issue], known: set[str]) -> bool:
    if not _list(value, location, issues, MAX_SOURCES):
        return False
    if any(type(item) is not str for item in value):
        issues.append(Issue("schema-source-ids-invalid", location))
        return False
    if len(set(value)) != len(value) or not set(value) <= known:
        issues.append(Issue("schema-source-ids-invalid", location))
        return False
    return True


def _safe_name(name: Any, suffix: str) -> bool:
    if type(name) is not str or not SAFE_NAME.fullmatch(name) or not name.endswith(suffix):
        return False
    stem = name.split(".", 1)[0].upper()
    return stem not in {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)), *(f"LPT{i}" for i in range(1, 10))}


def safe_https_url(value: str) -> bool:
    """Lexical public-URL policy only; never resolves DNS or fetches a resource."""
    if not isinstance(value, str) or not value.startswith("https://"):
        return False
    if re.search(r"[\s\\<>\"'`]", value) or any(ord(c) < 32 for c in value):
        return False
    try:
        parsed = urlsplit(value)
        host = parsed.hostname or ""
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port not in (None, 443):
            return False
        if "%" in parsed.netloc:
            return False
        if "?" in value.split("#", 1)[0]:
            selectors: set[str] = set()
            for selector in parsed.query.split("&"):
                match = re.fullmatch(r"(view|preserve-view|tabs)=([A-Za-z0-9._-]+)", selector)
                if not match or match[1] in selectors:
                    return False
                selectors.add(match[1])
        if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?", host) or "." not in host:
            return False
        if any(not label or len(label) > 63 or label.startswith("-") or label.endswith("-") for label in host.split(".")):
            return False
        if host.lower().endswith((
            ".local", ".internal", ".localhost", ".corp", ".msft.net",
            ".microsofticm.com", ".microsoftcrmapps.com", ".dynamics.com",
        )):
            return False
        if any(label in {"localhost", "intranet", "internal", "private"} for label in host.lower().split(".")):
            return False
        try:
            ipaddress.ip_address(host)
            return False
        except ValueError:
            pass
        decoded = unquote(value, errors="strict")
        if re.search(r"[\x00-\x20\\<>\"'`%]", decoded) or any(segment in {"cases", "incidents"} for segment in parsed.path.lower().split("/")):
            return False
        if scan_sensitive(decoded, "url"):
            return False
    except (ValueError, UnicodeError):
        return False
    return True


def validate_evidence(value: Any, issues: list[Issue]) -> tuple[dict[str, dict], dict[str, dict]]:
    """Validate schema v1; return source/article maps only when their records are valid."""
    sources: dict[str, dict] = {}
    articles: dict[str, dict] = {}
    if not _object(value, {"schema_version", "sources", "articles"}, "evidence:$", issues):
        return sources, articles
    if type(value["schema_version"]) is not int or value["schema_version"] != SCHEMA_VERSION:
        issues.append(Issue("schema-version-unsupported", "evidence:$.schema_version"))
    if _list(value["sources"], "evidence:$.sources", issues, MAX_SOURCES):
        for index, source in enumerate(value["sources"]):
            loc = f"evidence:$.sources[{index}]"
            before = len(issues)
            if not _object(source, SOURCE_FIELDS, loc, issues):
                continue
            for key in sorted(SOURCE_FIELDS):
                _text(source[key], f"{loc}.{key}", issues)
            if len(issues) != before:
                continue
            if not SOURCE_ID.fullmatch(source["id"]) or source["id"] in sources:
                issues.append(Issue("source-id-invalid-or-duplicate", loc + ".id"))
            _enum(source["kind"], {"public-document", "sanitized-evidence"}, loc + ".kind", issues)
            _enum(source["inspection_status"], {"original-inspected", "supplied-excerpt-only"}, loc + ".inspection_status", issues)
            _enum(source["excerpt_handling"], {"verbatim", "redacted"}, loc + ".excerpt_handling", issues)
            for key in SOURCE_FIELDS - {"text"}:
                if "\n" in source[key] or "\r" in source[key]:
                    issues.append(Issue("source-field-must-be-single-line", f"{loc}.{key}"))
            if source["kind"] == "public-document":
                if not safe_https_url(source["origin"]):
                    issues.append(Issue("public-origin-invalid", loc + ".origin"))
                if not re.fullmatch(r"(?:Section: .+|Anchor: #[A-Za-z][A-Za-z0-9_-]*|Page [1-9][0-9]*(?:, .+)?|Lines [1-9][0-9]*(?:-[1-9][0-9]*)?)", source["locator"]):
                    issues.append(Issue("public-locator-invalid", loc + ".locator"))
            elif source["kind"] == "sanitized-evidence":
                if not re.fullmatch(r"approved-evidence:[a-z][a-z0-9-]{2,63}", source["origin"]):
                    issues.append(Issue("sanitized-origin-invalid", loc + ".origin"))
                lines = len(normalize_excerpt(source["text"]).split("\n"))
                expected = "Lines 1" if lines == 1 else f"Lines 1-{lines}"
                if source["locator"] != expected:
                    issues.append(Issue("sanitized-locator-invalid", loc + ".locator"))
            if len(issues) == before:
                sources[source["id"]] = source
    if _list(value["articles"], "evidence:$.articles", issues, MAX_ARTICLES):
        used_names: set[str] = set()
        for index, article in enumerate(value["articles"]):
            loc = f"evidence:$.articles[{index}]"
            before = len(issues)
            if not _object(article, {"file", "claims", "enrichments"}, loc, issues):
                continue
            name = article["file"]
            if not _safe_name(name, ".md") or name.casefold() in used_names:
                issues.append(Issue("article-name-invalid-or-duplicate", loc + ".file"))
                continue
            used_names.add(name.casefold())
            claim_ids: set[str] = set()
            if _list(article["claims"], loc + ".claims", issues, MAX_CLAIMS):
                for ci, claim in enumerate(article["claims"]):
                    cloc = f"{loc}.claims[{ci}]"
                    if not _object(claim, {"id", "text", "source_ids", "basis"}, cloc, issues):
                        continue
                    cid = claim["id"]
                    if type(cid) is not str or not CLAIM_ID.fullmatch(cid) or cid in claim_ids:
                        issues.append(Issue("claim-id-invalid-or-duplicate", cloc + ".id"))
                    else:
                        claim_ids.add(cid)
                    _text(claim["text"], cloc + ".text", issues)
                    _id_list(claim["source_ids"], cloc + ".source_ids", issues, set(sources))
                    _enum(claim["basis"], {"observed", "reported", "documented", "inferred"}, cloc + ".basis", issues)
            if _list(article["enrichments"], loc + ".enrichments", issues, MAX_CLAIMS, False):
                seen: set[str] = set()
                for ei, enrichment in enumerate(article["enrichments"]):
                    eloc = f"{loc}.enrichments[{ei}]"
                    if not _object(enrichment, {"section", "source_ids", "change", "validation"}, eloc, issues):
                        continue
                    if _text(enrichment["section"], eloc + ".section", issues):
                        if enrichment["section"] in seen:
                            issues.append(Issue("enrichment-section-duplicate", eloc))
                        seen.add(enrichment["section"])
                    _text(enrichment["change"], eloc + ".change", issues)
                    _id_list(enrichment["source_ids"], eloc + ".source_ids", issues, set(sources))
                    _enum(enrichment["validation"], EXECUTION_VALIDATIONS, eloc + ".validation", issues)
            if len(issues) == before:
                articles[name] = article
    return sources, articles


def _mask_code(text: str) -> str:
    # Keep offsets and newlines intact, but code must not impersonate headings/citations.
    lines = text.splitlines(keepends=True)
    masked = []
    fence: tuple[str, int] | None = None
    for line in lines:
        start = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if fence:
            masked.append(re.sub(r"[^\n]", " ", line))
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(fence[1]) + r",}[ \t]*\n?", line):
                fence = None
        elif start:
            fence = (start[1][0], len(start[1]))
            masked.append(re.sub(r"[^\n]", " ", line))
        elif line.startswith(("    ", "\t")):
            masked.append(re.sub(r"[^\n]", " ", line))
        else:
            masked.append(line)
    visible = "".join(masked)
    return re.sub(r"(`+)([^\n]*?)\1", lambda match: " " * len(match[0]), visible)


def _sections(visible: str) -> list[Section]:
    matches = list(HEADING.finditer(visible))
    result = []
    for index, match in enumerate(matches):
        level = len(match[1])
        end = next((other.start() for other in matches[index + 1:] if len(other[1]) <= level), len(visible))
        result.append(Section(level, match[2], match.start(), end, match.end()))
    return result


def _frontmatter(text: str, loc: str, issues: list[Issue]) -> tuple[dict, str]:
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        issues.append(Issue("frontmatter-missing-or-invalid", loc))
        return {}, text
    metadata: dict[str, Any] = {}
    for line_index, line in enumerate(match[1].split("\n"), 2):
        entry = re.fullmatch(r"([a-z_]+):[ \t]*(.*)", line)
        location = f"{loc}:line:{line_index}"
        if not entry or entry[1] in metadata:
            issues.append(Issue("frontmatter-key-invalid-or-duplicate", location))
            continue
        key, value = entry.groups()
        try:
            if value.startswith('"') or key == "tags":
                value = strict_json_loads(value)
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1].replace("''", "'")
            elif any(char in value for char in "#{}[]&*!|>"):
                raise ValidationError("frontmatter-scalar-invalid")
        except ValidationError:
            issues.append(Issue("frontmatter-scalar-invalid", location))
            continue
        metadata[key] = value
    for key, values in METADATA_VALUES.items():
        if key not in metadata:
            issues.append(Issue("frontmatter-required-field", loc + ":metadata:" + key))
        else:
            _enum(metadata[key], values, loc + ":metadata:" + key, issues)
    kind = metadata.get("wiki_type")
    outcomes = OUTCOMES.get(kind, {}) if type(kind) is str else {}
    allowed = set(METADATA_VALUES) | {"title", "product", "tags"} | set(outcomes)
    if set(metadata) - allowed:
        issues.append(Issue("frontmatter-field-not-allowed", loc + ":metadata"))
    for key, values in outcomes.items():
        _enum(metadata.get(key), values, loc + ":metadata:" + key, issues)
    for key in ("title", "product"):
        if key in metadata:
            _text(metadata[key], loc + ":metadata:" + key, issues)
    if "tags" in metadata and (type(metadata["tags"]) is not list or any(type(tag) is not str or not tag for tag in metadata["tags"])):
        issues.append(Issue("frontmatter-tags-invalid", loc + ":metadata:tags"))
    if metadata.get("source_kind") == "current-session" and metadata.get("source_coverage") != "partial":
        issues.append(Issue("source-coverage-overclaimed", loc + ":metadata:source_coverage"))
    if metadata.get("source_coverage") == "complete-for-provided-transcript" and metadata.get("source_kind") != "provided-transcript":
        issues.append(Issue("source-coverage-kind-mismatch", loc + ":metadata:source_coverage"))
    if metadata.get("source_coverage") == "complete-for-selected-visible-events" and metadata.get("source_kind") != "local-session":
        issues.append(Issue("source-coverage-kind-mismatch", loc + ":metadata:source_coverage"))
    return metadata, text[match.end():]


def _fields(text: str) -> dict[str, list[str]]:
    matches = list(FIELD.finditer(text))
    result: dict[str, list[str]] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        value = text[match.start() + len("**" + match[1] + ":**"):end].strip("\n")
        result.setdefault(match[1], []).append(value.strip() if match[1] != "Original excerpt" else value)
    return result


def _one_field(fields: dict[str, list[str]], key: str) -> str | None:
    values = fields.get(key, [])
    return values[0] if len(values) == 1 else None


def _origin_value(value: str) -> str:
    match = re.fullmatch(r"\[[^\]\n]+\]\((https://[^()\s]+)\)", value)
    return match[1] if match else value


def _quote(value: str | None) -> str | None:
    if value is None:
        return None
    lines = value.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines or any(not re.match(r"^ {0,3}>", line) for line in lines):
        return None
    return "\n".join(re.sub(r"^ {0,3}> ?", "", line, count=1) for line in lines)


def _check_links(article: Article, approved: Path, declared: set[str], issues: list[Issue]) -> None:
    text = article.body
    loc = article.location
    # A deliberately narrow Markdown contract makes link checking fail closed.
    if re.search(r"\[[^\[\]\n]+\]:|!?\[[^\[\]\n]*\]\[[^\[\]\n]*\]", article.visible):
        issues.append(Issue("markdown-reference-links-not-supported", loc + ":body"))
    if re.search(r"<(?:!--|/?[A-Za-z][^>]*>)", article.visible):
        issues.append(Issue("markdown-html-or-autolink-not-supported", loc + ":body"))
    starts = list(re.finditer(r"!?\[[^\[\]\n]*\]\(", text))
    links = list(LINK.finditer(text))
    closing_labels = {m.start() for m in re.finditer(r"\]\(", text)}
    parsed_labels = {m.start() + m[0].index("](") for m in links}
    if {m.start() for m in starts} != {m.start() for m in links} or closing_labels != parsed_labels:
        issues.append(Issue("markdown-link-syntax-not-supported", loc + ":body"))
    anchors = set()
    for section in article.sections:
        anchor = re.sub(r"[^\w -]", "", section.title.lower()).replace(" ", "-")
        if anchor in anchors:
            issues.append(Issue("markdown-anchor-duplicate", loc + ":body"))
        anchors.add(anchor)
    for index, link in enumerate(links):
        dest = link[2]
        location = f"{loc}:link[{index}]"
        if link[0].startswith("!") or not dest or re.search(r"\s", dest):
            issues.append(Issue("markdown-link-syntax-not-supported", location))
            continue
        if dest.startswith("https://"):
            if not safe_https_url(dest):
                issues.append(Issue("external-url-invalid", location))
            continue
        if dest.startswith("#"):
            if dest[1:] not in anchors:
                issues.append(Issue("local-anchor-unresolved", location))
            continue
        try:
            decoded = unquote(dest, errors="strict")
            parsed = urlsplit(decoded)
        except (ValueError, UnicodeError):
            issues.append(Issue("local-link-invalid", location))
            continue
        if parsed.scheme or parsed.netloc or parsed.query or any(c in decoded for c in "\\/%") or ".." in parsed.path:
            issues.append(Issue("local-link-outside-approved-directory", location))
            continue
        if not parsed.path or parsed.path not in declared:
            issues.append(Issue("local-link-undeclared-target", location))
            continue
        try:
            target = approved / parsed.path
            if target.resolve(strict=True).parent != approved:
                issues.append(Issue("local-link-outside-approved-directory", location))
        except (OSError, RuntimeError, ValueError):
            issues.append(Issue("local-link-target-unavailable", location))


def _check_sources(article: Article, sources: dict[str, dict], evidence_name: str, issues: list[Issue]) -> set[str]:
    refs = next((s for s in article.sections if s.level == 2 and s.title == "References and original excerpts"), None)
    if not refs:
        return set()
    entries = [s for s in article.sections if s.level == 3 and refs.start < s.start < refs.end]
    ids: set[str] = set()
    mapping = {
        "Source type": "kind", "Title": "title", "Publisher or source role": "publisher",
        "Origin": "origin", "Exact location": "locator", "Version or revision": "version",
        "Verification": "inspection_status", "Excerpt handling": "excerpt_handling",
    }
    for index, entry in enumerate(entries):
        loc = f"{article.location}:source[{index}]"
        sid = entry.title
        if not SOURCE_ID.fullmatch(sid) or sid in ids or sid not in sources:
            issues.append(Issue("source-entry-unresolved-or-duplicate", loc))
            continue
        ids.add(sid)
        fields = _fields(article.body[entry.content_start:entry.end])
        if set(fields) != set(SOURCE_MARKDOWN_FIELDS) or any(len(v) != 1 or not v[0].strip() for v in fields.values()):
            issues.append(Issue("source-entry-fields-invalid", loc))
            continue
        if list(fields) != SOURCE_MARKDOWN_FIELDS:
            issues.append(Issue("source-entry-field-order", loc))
        source = sources[sid]
        for label, key in mapping.items():
            value = _one_field(fields, label)
            if label == "Origin":
                value = _origin_value(value or "")
            if value != source[key]:
                issues.append(Issue("source-entry-evidence-mismatch", loc + ":" + key))
        expected = f"{sid} in [{evidence_name}]({evidence_name})"
        if _one_field(fields, "Evidence record") != expected:
            issues.append(Issue("source-entry-evidence-link-mismatch", loc))
        excerpt = _quote(_one_field(fields, "Original excerpt"))
        if excerpt is None:
            issues.append(Issue("source-excerpt-format-invalid", loc))
        elif excerpt != normalize_excerpt(source["text"]):
            issues.append(Issue("source-excerpt-mismatch", loc))
        access = _one_field(fields, "Access")
        allowed_access = {"Public"} if source["kind"] == "public-document" else {"engineer-provided", "approved restricted documentation"}
        if access not in allowed_access:
            issues.append(Issue("source-access-invalid", loc))
        inspected = _one_field(fields, "Inspected on") or ""
        try:
            valid_date = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", inspected)) and bool(date.fromisoformat(inspected))
        except ValueError:
            valid_date = False
        if not valid_date and not (inspected == "Not independently inspected" and source["inspection_status"] == "supplied-excerpt-only"):
            issues.append(Issue("source-inspection-date-invalid", loc))
    body_citations = list(CITATION.finditer(article.visible[:refs.start]))
    cited = {m[1] for m in body_citations}
    for citation in CITATION.finditer(article.visible):
        if citation[1].lower() != citation[2] or citation[1] not in ids:
            issues.append(Issue("citation-unresolved-or-mismatched", article.location + ":body"))
    for link in LINK.finditer(article.visible):
        if re.fullmatch(r"S[0-9]+", link[1]) and not CITATION.fullmatch(link[0]):
            issues.append(Issue("citation-format-invalid", article.location + ":body"))
    if ids != cited:
        issues.append(Issue("source-entry-unused-or-missing", article.location + ":references"))
    return cited


def _direct_content(article: Article, section: Section) -> str:
    end = next((s.start for s in article.sections if section.start < s.start < section.end and s.level > section.level), section.end)
    return article.visible[section.content_start:end]


def _check_claims_and_enrichments(article: Article, record: dict, sources: dict[str, dict], issues: list[Issue]) -> set[str]:
    loc = article.location
    refs = next((s for s in article.sections if s.level == 2 and s.title == "References and original excerpts"), None)
    end = refs.start if refs else len(article.body)
    body = article.body[:end]
    visible = article.visible[:end]
    citations = list(CITATION.finditer(visible))
    selected_ids: set[str] = set()
    claim_positions: list[tuple[int, int, set[str]]] = []
    for index, claim in enumerate(record["claims"]):
        cloc = f"{loc}:claim[{index}]"
        selected_ids.update(claim["source_ids"])
        positions = [m.start() for m in islice(re.finditer(re.escape(normalize_excerpt(claim["text"])), body), MAX_CLAIM_OCCURRENCES + 1)]
        if len(positions) > MAX_CLAIM_OCCURRENCES:
            issues.append(Issue("claim-occurrence-limit-exceeded", cloc))
            continue
        if not positions:
            issues.append(Issue("claim-text-absent", cloc))
            continue
        matched = False
        for start in positions:
            finish = start + len(normalize_excerpt(claim["text"]))
            # Nearest heading boundary, not the whole article, is the citation neighborhood.
            lower = max((s.content_start for s in article.sections if s.content_start <= start), default=0)
            upper = min((s.start for s in article.sections if s.start >= finish), default=end)
            nearby = {m[1] for m in citations if lower <= m.start() < upper and min(abs(m.start() - finish), abs(start - m.end())) <= 1200}
            if set(claim["source_ids"]) <= nearby:
                matched = True
                claim_positions.append((start, finish, set(claim["source_ids"])))
        if not matched:
            issues.append(Issue("claim-nearby-citation-missing", cloc))
        if claim["basis"] in {"observed", "reported"} and not any(sources[sid]["kind"] == "sanitized-evidence" for sid in claim["source_ids"]):
            issues.append(Issue("claim-observation-needs-sanitized-evidence", cloc))
    if selected_ids != {m[1] for m in citations}:
        issues.append(Issue("claim-citation-coverage-mismatch", loc + ":claims"))
    kind = article.metadata["wiki_type"]
    container_name = {"qa": "Questions and answers", "how-to": "Step-by-step procedure", "break-fix": "Resolution or workaround"}[kind]
    container = next((s for s in article.sections if s.level == 2 and s.title == container_name), None)
    blocks = [s for s in article.sections if s.level == 3 and container and container.start < s.start < container.end]
    if any(s.start < end and s not in blocks and re.match(r"Step [0-9]+", s.title) for s in article.sections):
        issues.append(Issue("step-heading-outside-procedure", loc + ":body"))
    if not blocks:
        issues.append(Issue("answer-or-step-blocks-missing", loc + ":body"))
    required_fields = {
        "qa": {"Answer", "Conditions and exceptions", "Sources"},
        "how-to": {"Where", "Inputs", "Action", "Why", "Expected result", "If the result differs", "Safety and rollback", "Sources"},
        "break-fix": {"Prerequisites and impact", "Action", "Expected result", "If it fails", "Rollback", "Sources"},
    }[kind]
    for index, block in enumerate(blocks, 1):
        bloc = f"{loc}:block[{index - 1}]"
        pattern = rf"Q{index}\. .+" if kind == "qa" else rf"Step {index} - .+"
        if not re.fullmatch(pattern, block.title):
            issues.append(Issue("answer-or-step-heading-invalid", bloc))
        text = article.visible[block.content_start:block.end]
        fields = _fields(article.body[block.content_start:block.end])
        if any(not _one_field(fields, key) for key in required_fields):
            issues.append(Issue("answer-or-step-fields-missing", bloc))
        block_ids = {m[1] for m in CITATION.finditer(text)}
        mapped = set().union(*(ids for start, finish, ids in claim_positions if block.content_start <= start < finish <= block.end))
        if not block_ids or not mapped or not block_ids <= mapped:
            issues.append(Issue("answer-or-step-claim-citation-missing", bloc))
    enrichments = {item["section"]: item for item in record["enrichments"]}
    sections = [s for s in article.sections if s.level >= 2 and s.start < end]
    titles = [s.title for s in sections]
    for index, item in enumerate(record["enrichments"]):
        if titles.count(item["section"]) != 1:
            issues.append(Issue("enrichment-heading-unresolved", f"{loc}:enrichment[{index}]"))
    extraction = article.metadata["content_mode"] == "extraction-only"
    if extraction and enrichments:
        issues.append(Issue("extraction-only-enrichments-prohibited", loc + ":enrichments"))
    for index, section in enumerate(sections):
        fields = _fields(_direct_content(article, section))
        provenance = _one_field(fields, "Provenance")
        validation = _one_field(fields, "Execution validation")
        is_step = kind != "qa" and section in blocks
        is_enriched = section.title in enrichments
        sloc = f"{loc}:section[{index}]"
        if is_step or provenance is not None or validation is not None or is_enriched:
            if provenance not in PROVENANCES or validation not in EXECUTION_VALIDATIONS:
                issues.append(Issue("provenance-or-execution-label-missing-or-invalid", sloc))
                continue
            if extraction and provenance != "observed-in-session":
                issues.append(Issue("extraction-only-new-step-prohibited", sloc))
            if (provenance != "observed-in-session") != is_enriched:
                issues.append(Issue("enrichment-label-manifest-mismatch", sloc))
            if is_enriched:
                enrichment = enrichments[section.title]
                section_ids = {m[1] for m in CITATION.finditer(_direct_content(article, section))}
                if validation != enrichment["validation"] or not set(enrichment["source_ids"]) <= section_ids:
                    issues.append(Issue("enrichment-validation-or-citations-mismatch", sloc))
            if extraction and is_step:
                observations = [claim for claim in record["claims"] if claim["basis"] in {"observed", "reported"} and normalize_excerpt(claim["text"]) in article.body[section.content_start:section.end]]
                if not observations:
                    issues.append(Issue("extraction-only-step-needs-observed-or-reported-claim", sloc))
    return selected_ids


def _check_review(value: Any, evidence_raw: bytes, articles: list[Article], records: dict[str, dict], issues: list[Issue]) -> str:
    review_issues: list[Issue] = []
    loc = "review:$"
    if not _object(value, {"schema_version", "reviewer_kind", "evidence_sha256", "articles"}, loc, review_issues):
        issues.extend(Issue(i.code, i.location, "semantic") for i in review_issues)
        return "rejected"
    if type(value["schema_version"]) is not int or value["schema_version"] != 1:
        review_issues.append(Issue("schema-version-unsupported", loc + ".schema_version"))
    _enum(value["reviewer_kind"], {"human", "separate-agent"}, loc + ".reviewer_kind", review_issues)
    if value["evidence_sha256"] != sha256_bytes(evidence_raw):
        review_issues.append(Issue("review-evidence-hash-mismatch", loc + ".evidence_sha256"))
    known = {article.name: article for article in articles}
    seen: set[str] = set()
    verdicts: list[str] = []
    if _list(value["articles"], loc + ".articles", review_issues, MAX_ARTICLES):
        for index, record in enumerate(value["articles"]):
            rloc = f"review:$.articles[{index}]"
            if not _object(record, {"file", "sha256", "coverage", "claims"}, rloc, review_issues):
                continue
            name = record["file"]
            if type(name) is not str or name not in known or name in seen:
                review_issues.append(Issue("review-article-unresolved-or-duplicate", rloc))
                continue
            seen.add(name)
            if record["sha256"] != sha256_bytes(known[name].raw):
                review_issues.append(Issue("review-article-hash-mismatch", rloc + ".sha256"))
            _enum(record["coverage"], {"all-substantive-claims-reviewed"}, rloc + ".coverage", review_issues)
            expected = {claim["id"] for claim in records[name]["claims"]}
            reviewed: set[str] = set()
            if _list(record["claims"], rloc + ".claims", review_issues, MAX_CLAIMS):
                for ci, claim in enumerate(record["claims"]):
                    cloc = f"{rloc}.claims[{ci}]"
                    if not _object(claim, {"id", "verdict", "reason"}, cloc, review_issues):
                        continue
                    cid = claim["id"]
                    if type(cid) is not str or cid not in expected or cid in reviewed:
                        review_issues.append(Issue("review-claim-unresolved-or-duplicate", cloc))
                    else:
                        reviewed.add(cid)
                    _text(claim["reason"], cloc + ".reason", review_issues)
                    if _enum(claim["verdict"], {"supported", "qualified", "unsupported"}, cloc + ".verdict", review_issues):
                        verdicts.append(claim["verdict"])
                        if claim["verdict"] == "unsupported":
                            review_issues.append(Issue("review-claim-unsupported", cloc))
            if reviewed != expected:
                review_issues.append(Issue("review-claim-coverage-incomplete", rloc))
    if seen != set(known):
        review_issues.append(Issue("review-article-coverage-incomplete", loc))
    issues.extend(Issue(i.code, i.location, "semantic") for i in review_issues)
    if review_issues:
        return "rejected"
    return "reported-qualified" if "qualified" in verdicts else "reported-supported"


def _result(issues: list[Issue], semantic: str = "pending", hashes: dict | None = None) -> dict:
    unique = sorted({(i.domain, i.location, i.code) for i in issues})
    return {
        "schema_version": 1,
        "status": "failed" if issues else "passed",
        "mechanical_status": "failed" if any(i.domain == "mechanical" for i in issues) else "passed",
        "semantic_review": semantic,
        "publication_status": "not-authorized",
        "issues": [Issue(code, location, domain).as_dict() for domain, location, code in unique],
        "hashes": hashes or {},
        "limitations": LIMITATIONS.copy(),
    }


def _read_declared(path: Path, loc: str, approved: Path, issues: list[Issue]) -> tuple[bytes, str] | None:
    try:
        resolved = path.resolve(strict=True)
        if resolved.parent != approved or not resolved.is_file():
            issues.append(Issue("file-outside-approved-directory-or-not-regular", loc))
            return None
        if resolved.stat().st_size > MAX_FILE_BYTES:
            issues.append(Issue("file-too-large", loc))
            return None
        with resolved.open("rb") as stream:
            raw = stream.read(MAX_FILE_BYTES + 1)
        if len(raw) > MAX_FILE_BYTES:
            issues.append(Issue("file-too-large", loc))
            return None
        if not raw:
            issues.append(Issue("file-empty", loc))
            return None
        text = raw.decode("utf-8")
        if text.startswith("\ufeff") or "\x00" in text or "\r" in text.replace("\r\n", ""):
            issues.append(Issue("file-encoding-invalid", loc))
            return None
        return raw, text
    except FileNotFoundError:
        issues.append(Issue("file-missing", loc))
    except UnicodeError:
        issues.append(Issue("file-encoding-invalid", loc))
    except (OSError, RuntimeError, ValueError):
        issues.append(Issue("file-unreadable", loc))
    return None


def validate_bundle(
    article_paths: Iterable[str | Path],
    evidence_path: str | Path,
    *,
    deny_terms: Iterable[str] = (),
    review_path: str | Path | None = None,
    require_semantic_review: bool = False,
) -> dict:
    """Validate only declared files, without writes/network. Absolute paths are mandatory."""
    issues: list[Issue] = []
    try:
        if isinstance(deny_terms, str):
            raise TypeError
        terms = tuple(deny_terms)
    except TypeError:
        return _result([Issue("argument-invalid", "arguments:deny_terms")])
    if any(type(term) is not str or not term.strip() for term in terms) or type(require_semantic_review) is not bool:
        return _result([Issue("argument-invalid", "arguments")])
    try:
        if isinstance(article_paths, (str, Path)):
            raise ValueError
        paths = [Path(path) for path in article_paths]
        evidence = Path(evidence_path)
        review = Path(review_path) if review_path is not None else None
    except (TypeError, ValueError):
        return _result([Issue("argument-invalid", "arguments")])
    if not paths or len(paths) > MAX_ARTICLES:
        return _result([Issue("article-count-invalid", "arguments:articles")])
    declared_paths = [(p, f"article[{i}]", ".md") for i, p in enumerate(paths)]
    declared_paths += [(evidence, "evidence", ".json")]
    if review is not None:
        declared_paths.append((review, "review", ".json"))
    try:
        approved = evidence.parent.resolve(strict=True)
    except (OSError, RuntimeError, ValueError):
        return _result([Issue("approved-directory-unavailable", "evidence:directory")])
    names: set[str] = set()
    resolved_names: set[str] = set()
    for path, loc, suffix in declared_paths:
        if not path.is_absolute() or ".." in path.parts or not _safe_name(path.name, suffix):
            issues.append(Issue("file-path-invalid", loc))
            continue
        if path.name.casefold() in names:
            issues.append(Issue("file-name-collision", loc))
        names.add(path.name.casefold())
        issues.extend(scan_sensitive(path.name, loc + ":filename", terms))
        try:
            if path.parent.resolve(strict=True) != approved:
                issues.append(Issue("file-directory-mismatch", loc))
            resolved = str(path.resolve()).casefold()
            if resolved in resolved_names:
                issues.append(Issue("file-target-collision", loc))
            resolved_names.add(resolved)
        except (OSError, RuntimeError, ValueError):
            issues.append(Issue("file-unreadable", loc))
    if issues:
        return _result(issues)
    loaded: dict[str, tuple[bytes, str]] = {}
    for path, loc, _ in declared_paths:
        content = _read_declared(path, loc, approved, issues)
        if content:
            loaded[loc] = content
            issues.extend(scan_sensitive(content[1], loc, terms))
    if len(loaded) != len(declared_paths):
        return _result(issues)
    hashes = {
        "evidence_sha256": sha256_bytes(loaded["evidence"][0]),
        "articles": [{"index": i, "sha256": sha256_bytes(loaded[f"article[{i}]"][0])} for i in range(len(paths))],
    }
    json_values = {}
    for name in ("evidence", "review"):
        if name not in loaded:
            continue
        try:
            json_values[name] = strict_json_loads(loaded[name][1])
            for location, value in _strings(json_values[name]):
                issues.extend(scan_sensitive(value, f"{name}:{location}", terms))
        except (ValidationError, RecursionError) as error:
            code = str(error) if isinstance(error, ValidationError) else "json-too-deep"
            issues.append(Issue(code, name))
    if "evidence" not in json_values:
        return _result(issues, hashes=hashes)
    schema_issues: list[Issue] = []
    sources, records = validate_evidence(json_values["evidence"], schema_issues)
    issues.extend(schema_issues)
    if schema_issues:
        return _result(issues, hashes=hashes)
    if set(records) != {path.name for path in paths}:
        issues.append(Issue("declared-article-manifest-mismatch", "evidence:$.articles"))
        return _result(issues, hashes=hashes)
    articles = []
    selected: set[str] = set()
    any_complete = False
    for index, path in enumerate(paths):
        loc = f"article[{index}]"
        raw, text = loaded[loc]
        before = len(issues)
        metadata, body = _frontmatter(normalize_excerpt(text), loc, issues)
        if len(issues) != before:
            continue
        for location, value in _strings(metadata):
            issues.extend(scan_sensitive(value, f"{loc}:metadata:{location}", terms))
        any_complete |= metadata["reference_status"] == "complete"
        visible = _mask_code(body)
        if sum(1 for _ in HEADING.finditer(visible)) > MAX_HEADINGS or sum(1 for _ in CITATION.finditer(visible)) > MAX_CITATIONS:
            issues.append(Issue("article-structure-limit-exceeded", loc + ":body"))
            continue
        article = Article(path.name, raw, metadata, body, visible, _sections(visible), loc)
        articles.append(article)
        if [s.title for s in article.sections if s.level == 2] != HEADINGS[metadata["wiki_type"]]:
            issues.append(Issue("article-headings-mismatch", loc + ":body"))
        if len([s for s in article.sections if s.level == 1]) != 1:
            issues.append(Issue("article-title-heading-invalid", loc + ":body"))
        _check_links(article, approved, {p.name for p, _, _ in declared_paths}, issues)
        _check_sources(article, sources, evidence.name, issues)
        selected.update(_check_claims_and_enrichments(article, records[path.name], sources, issues))
    if selected != set(sources):
        issues.append(Issue("evidence-source-unused-in-bundle", "evidence:$.sources"))
    semantic = "pending"
    if "review" in json_values and len(articles) == len(paths):
        semantic = _check_review(json_values["review"], loaded["evidence"][0], articles, records, issues)
    elif review is not None:
        semantic = "rejected"
    if (require_semantic_review or any_complete) and semantic not in {"reported-supported", "reported-qualified"}:
        issues.append(Issue("semantic-review-required", "review", "semantic"))
    return _result(issues, semantic, hashes)


class _ArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise ValidationError("cli-arguments-invalid")


def main(argv: list[str] | None = None) -> int:
    parser = _ArgumentParser(description=__doc__)
    parser.add_argument("--article", action="append", required=True, help="Absolute approved article path; repeat for each article.")
    parser.add_argument("--evidence", required=True, help="Absolute approved evidence JSON path.")
    parser.add_argument("--deny-term", action="append", default=[], help="Case-insensitive reader-specific deny term; matches are never printed.")
    parser.add_argument("--review", help="Absolute separate reviewer attestation JSON path.")
    parser.add_argument("--require-semantic-review", action="store_true")
    try:
        args = parser.parse_args(argv)
        result = validate_bundle(args.article, args.evidence, deny_terms=args.deny_term, review_path=args.review, require_semantic_review=args.require_semantic_review)
    except ValidationError:
        result = _result([Issue("cli-arguments-invalid", "arguments")])
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    sys.exit(main())
