#!/usr/bin/env python3
"""Generate format annotations from Markdown and finalize a Feishu docx note in place."""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
import time
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib import error, parse, request


BASE_URL = "https://open.feishu.cn/open-apis"
DEFAULT_TIMEOUT = 30
DEFAULT_LABEL_COLOR = 5  # Blue
DEFAULT_WARNING_COLOR = 4  # Yellow
DEFAULT_CRITICAL_COLOR = 2  # Red
DEFAULT_QUOTE_COLOR = 7  # Gray
DEFAULT_BATCH_SIZE = 200
DEFAULT_FINALIZE_ROUNDS = 2
AUDIT_AUTO_FIX_TRUE = "是"
AUDIT_AUTO_FIX_FALSE = "否"
AUDIT_FIELDS = ["位置", "期望动作", "当前飞书状态", "问题类型", "严重等级", "证据", "修复建议", "可否自动修复"]
FORMAT_FIELDS = ["位置", "原文片段", "建议动作", "强度等级", "作用说明", "Feishu 落地样式"]
FORMAT_LOCATION_FIELD = FORMAT_FIELDS[0]
FORMAT_EXCERPT_FIELD = FORMAT_FIELDS[1]
FORMAT_ACTION_FIELD = FORMAT_FIELDS[2]
FORMAT_INTENSITY_FIELD = FORMAT_FIELDS[3]
AUDIT_LOCATION_FIELD = AUDIT_FIELDS[0]
AUDIT_AUTO_FIX_FIELD = AUDIT_FIELDS[-1]
ALLOWED_ACTIONS = {
    "bold",
    "italic",
    "inline_code",
    "bullet_list",
    "numbered_list",
    "quote_block",
    "table_candidate",
    "highlight_color",
    "tighten_spacing",
    "preserve_spacing",
}
EMPHASIS_ACTIONS = {"bold", "italic", "inline_code", "highlight_color"}
LIST_ACTIONS = {"bullet_list", "numbered_list", "quote_block"}
LIST_FIELD_NAMES = {"bullet_list": "bullet", "numbered_list": "ordered", "quote_block": "quote"}
EDITABLE_BLOCK_TYPES = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 17}
TEXTISH_BLOCK_TYPES = {2, 12, 13, 14, 15, 17}
LABEL_EMPHASIS_BLOCK_TYPES = {2, 12, 13, 15, 17}
SAFE_ELEMENT_TYPES = {"text_run", "equation", "mention_user", "mention_doc", "reminder"}
META_KEYS = {"block_id", "parent_id", "children", "block_type"}
TABLE_BLOCK_TYPES = {31}
TABLE_CELL_BLOCK_TYPES = {32}
QUOTE_CONTAINER_BLOCK_TYPES = {34}
HEADING_BLOCK_TYPES = {3, 4, 5, 6, 7, 8, 9, 10, 11}
LEADING_LABELS = [
    "核心目标",
    "核心问题",
    "核心结论",
    "关键结论",
    "关键观察",
    "核心创新",
    "核心思路",
    "主要结论",
    "主要判断",
    "方法创新",
    "研究动机",
    "研究背景",
    "直观理解",
    "公式含义",
    "变量释义",
    "变量定义",
    "定义",
    "解释",
    "说明",
    "注意",
    "结论",
    "原因",
    "问题",
    "方法",
    "结果",
    "输入",
    "输出",
    "实验设置",
    "实验协议",
    "对比对象",
    "术语关系",
    "复杂度分析",
    "任务适配",
    "目标函数",
    "优化目标",
    "启发",
    "局限",
    "改进",
    "总结",
    "项目代码",
]
LEADING_LABEL_PATTERN = re.compile(
    r"^(?P<prefix>•\s+)?(?P<label>("
    + "|".join(re.escape(label) for label in sorted(LEADING_LABELS, key=len, reverse=True))
    + r")\s*[：:])"
)
INLINE_MARKDOWN_PATTERN = re.compile(r"(`[^`\n]+`|\*\*[^*\n]+\*\*)")
INLINE_FORMULA_PATTERN = re.compile(r"(?<!\$)\$(?P<expr>[^$\n]{1,120}?)(?<!\\)\$(?!\$)")
DISPLAY_FORMULA_PATTERNS = (
    re.compile(r"^\s*\$\$(?P<expr>[\s\S]+?)\$\$\s*$"),
    re.compile(r"^\s*\\\[(?P<expr>[\s\S]+?)\\\]\s*$"),
)
HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(?P<title>.+?)\s*$")
BULLET_PATTERN = re.compile(r"^\s*[-*]\s+(?P<body>.+?)\s*$")
ORDERED_PATTERN = re.compile(r"^\s*(?P<num>\d+)\.\s+(?P<body>.+?)\s*$")
QUOTE_PATTERN = re.compile(r"^\s*>\s+(?P<body>.+?)\s*$")
PIPE_TABLE_PATTERN = re.compile(r"^\|.*\|\s*$")
BOLD_PATTERN = re.compile(r"\*\*(?P<text>[^*\n][^*\n]*?)\*\*")
CODE_PATTERN = re.compile(r"`(?P<text>[^`\n]+?)`")
ITALIC_PATTERN = re.compile(r"(?<!\*)\*(?P<text>[^*\n][^*\n]*?)\*(?!\*)")
HIGHLIGHT_LABEL_PATTERN = re.compile(r"^(?P<label>(核心结论|主要判断|可借鉴点|局限与改进|全文概括|结论|注意|说明))[：:]")
MARKDOWN_LINK_PATTERN = re.compile(r"\[(?P<label>[^\]\n]+)\]\((?P<url>[^)\n]+)\)")
TABLE_SEPARATOR_PATTERN = re.compile(r"^:?-{3,}:?$")
RED_HIGHLIGHT_KEYWORDS = (
    "纠偏",
    "核心结论",
    "主要判断",
    "关键判断",
    "最能支撑",
    "真正要解决",
    "不是新传播算子",
    "不是新算子",
    "不是在发明",
)
YELLOW_HIGHLIGHT_KEYWORDS = (
    "边界",
    "局限",
    "注意",
    "反例",
    "限制",
    "适用",
    "不能",
    "不等于",
    "误区",
    "风险",
)
BLOCK_TYPE_NAMES = {
    1: "page",
    2: "text",
    3: "heading1",
    4: "heading2",
    5: "heading3",
    6: "heading4",
    7: "heading5",
    8: "heading6",
    9: "heading7",
    10: "heading8",
    11: "heading9",
    12: "bullet",
    13: "ordered",
    14: "code",
    15: "quote",
    17: "todo",
    31: "table",
    32: "table_cell",
    34: "quote_container",
}


class FeishuAPIError(RuntimeError):
    """Raised when a Feishu OpenAPI request fails."""


@dataclass
class AnnotationEntry:
    位置: str
    原文片段: str
    建议动作: str
    强度等级: str
    作用说明: str
    Feishu落地样式: str

    def as_dict(self) -> dict[str, str]:
        return {
            "位置": self.位置,
            "原文片段": self.原文片段,
            "建议动作": self.建议动作,
            "强度等级": self.强度等级,
            "作用说明": self.作用说明,
            "Feishu 落地样式": self.Feishu落地样式,
        }


@dataclass
class AuditIssue:
    位置: str
    期望动作: str
    当前飞书状态: str
    问题类型: str
    严重等级: str
    证据: str
    修复建议: str
    可否自动修复: str

    def as_dict(self) -> dict[str, str]:
        return {
            "位置": self.位置,
            "期望动作": self.期望动作,
            "当前飞书状态": self.当前飞书状态,
            "问题类型": self.问题类型,
            "严重等级": self.严重等级,
            "证据": self.证据,
            "修复建议": self.修复建议,
            "可否自动修复": self.可否自动修复,
        }


@dataclass
class NoteTableSpec:
    location: str
    line_no: int
    headings: list[str]
    rows: list[list[str]]
    source_lines: list[str]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    @property
    def column_count(self) -> int:
        return max((len(row) for row in self.rows), default=0)


@dataclass
class Proposal:
    proposal_type: str
    block_id: str | None
    block_type: int | None
    actions: list[str]
    before: str
    after: str
    request: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None


@dataclass
class BlockState:
    block_id: str
    block_type: int
    block_name: str
    original_elements: list[dict[str, Any]]
    updated_elements: list[dict[str, Any]]
    actions: list[str]


class FeishuDocxClient:
    def __init__(self, app_id: str, app_secret: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.app_id = app_id
        self.app_secret = app_secret
        self.timeout = timeout

    def get_tenant_access_token(self) -> str:
        response = self._request(
            "POST",
            "/auth/v3/tenant_access_token/internal",
            body={"app_id": self.app_id, "app_secret": self.app_secret},
        )
        token = response.get("tenant_access_token")
        if not token:
            raise FeishuAPIError("Feishu auth response did not include tenant_access_token.")
        return token

    def get_raw_content(self, document_id: str, access_token: str) -> str:
        response = self._request(
            "GET",
            f"/docx/v1/documents/{document_id}/raw_content",
            query={"lang": 0},
            access_token=access_token,
        )
        if "data" in response:
            return response["data"].get("content", "")
        return response.get("content", "")

    def list_blocks(self, document_id: str, access_token: str) -> list[dict[str, Any]]:
        items: list[dict[str, Any]] = []
        page_token: str | None = None
        while True:
            query: dict[str, Any] = {"page_size": 500, "document_revision_id": -1}
            if page_token:
                query["page_token"] = page_token
            response = self._request(
                "GET",
                f"/docx/v1/documents/{document_id}/blocks",
                query=query,
                access_token=access_token,
            )
            data = response.get("data", response)
            items.extend(data.get("items", []))
            if not data.get("has_more"):
                break
            page_token = data.get("page_token")
            if not page_token:
                break
        return items

    def batch_update_blocks(
        self,
        document_id: str,
        access_token: str,
        requests_payload: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return self._request(
            "PATCH",
            f"/docx/v1/documents/{document_id}/blocks/batch_update",
            query={"document_revision_id": -1, "client_token": str(uuid.uuid4())},
            body={"requests": requests_payload},
            access_token=access_token,
        )

    def batch_delete_children(
        self,
        document_id: str,
        parent_id: str,
        access_token: str,
        start_index: int,
        end_index: int,
    ) -> dict[str, Any]:
        return self._request(
            "DELETE",
            f"/docx/v1/documents/{document_id}/blocks/{parent_id}/children/batch_delete",
            query={"document_revision_id": -1},
            body={"start_index": start_index, "end_index": end_index},
            access_token=access_token,
        )

    def create_child_blocks(
        self,
        document_id: str,
        parent_id: str,
        access_token: str,
        children_payload: list[dict[str, Any]],
        index: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"children": children_payload}
        if index is not None:
            body["index"] = index
        return self._request(
            "POST",
            f"/docx/v1/documents/{document_id}/blocks/{parent_id}/children",
            query={"document_revision_id": -1},
            body=body,
            access_token=access_token,
        )

    def create_descendant_blocks(
        self,
        document_id: str,
        parent_id: str,
        access_token: str,
        children_id: list[str],
        descendants: list[dict[str, Any]],
        index: int | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"children_id": children_id, "descendants": descendants}
        if index is not None:
            body["index"] = index
        return self._request(
            "POST",
            f"/docx/v1/documents/{document_id}/blocks/{parent_id}/descendant",
            query={"document_revision_id": -1, "client_token": str(uuid.uuid4())},
            body=body,
            access_token=access_token,
        )

    def _request(
        self,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        access_token: str | None = None,
        retries: int = 3,
    ) -> dict[str, Any]:
        url = BASE_URL + path
        if query:
            url += "?" + parse.urlencode(query)
        headers = {}
        payload = None
        if access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        if body is not None:
            headers["Content-Type"] = "application/json; charset=utf-8"
            payload = json.dumps(body, ensure_ascii=False).encode("utf-8")

        attempt = 0
        while True:
            req = request.Request(url=url, data=payload, headers=headers, method=method)
            try:
                with request.urlopen(req, timeout=self.timeout) as resp:
                    raw = resp.read().decode("utf-8")
            except error.HTTPError as exc:
                raw = exc.read().decode("utf-8", errors="replace")
                retriable = exc.code in {429, 500, 503}
                if retriable and attempt < retries:
                    self._sleep_with_backoff(attempt)
                    attempt += 1
                    continue
                raise FeishuAPIError(
                    f"HTTP {exc.code} for {method} {path}: {raw or exc.reason}"
                ) from exc
            except error.URLError as exc:
                if attempt < retries:
                    self._sleep_with_backoff(attempt)
                    attempt += 1
                    continue
                raise FeishuAPIError(f"Network error for {method} {path}: {exc}") from exc

            try:
                data = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise FeishuAPIError(f"Invalid JSON response for {method} {path}: {raw}") from exc

            code = data.get("code", 0)
            if code == 0:
                return data

            retriable_code = code in {99991400}
            if retriable_code and attempt < retries:
                self._sleep_with_backoff(attempt)
                attempt += 1
                continue
            raise FeishuAPIError(
                f"Feishu API error for {method} {path}: code={code}, msg={data.get('msg', '')}"
            )

    @staticmethod
    def _sleep_with_backoff(attempt: int) -> None:
        time.sleep(min(2.0, 0.5 * (2**attempt)))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate annotation artifacts and preview/apply Feishu docx finalization."
    )
    parser.add_argument(
        "--mode",
        choices=("annotate", "preview", "apply", "audit", "finalize"),
        default="preview",
        help="annotate only writes .format-annotations.*; preview/apply/audit/finalize also analyze a Feishu doc.",
    )
    parser.add_argument("--note-file", help="Local Markdown note used to generate annotation artifacts.")
    parser.add_argument("--annotations-json", help="Existing .format-annotations.json path.")
    parser.add_argument("--annotations-md", help="Optional output path for .format-annotations.md.")
    parser.add_argument("--doc-url", help="Feishu docx URL.")
    parser.add_argument("--doc-token", help="Feishu docx token/document_id.")
    parser.add_argument(
        "--blocks-json",
        help="Offline preview using a saved blocks.json backup instead of calling Feishu.",
    )
    parser.add_argument(
        "--raw-content-file",
        help="Optional raw_content.txt file paired with --blocks-json for richer backups.",
    )
    parser.add_argument(
        "--backup-dir",
        help="Directory for apply-mode backups. Default: <skill>/backups",
    )
    parser.add_argument(
        "--report-file",
        help="Optional JSON report output path for preview/apply analysis.",
    )
    parser.add_argument("--audit-md", help="Optional output path for .feishu-audit.md.")
    parser.add_argument("--audit-json", help="Optional output path for .feishu-audit.json.")
    parser.add_argument(
        "--enable-color",
        action="store_true",
        help="Apply restrained label text color where the API style is stable enough.",
    )
    return parser.parse_args()


def resolve_document_id(
    doc_url: str | None,
    doc_token: str | None,
    blocks_json: str | None = None,
) -> str:
    if doc_token:
        return doc_token.strip()
    if doc_url:
        match = re.search(r"/docx/([A-Za-z0-9]+)", doc_url)
        if not match:
            raise SystemExit(f"Unable to parse Feishu document token from URL: {doc_url}")
        return match.group(1)
    if blocks_json:
        stem = Path(blocks_json).resolve().parent.name
        token = stem.split("-")[0]
        if token:
            return token
    raise SystemExit("Either --doc-url, --doc-token, or --blocks-json is required.")


def require_credentials() -> tuple[str, str]:
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    missing = [
        name
        for name, value in (("FEISHU_APP_ID", app_id), ("FEISHU_APP_SECRET", app_secret))
        if not value
    ]
    if missing:
        raise SystemExit("Missing required environment variables: " + ", ".join(missing))
    return app_id, app_secret


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def escape_md_cell(text: str) -> str:
    return text.replace("\\", "\\\\").replace("|", "\\|").replace("\n", "<br>")


def annotation_output_paths(note_path: Path) -> tuple[Path, Path]:
    base = note_path.with_suffix("")
    return (
        note_path.parent / f"{base.name}.format-annotations.md",
        note_path.parent / f"{base.name}.format-annotations.json",
    )


def audit_output_paths(note_path: Path) -> tuple[Path, Path]:
    base = note_path.with_suffix("")
    return (
        note_path.parent / f"{base.name}.feishu-audit.md",
        note_path.parent / f"{base.name}.feishu-audit.json",
    )


def sanitize_excerpt(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^>\s+", "", text)
    text = re.sub(r"^\s*[-*]\s+", "", text)
    text = re.sub(r"^\s*\d+\.\s+", "", text)
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)
    return re.sub(r"\s+", " ", text).strip()


def strip_markdown_links(text: str) -> str:
    return MARKDOWN_LINK_PATTERN.sub(lambda match: match.group("label"), text)


def markdown_inline_to_plain_text(text: str) -> str:
    text = strip_markdown_links(text)
    text = text.replace("**", "").replace("`", "")
    text = re.sub(r"(?<!\*)\*(?P<text>[^*\n][^*\n]*?)\*(?!\*)", r"\g<text>", text)
    return text.strip()


def extract_location_path(location: str) -> list[str]:
    prefix = location.split("@L", 1)[0].strip()
    if not prefix:
        return []
    return [part.strip() for part in prefix.split(">") if part.strip()]


def parse_pipe_row(line: str) -> list[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    cells = [cell.replace("\\|", "|").strip() for cell in stripped.split("|")]
    return [markdown_inline_to_plain_text(cell) for cell in cells]


def is_table_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(TABLE_SEPARATOR_PATTERN.fullmatch(cell.replace(" ", "")) for cell in cells)


def parse_pipe_table_lines(lines: list[str]) -> list[list[str]]:
    rows = [parse_pipe_row(line) for line in lines]
    if len(rows) >= 2 and is_table_separator_row(rows[1]):
        rows.pop(1)
    return rows


def normalized_text(text: str) -> str:
    text = sanitize_excerpt(text)
    text = text.replace("•", " ")
    return re.sub(r"\s+", "", text).lower()


def add_annotation(
    entries: list[AnnotationEntry],
    seen: set[tuple[str, str, str]],
    *,
    location: str,
    excerpt: str,
    action: str,
    intensity: str,
    reason: str,
    feishu_style: str,
) -> None:
    excerpt = sanitize_excerpt(excerpt)
    if not excerpt and action not in {"tighten_spacing", "preserve_spacing"}:
        return
    if action not in ALLOWED_ACTIONS:
        raise ValueError(f"Unsupported annotation action: {action}")
    key = (location, excerpt, action)
    if key in seen:
        return
    seen.add(key)
    entries.append(
        AnnotationEntry(
            位置=location,
            原文片段=excerpt or "(留白位置)",
            建议动作=action,
            强度等级=intensity,
            作用说明=reason,
            Feishu落地样式=feishu_style,
        )
    )


def location_from_context(headings: list[str], line_no: int) -> str:
    path = " > ".join(headings[-3:]) if headings else "正文"
    return f"{path} @L{line_no}"


def classify_highlight_semantics(excerpt: str, location: str) -> tuple[str, str, str]:
    excerpt = sanitize_excerpt(excerpt)
    if HIGHLIGHT_LABEL_PATTERN.match(excerpt) or any(
        label in excerpt for label in ("核心结论", "主要判断", "可借鉴点", "局限与改进", "全文概括")
    ):
        return "medium", "蓝色结构标签", "结构标签和收束标签优先使用蓝色强调，帮助读者快速定位段落功能。"
    if any(keyword in excerpt for keyword in YELLOW_HIGHLIGHT_KEYWORDS):
        return "medium", "黄色边界提醒", "边界、限制和注意事项应用黄色提醒，避免和红色结论句混在一起。"
    if any(keyword in excerpt for keyword in RED_HIGHLIGHT_KEYWORDS) or "Question&Study" in location:
        return "high", "红色关键判断", "关键纠偏句、反转句和强结论句应用红色强调，帮助读者抓住真正的判断核心。"
    return "medium", "蓝色结构标签", "默认颜色强调只服务于结构定位和短句收束，不给整段刷色。"


def generate_annotation_entries(note_path: Path) -> list[dict[str, str]]:
    lines = note_path.read_text(encoding="utf-8").splitlines()
    headings: list[str] = []
    entries: list[AnnotationEntry] = []
    seen: set[tuple[str, str, str]] = set()
    index = 0
    while index < len(lines):
        line = lines[index]
        line_no = index + 1
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group("title").strip()
            headings = headings[: max(level - 1, 0)]
            headings.append(title)
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=title,
                action="preserve_spacing",
                intensity="medium",
                reason="标题前后需要保留停顿，避免正文直接贴住标题导致层次塌陷。",
                feishu_style="保留标题上下必要留白",
            )
            index += 1
            continue

        if PIPE_TABLE_PATTERN.match(line):
            start = index
            table_lines = [line]
            index += 1
            while index < len(lines) and PIPE_TABLE_PATTERN.match(lines[index]):
                table_lines.append(lines[index])
                index += 1
            excerpt = "\n".join(table_lines)
            location = location_from_context(headings, start + 1)
            add_annotation(
                entries,
                seen,
                location=location,
                excerpt=excerpt,
                action="table_candidate",
                intensity="high",
                reason="这是连续管道表格，应优先转换为真实 Feishu 表格，避免继续依赖文本对齐。",
                feishu_style="真实表格块",
            )
            add_annotation(
                entries,
                seen,
                location=location,
                excerpt=table_lines[0],
                action="preserve_spacing",
                intensity="medium",
                reason="表格前后需要保留稳定留白，防止分析段与表格黏连。",
                feishu_style="保留表格前后留白",
            )
            continue

        quote_match = QUOTE_PATTERN.match(line)
        if quote_match:
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=quote_match.group("body"),
                action="quote_block",
                intensity="high",
                reason="这是收束句或总判断句，更适合在飞书中落为引用块以形成明显停顿。",
                feishu_style="引用块",
            )

        bullet_match = BULLET_PATTERN.match(line)
        if bullet_match:
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=bullet_match.group("body"),
                action="bullet_list",
                intensity="medium",
                reason="这是平级观察或平级结论，适合用普通分点提升扫描效率。",
                feishu_style="无序列表",
            )

        ordered_match = ORDERED_PATTERN.match(line)
        if ordered_match:
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=ordered_match.group("body"),
                action="numbered_list",
                intensity="medium",
                reason="这是顺序链或闭环链，适合用编号列表保持推进关系。",
                feishu_style="有序列表",
            )

        for match in BOLD_PATTERN.finditer(line):
            bold_excerpt = match.group("text")
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=bold_excerpt,
                action="bold",
                intensity="high",
                reason="这段内容已经承担关键判断或关键对比，应在飞书中保持明显强调。",
                feishu_style="文本粗体",
            )
            if any(keyword in bold_excerpt for keyword in RED_HIGHLIGHT_KEYWORDS) or any(
                keyword in bold_excerpt for keyword in YELLOW_HIGHLIGHT_KEYWORDS
            ):
                color_intensity, color_style, color_reason = classify_highlight_semantics(
                    bold_excerpt,
                    location_from_context(headings, line_no),
                )
                add_annotation(
                    entries,
                    seen,
                    location=location_from_context(headings, line_no),
                    excerpt=bold_excerpt,
                    action="highlight_color",
                    intensity=color_intensity,
                    reason=color_reason,
                    feishu_style=color_style,
                )

        for match in CODE_PATTERN.finditer(line):
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=match.group("text"),
                action="inline_code",
                intensity="medium",
                reason="模型名、字段名或符号名更适合用行内代码样式与普通叙述区分。",
                feishu_style="行内代码",
            )

        for match in ITALIC_PATTERN.finditer(line):
            text = match.group("text").strip()
            if text and len(text) <= 80:
                add_annotation(
                    entries,
                    seen,
                    location=location_from_context(headings, line_no),
                    excerpt=text,
                    action="italic",
                    intensity="low",
                    reason="这是轻量强调概念或英文术语，适合用斜体保持节奏。",
                    feishu_style="文本斜体",
                )

        label_match = HIGHLIGHT_LABEL_PATTERN.match(sanitize_excerpt(line))
        if label_match:
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=label_match.group("label"),
                action="highlight_color",
                intensity="medium",
                reason="这是标签式收束点，用受控颜色强化有助于读者快速识别段落用途。",
                feishu_style="受控标签色",
            )

        line_excerpt = sanitize_excerpt(line)
        if line_excerpt and len(line_excerpt) <= 90 and (
            any(keyword in line_excerpt for keyword in RED_HIGHLIGHT_KEYWORDS)
            or any(keyword in line_excerpt for keyword in YELLOW_HIGHLIGHT_KEYWORDS)
        ):
            color_intensity, color_style, color_reason = classify_highlight_semantics(
                line_excerpt,
                location_from_context(headings, line_no),
            )
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=line_excerpt,
                action="highlight_color",
                intensity=color_intensity,
                reason=color_reason,
                feishu_style=color_style,
            )

        if line.strip() == "":
            blank_run = 1
            while index + blank_run < len(lines) and lines[index + blank_run].strip() == "":
                blank_run += 1
            if blank_run > 1:
                add_annotation(
                    entries,
                    seen,
                    location=location_from_context(headings, line_no),
                    excerpt="",
                    action="tighten_spacing",
                    intensity="medium",
                    reason="连续空行超过一行会打断阅读节奏，应在终稿阶段做保守收缩。",
                    feishu_style="删除冗余空文本块或空行",
                )
            index += 1
            continue

        if "这说明" in line or "更准确地说" in line or "真正关键" in line:
            add_annotation(
                entries,
                seen,
                location=location_from_context(headings, line_no),
                excerpt=line,
                action="bold",
                intensity="medium",
                reason="这是段内收束或纠偏句，值得在飞书中被显化。",
                feishu_style="文本粗体",
            )

        index += 1
    return [entry.as_dict() for entry in entries]


def write_annotation_artifacts(
    note_path: Path,
    entries: list[dict[str, str]],
    markdown_path: Path | None = None,
    json_path: Path | None = None,
) -> tuple[Path, Path]:
    default_md, default_json = annotation_output_paths(note_path)
    markdown_path = markdown_path or default_md
    json_path = json_path or default_json
    ensure_directory(markdown_path.parent)
    ensure_directory(json_path.parent)
    lines = [
        "# 格式标注表",
        "",
        "| " + " | ".join(FORMAT_FIELDS) + " |",
        "| " + " | ".join(["---"] * len(FORMAT_FIELDS)) + " |",
    ]
    for entry in entries:
        lines.append("| " + " | ".join(escape_md_cell(entry[field]) for field in FORMAT_FIELDS) + " |")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(json_path, entries)
    return markdown_path, json_path


def write_audit_artifacts(
    note_path: Path,
    issues: list[dict[str, str]],
    markdown_path: Path | None = None,
    json_path: Path | None = None,
) -> tuple[Path, Path]:
    default_md, default_json = audit_output_paths(note_path)
    markdown_path = markdown_path or default_md
    json_path = json_path or default_json
    ensure_directory(markdown_path.parent)
    ensure_directory(json_path.parent)
    lines = [
        "# Feishu Audit Report",
        "",
        "| " + " | ".join(AUDIT_FIELDS) + " |",
        "| " + " | ".join(["---"] * len(AUDIT_FIELDS)) + " |",
    ]
    for issue in issues:
        lines.append("| " + " | ".join(escape_md_cell(issue[field]) for field in AUDIT_FIELDS) + " |")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    write_json(json_path, issues)
    return markdown_path, json_path


def scan_note_tables(note_path: Path) -> list[NoteTableSpec]:
    lines = note_path.read_text(encoding="utf-8").splitlines()
    headings: list[str] = []
    tables: list[NoteTableSpec] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            level = len(heading_match.group(1))
            title = heading_match.group("title").strip()
            headings = headings[: max(level - 1, 0)]
            headings.append(title)
            index += 1
            continue
        if PIPE_TABLE_PATTERN.match(line):
            start = index
            table_lines = [line]
            index += 1
            while index < len(lines) and PIPE_TABLE_PATTERN.match(lines[index]):
                table_lines.append(lines[index])
                index += 1
            tables.append(
                NoteTableSpec(
                    location=location_from_context(headings, start + 1),
                    line_no=start + 1,
                    headings=list(headings),
                    rows=parse_pipe_table_lines(table_lines),
                    source_lines=table_lines,
                )
            )
            continue
        index += 1
    return tables


def infer_note_path_from_annotations(annotations_path: Path) -> Path:
    name = annotations_path.name
    suffix = ".format-annotations.json"
    if name.endswith(suffix):
        return annotations_path.with_name(name[: -len(suffix)] + ".md")
    return annotations_path.with_suffix(".md")


def build_note_table_specs(
    note_path: Path | None,
    annotations: list[dict[str, str]],
) -> list[NoteTableSpec]:
    if note_path and note_path.exists():
        return scan_note_tables(note_path)

    tables: list[NoteTableSpec] = []
    for index, annotation in enumerate(annotations):
        if annotation[FORMAT_ACTION_FIELD] != "table_candidate":
            continue
        lines = [line for line in annotation[FORMAT_EXCERPT_FIELD].splitlines() if line.strip()]
        if not lines:
            continue
        rows = parse_pipe_table_lines(lines)
        if not rows:
            continue
        tables.append(
            NoteTableSpec(
                location=annotation[FORMAT_LOCATION_FIELD],
                line_no=index + 1,
                headings=extract_location_path(annotation[FORMAT_LOCATION_FIELD]),
                rows=rows,
                source_lines=lines,
            )
        )
    return tables


def heading_level_from_block_type(block_type: int | None) -> int | None:
    if block_type is None or block_type not in HEADING_BLOCK_TYPES:
        return None
    return block_type - 2


def extract_block_visible_text(block: dict[str, Any]) -> str:
    _, container = get_text_container(block)
    if not container:
        return ""
    return visible_text(container.get("elements", []))


def collect_descendant_visible_text(
    block_id: str,
    block_map: dict[str, dict[str, Any]],
    visited: set[str] | None = None,
) -> str:
    if not block_id:
        return ""
    if visited is None:
        visited = set()
    if block_id in visited:
        return ""
    visited.add(block_id)
    block = block_map.get(block_id)
    if not block:
        return ""
    direct_text = extract_block_visible_text(block)
    if direct_text:
        return direct_text
    parts: list[str] = []
    for child_id in block.get("children", []):
        child_text = collect_descendant_visible_text(child_id, block_map, visited)
        if child_text:
            parts.append(child_text)
    return "\n".join(part for part in parts if part)


def normalize_table_cell(text: str) -> str:
    return normalized_text(markdown_inline_to_plain_text(text))


def normalize_table_rows(rows: list[list[str]]) -> list[list[str]]:
    return [[normalize_table_cell(cell) for cell in row] for row in rows]


def table_rows_equal(left: list[list[str]], right: list[list[str]]) -> bool:
    return normalize_table_rows(left) == normalize_table_rows(right)


def build_page_context(
    blocks: list[dict[str, Any]],
) -> tuple[str | None, dict[str, dict[str, Any]], list[dict[str, Any]]]:
    block_map = {block["block_id"]: block for block in blocks if block.get("block_id")}
    page_block = next((block for block in blocks if block.get("block_type") == 1), None)
    if not page_block:
        return None, block_map, []

    heading_stack: list[str] = []
    contexts: list[dict[str, Any]] = []
    for index, child_id in enumerate(page_block.get("children", [])):
        block = block_map.get(child_id)
        block_type = block.get("block_type") if block else None
        text = extract_block_visible_text(block) if block else ""
        level = heading_level_from_block_type(block_type)
        if level is not None:
            heading_stack = heading_stack[: max(level - 1, 0)]
            heading_stack.append(text.strip())
        contexts.append(
            {
                "index": index,
                "block_id": child_id,
                "block_type": block_type,
                "text": text,
                "path": list(heading_stack),
            }
        )
    return page_block.get("block_id"), block_map, contexts


def path_covers(context_path: list[str], expected_path: list[str]) -> bool:
    if not expected_path:
        return True
    if len(context_path) >= len(expected_path):
        if context_path[: len(expected_path)] == expected_path:
            return True
        return context_path[-len(expected_path) :] == expected_path
    return expected_path[-len(context_path) :] == context_path


def resolve_section_range(
    contexts: list[dict[str, Any]],
    expected_path: list[str],
) -> tuple[int, int] | None:
    indexes = [ctx["index"] for ctx in contexts if path_covers(ctx["path"], expected_path)]
    if not indexes:
        return None
    return min(indexes), max(indexes) + 1


def extract_table_rows_from_block(
    table_block: dict[str, Any],
    block_map: dict[str, dict[str, Any]],
) -> list[list[str]]:
    if table_block.get("block_type") not in TABLE_BLOCK_TYPES:
        return []
    table = table_block.get("table", {})
    property_data = table.get("property", {})
    row_size = int(property_data.get("row_size", 0) or 0)
    column_size = int(property_data.get("column_size", 0) or 0)
    cells = table.get("cells", [])
    if row_size <= 0 or column_size <= 0 or not cells:
        return []

    rows: list[list[str]] = []
    cursor = 0
    for _ in range(row_size):
        row: list[str] = []
        for _ in range(column_size):
            if cursor >= len(cells):
                row.append("")
            else:
                row.append(collect_descendant_visible_text(cells[cursor], block_map).strip())
            cursor += 1
        rows.append(row)
    return rows


def build_audit_issue(
    *,
    location: str,
    expected_action: str,
    current_state: str,
    problem_type: str,
    severity: str,
    evidence: str,
    repair: str,
    auto_fixable: bool,
) -> dict[str, str]:
    return {
        AUDIT_FIELDS[0]: location,
        AUDIT_FIELDS[1]: expected_action,
        AUDIT_FIELDS[2]: current_state,
        AUDIT_FIELDS[3]: problem_type,
        AUDIT_FIELDS[4]: severity,
        AUDIT_FIELDS[5]: evidence,
        AUDIT_FIELDS[6]: repair,
        AUDIT_FIELDS[7]: AUDIT_AUTO_FIX_TRUE if auto_fixable else AUDIT_AUTO_FIX_FALSE,
    }


def table_state_summary(
    table_rows: list[list[str]],
    pipe_lines: list[str],
) -> str:
    parts: list[str] = []
    if table_rows:
        parts.append(f"native_table={len(table_rows)}x{max((len(row) for row in table_rows), default=0)}")
    if pipe_lines:
        parts.append(f"pipe_rows={len(pipe_lines)}")
    return ", ".join(parts) if parts else "no_table_found"


def read_annotations(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise SystemExit(f"Annotation JSON must be a list: {path}")
    normalized_entries: list[dict[str, str]] = []
    for item in data:
        if not isinstance(item, dict):
            raise SystemExit(f"Annotation entry must be an object: {path}")
        normalized_item = {}
        for field in FORMAT_FIELDS:
            if field not in item:
                raise SystemExit(f"Missing annotation field {field} in {path}")
            normalized_item[field] = str(item[field])
        if normalized_item["建议动作"] not in ALLOWED_ACTIONS:
            raise SystemExit(f"Unsupported annotation action: {normalized_item['建议动作']}")
        normalized_entries.append(normalized_item)
    return normalized_entries


def get_text_container(block: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    for key, value in block.items():
        if key in META_KEYS or not isinstance(value, dict):
            continue
        if "elements" in value:
            return key, value
    return None, None


def is_safe_editable_element(element: dict[str, Any]) -> bool:
    return len(element) == 1 and next(iter(element.keys())) in SAFE_ELEMENT_TYPES


def visible_text(elements: list[dict[str, Any]]) -> str:
    parts: list[str] = []
    for element in elements:
        if "text_run" in element:
            parts.append(element["text_run"].get("content", ""))
        elif "equation" in element:
            parts.append(element["equation"].get("content", ""))
        elif "mention_doc" in element:
            parts.append("@文档")
        elif "mention_user" in element:
            parts.append("@用户")
        elif "reminder" in element:
            parts.append("@提醒")
    return "".join(parts)


def make_excerpt(elements: list[dict[str, Any]], limit: int = 100) -> str:
    text = visible_text(elements).replace("\n", "\\n")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def normalize_text_run_content(content: str, *, is_terminal_run: bool) -> str:
    normalized = content.replace("\u00a0", " ")
    normalized = re.sub(r"[ \t]+\n", "\n", normalized)
    if is_terminal_run:
        normalized = re.sub(r"[ \t]+$", "", normalized)
    return normalized


def normalize_equation_content(content: str) -> str:
    stripped = content.strip()
    for pattern in DISPLAY_FORMULA_PATTERNS:
        match = pattern.match(stripped)
        if match:
            return match.group("expr").strip()
    return stripped


def unwrap_display_formula(text: str) -> str | None:
    stripped = text.strip()
    for pattern in DISPLAY_FORMULA_PATTERNS:
        match = pattern.match(stripped)
        if match:
            expr = match.group("expr").strip()
            if expr:
                return expr
    return None


def is_obvious_inline_formula(expr: str) -> bool:
    expr = expr.strip()
    if not expr or len(expr) > 80:
        return False
    if re.search(r"https?://", expr):
        return False
    if re.search(r"[\u4e00-\u9fff]", expr):
        return False
    if expr.isdigit():
        return False
    if re.fullmatch(r"[A-Za-z][A-Za-z0-9_{}^]*", expr):
        return True
    if any(ch in expr for ch in "\\_^=+-*/()[]{}"):
        return bool(re.fullmatch(r"[A-Za-z0-9\\_^=+\-*/(){}\[\].,: ]+", expr))
    return False


def append_action(actions: list[str], action: str) -> None:
    if action not in actions:
        actions.append(action)


def merge_styles(*styles: dict[str, Any] | None) -> dict[str, Any] | None:
    merged: dict[str, Any] = {}
    for style in styles:
        if style:
            merged.update(style)
    return merged or None


def build_text_run_element(content: str, style: dict[str, Any] | None) -> dict[str, Any] | None:
    if not content:
        return None
    text_run: dict[str, Any] = {"content": content}
    if style:
        text_run["text_element_style"] = style
    return {"text_run": text_run}


def split_text_run_markdown(
    content: str,
    base_style: dict[str, Any] | None,
    inherited_style: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    if not content:
        return []
    if "`" not in content and "**" not in content:
        element = build_text_run_element(content, merge_styles(base_style, inherited_style))
        return [element] if element else []

    output: list[dict[str, Any]] = []
    cursor = 0
    for match in INLINE_MARKDOWN_PATTERN.finditer(content):
        if match.start() > cursor:
            plain = build_text_run_element(
                content[cursor : match.start()],
                merge_styles(base_style, inherited_style),
            )
            if plain:
                output.append(plain)

        token = match.group(0)
        if token.startswith("`"):
            inner = token[1:-1]
            style = merge_styles(base_style, inherited_style, {"inline_code": True})
        else:
            inner = token[2:-2]
            style = merge_styles(base_style, inherited_style, {"bold": True})
        marked = build_text_run_element(inner, style)
        if marked:
            output.append(marked)
        cursor = match.end()

    if cursor < len(content):
        tail = build_text_run_element(content[cursor:], merge_styles(base_style, inherited_style))
        if tail:
            output.append(tail)
    return output


def render_markdown_artifacts(
    block_type: int,
    elements: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    if not elements or any("text_run" not in element for element in elements):
        return elements, []

    first_text_index = None
    prefix_mode: str | None = None
    for index, element in enumerate(elements):
        content = element["text_run"].get("content", "")
        if not content:
            continue
        first_text_index = index
        if block_type == 2 and content.startswith("> "):
            prefix_mode = "quote"
        elif block_type == 2 and content.startswith("* "):
            prefix_mode = "bullet-marker"
        break

    output: list[dict[str, Any]] = []
    actions: list[str] = []
    for index, element in enumerate(elements):
        content = element["text_run"].get("content", "")
        base_style = copy.deepcopy(element["text_run"].get("text_element_style", {}))
        inherited_style: dict[str, Any] | None = None
        had_backticks = "`" in content
        had_bold_markers = "**" in content

        if index == first_text_index and prefix_mode == "quote":
            content = content[2:]
            inherited_style = {"italic": True, "text_color": DEFAULT_QUOTE_COLOR}
            append_action(actions, "render-quote-marker")
        elif index == first_text_index and prefix_mode == "bullet-marker":
            content = "• " + content[2:]
            append_action(actions, "render-bullet-marker")

        if prefix_mode == "quote" and inherited_style is None:
            inherited_style = {"italic": True, "text_color": DEFAULT_QUOTE_COLOR}

        split_elements = split_text_run_markdown(content, base_style, inherited_style)
        if had_backticks and any(
            part.get("text_run", {}).get("text_element_style", {}).get("inline_code")
            for part in split_elements
        ):
            append_action(actions, "render-inline-code")
        if had_bold_markers and any(
            part.get("text_run", {}).get("text_element_style", {}).get("bold")
            for part in split_elements
        ):
            append_action(actions, "render-bold-marker")
        output.extend(split_elements)

    return output, actions


def render_inline_formulas(elements: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], bool]:
    if not elements or any("text_run" not in element for element in elements):
        return elements, False
    changed = False
    output: list[dict[str, Any]] = []
    for element in elements:
        content = element["text_run"].get("content", "")
        base_style = copy.deepcopy(element["text_run"].get("text_element_style", {}))
        cursor = 0
        local_changed = False
        for match in INLINE_FORMULA_PATTERN.finditer(content):
            expr = match.group("expr").strip()
            if not is_obvious_inline_formula(expr):
                continue
            local_changed = True
            if match.start() > cursor:
                plain = build_text_run_element(content[cursor:match.start()], base_style)
                if plain:
                    output.append(plain)
            output.append({"equation": {"content": expr}})
            cursor = match.end()
        if not local_changed:
            output.append(copy.deepcopy(element))
            continue
        changed = True
        if cursor < len(content):
            tail = build_text_run_element(content[cursor:], base_style)
            if tail:
                output.append(tail)
    return output, changed


def maybe_style_heading(
    elements: list[dict[str, Any]],
    block_type: int,
    enable_color: bool,
) -> tuple[list[dict[str, Any]], str | None]:
    if not enable_color or block_type != 4:
        return elements, None
    if any("text_run" not in element for element in elements):
        return elements, None

    changed = False
    updated = copy.deepcopy(elements)
    for element in updated:
        style = copy.deepcopy(element["text_run"].get("text_element_style", {}))
        if style.get("text_color") == DEFAULT_LABEL_COLOR and style.get("bold"):
            continue
        style["bold"] = True
        style["text_color"] = DEFAULT_LABEL_COLOR
        element["text_run"]["text_element_style"] = style
        changed = True
    return (updated, "color-heading2") if changed else (elements, None)


def maybe_emphasize_leading_label(
    elements: list[dict[str, Any]],
    enable_color: bool,
) -> tuple[list[dict[str, Any]], str | None]:
    for index, element in enumerate(elements):
        if "text_run" not in element:
            return elements, None

        text_run = element["text_run"]
        content = text_run.get("content", "")
        if not content:
            continue
        if text_run.get("comment_ids") or text_run.get("link"):
            return elements, None

        match = LEADING_LABEL_PATTERN.match(content)
        if not match:
            return elements, None

        base_style = copy.deepcopy(text_run.get("text_element_style", {}))
        label_style = copy.deepcopy(base_style)
        already_colored = label_style.get("text_color") == DEFAULT_LABEL_COLOR
        if label_style.get("bold") and (not enable_color or already_colored):
            return elements, None

        label_style["bold"] = True
        if enable_color:
            label_style["text_color"] = DEFAULT_LABEL_COLOR

        prefix_content = match.group("prefix") or ""
        label_content = match.group("label")
        rest_content = content[match.end() :]
        new_elements = copy.deepcopy(elements[:index])

        if prefix_content:
            prefix_element = copy.deepcopy(element)
            prefix_element["text_run"]["content"] = prefix_content
            if base_style:
                prefix_element["text_run"]["text_element_style"] = base_style
            else:
                prefix_element["text_run"].pop("text_element_style", None)
            new_elements.append(prefix_element)

        label_element = copy.deepcopy(element)
        label_element["text_run"]["content"] = label_content
        label_element["text_run"]["text_element_style"] = label_style
        new_elements.append(label_element)

        if rest_content:
            rest_element = copy.deepcopy(element)
            rest_element["text_run"]["content"] = rest_content
            if base_style:
                rest_element["text_run"]["text_element_style"] = base_style
            else:
                rest_element["text_run"].pop("text_element_style", None)
            new_elements.append(rest_element)

        new_elements.extend(copy.deepcopy(elements[index + 1 :]))
        action = "bold-leading-label-with-color" if enable_color else "bold-leading-label"
        return new_elements, action
    return elements, None


def apply_style_to_substring(
    elements: list[dict[str, Any]],
    substring: str,
    style_updates: dict[str, Any],
) -> tuple[list[dict[str, Any]], bool]:
    if not elements or any("text_run" not in element for element in elements):
        return elements, False
    full_text = "".join(element["text_run"].get("content", "") for element in elements)
    if not substring:
        return elements, False
    start = full_text.find(substring)
    if start < 0:
        return elements, False
    end = start + len(substring)
    cursor = 0
    output: list[dict[str, Any]] = []
    changed = False
    for element in elements:
        content = element["text_run"].get("content", "")
        base_style = copy.deepcopy(element["text_run"].get("text_element_style", {}))
        local_start = cursor
        local_end = cursor + len(content)
        if local_end <= start or local_start >= end:
            output.append(copy.deepcopy(element))
            cursor = local_end
            continue

        overlap_start = max(start, local_start) - local_start
        overlap_end = min(end, local_end) - local_start
        prefix = content[:overlap_start]
        middle = content[overlap_start:overlap_end]
        suffix = content[overlap_end:]
        if prefix:
            prefix_element = build_text_run_element(prefix, base_style)
            if prefix_element:
                output.append(prefix_element)
        if middle:
            middle_style = merge_styles(base_style, style_updates)
            middle_element = build_text_run_element(middle, middle_style)
            if middle_element:
                output.append(middle_element)
            if middle_style != base_style:
                changed = True
        if suffix:
            suffix_element = build_text_run_element(suffix, base_style)
            if suffix_element:
                output.append(suffix_element)
        cursor = local_end
    return output, changed


def apply_action_to_block_state(
    state: BlockState,
    excerpt: str,
    action: str,
    intensity: str,
) -> bool:
    if action not in EMPHASIS_ACTIONS:
        return False
    style_updates: dict[str, Any] = {}
    if action == "bold":
        style_updates["bold"] = True
    elif action == "italic":
        style_updates["italic"] = True
    elif action == "inline_code":
        style_updates["inline_code"] = True
    elif action == "highlight_color":
        if any(keyword in excerpt for keyword in RED_HIGHLIGHT_KEYWORDS):
            style_updates["text_color"] = DEFAULT_CRITICAL_COLOR
        elif any(keyword in excerpt for keyword in YELLOW_HIGHLIGHT_KEYWORDS):
            style_updates["text_color"] = DEFAULT_WARNING_COLOR
        else:
            style_updates["text_color"] = DEFAULT_LABEL_COLOR
        if intensity == "high":
            style_updates["bold"] = True
    updated_elements, changed = apply_style_to_substring(state.updated_elements, excerpt, style_updates)
    if changed:
        state.updated_elements = updated_elements
        append_action(state.actions, f"annotation-{action}")
    return changed


def build_block_states(
    blocks: list[dict[str, Any]],
    enable_color: bool,
) -> tuple[dict[str, BlockState], list[dict[str, Any]], Counter[str]]:
    states: dict[str, BlockState] = {}
    blank_blocks: list[dict[str, Any]] = []
    skip_reasons: Counter[str] = Counter()
    for block in blocks:
        block_type = block.get("block_type")
        if block_type not in EDITABLE_BLOCK_TYPES:
            continue
        _, container = get_text_container(block)
        if not container:
            continue
        elements = container.get("elements", [])
        if not elements:
            continue
        if any(not is_safe_editable_element(element) for element in elements):
            skip_reasons.update(["unsupported-inline-element"])
            continue
        current_text = visible_text(elements)
        if not current_text.strip():
            blank_blocks.append(block)
            skip_reasons.update(["blank-text-block"])
            continue
        state = BlockState(
            block_id=block["block_id"],
            block_type=block_type,
            block_name=BLOCK_TYPE_NAMES.get(block_type, str(block_type)),
            original_elements=copy.deepcopy(elements),
            updated_elements=copy.deepcopy(elements),
            actions=[],
        )
        last_text_run_index = None
        for idx, element in enumerate(state.updated_elements):
            if "text_run" in element:
                last_text_run_index = idx
        whitespace_touched = False
        equation_touched = False
        for idx, element in enumerate(state.updated_elements):
            if "text_run" in element:
                content = element["text_run"].get("content", "")
                normalized = normalize_text_run_content(
                    content,
                    is_terminal_run=idx == last_text_run_index,
                )
                if normalized != content:
                    element["text_run"]["content"] = normalized
                    whitespace_touched = True
            elif "equation" in element:
                content = element["equation"].get("content", "")
                normalized = normalize_equation_content(content)
                if normalized != content:
                    element["equation"]["content"] = normalized
                    equation_touched = True
        if whitespace_touched:
            append_action(state.actions, "trim-trailing-whitespace")
        if equation_touched:
            append_action(state.actions, "normalize-equation-content")

        current_visible = visible_text(state.updated_elements)
        if block_type == 2 and all("text_run" in element for element in state.updated_elements):
            expression = unwrap_display_formula(current_visible)
            if expression:
                state.updated_elements = [{"equation": {"content": expression}}]
                append_action(state.actions, "normalize-display-formula")
                states[state.block_id] = state
                continue

        rendered_elements, render_actions = render_markdown_artifacts(block_type, state.updated_elements)
        if render_actions:
            state.updated_elements = rendered_elements
            for action in render_actions:
                append_action(state.actions, action)

        inline_elements, inline_changed = render_inline_formulas(state.updated_elements)
        if inline_changed:
            state.updated_elements = inline_elements
            append_action(state.actions, "normalize-inline-formula")

        if block_type in LABEL_EMPHASIS_BLOCK_TYPES:
            emphasized_elements, label_action = maybe_emphasize_leading_label(
                state.updated_elements, enable_color
            )
            if label_action:
                state.updated_elements = emphasized_elements
                append_action(state.actions, label_action)

        heading_elements, heading_action = maybe_style_heading(
            state.updated_elements, block_type, enable_color
        )
        if heading_action:
            state.updated_elements = heading_elements
            append_action(state.actions, heading_action)

        states[state.block_id] = state
    return states, blank_blocks, skip_reasons


def build_search_index(states: dict[str, BlockState]) -> list[tuple[str, str]]:
    indexed = [
        (block_id, normalized_text(visible_text(state.updated_elements)))
        for block_id, state in states.items()
    ]
    indexed.sort(key=lambda item: len(item[1]), reverse=True)
    return indexed


def find_matching_block_id(excerpt: str, search_index: list[tuple[str, str]]) -> str | None:
    target = normalized_text(excerpt)
    if not target or target == normalized_text("(留白位置)"):
        return None
    best_block_id = None
    best_score = -1
    for block_id, normalized_visible in search_index:
        if not normalized_visible:
            continue
        if target in normalized_visible or normalized_visible in target:
            score = min(len(target), len(normalized_visible))
            if score > best_score:
                best_score = score
                best_block_id = block_id
    return best_block_id


def contiguous_ranges(indexes: list[int]) -> list[tuple[int, int]]:
    if not indexes:
        return []
    ranges: list[tuple[int, int]] = []
    start = indexes[0]
    end = indexes[0]
    for value in indexes[1:]:
        if value == end + 1:
            end = value
            continue
        ranges.append((start, end))
        start = value
        end = value
    ranges.append((start, end))
    return ranges


def build_child_index_map(
    blocks: list[dict[str, Any]],
) -> dict[str, tuple[str, int, int | None]]:
    child_indexes: dict[str, tuple[str, int, int | None]] = {}
    for block in blocks:
        parent_id = block.get("block_id")
        if not parent_id:
            continue
        parent_type = block.get("block_type")
        for index, child_id in enumerate(block.get("children", [])):
            child_indexes[child_id] = (parent_id, index, parent_type)
    return child_indexes


def strip_prefix_from_elements(
    elements: list[dict[str, Any]],
    *,
    literal_prefixes: tuple[str, ...] = (),
    regex_prefix: str | None = None,
) -> list[dict[str, Any]] | None:
    updated = copy.deepcopy(elements)
    for index, element in enumerate(updated):
        text_run = element.get("text_run")
        if not text_run:
            continue
        content = text_run.get("content", "")
        if not content:
            continue
        stripped = content
        for prefix in literal_prefixes:
            if stripped.startswith(prefix):
                stripped = stripped[len(prefix) :]
                break
        else:
            if regex_prefix:
                stripped = re.sub(regex_prefix, "", stripped, count=1)
        if stripped == content:
            return None
        text_run["content"] = stripped
        normalized = [candidate for candidate in updated if candidate.get("text_run", {}).get("content", "") or "text_run" not in candidate]
        return normalized or updated[index : index + 1]
    return None


def build_list_block_replacement_proposal(
    action: str,
    block_id: str,
    location: str,
    block_map: dict[str, dict[str, Any]],
    states: dict[str, BlockState],
    child_indexes: dict[str, tuple[str, int, int | None]],
) -> Proposal | None:
    if action not in LIST_ACTIONS:
        return None
    state = states.get(block_id)
    if not state or state.block_type != 2:
        return None
    child_info = child_indexes.get(block_id)
    if not child_info:
        return None
    parent_id, start_index, parent_type = child_info
    if parent_type in TABLE_BLOCK_TYPES | TABLE_CELL_BLOCK_TYPES:
        return None

    replacement_elements = copy.deepcopy(state.updated_elements)
    if action == "bullet_list":
        stripped = strip_prefix_from_elements(
            replacement_elements,
            literal_prefixes=("• ", "* ", "- "),
        )
        if stripped is None:
            return None
        replacement_elements = stripped
    elif action == "numbered_list":
        stripped = strip_prefix_from_elements(
            replacement_elements,
            regex_prefix=r"^\d+\.\s+",
        )
        if stripped is None:
            return None
        replacement_elements = stripped
    elif action == "quote_block":
        stripped = strip_prefix_from_elements(
            replacement_elements,
            literal_prefixes=("> ",),
        )
        if stripped is not None:
            replacement_elements = stripped

    target_block_type = next(iter(expected_list_block_type(action) - {34}))
    return Proposal(
        proposal_type="replace_block_type",
        block_id=parent_id,
        block_type=parent_type,
        actions=[f"annotation-{action}", "normalize-block-type"],
        before=make_excerpt(state.original_elements),
        after=f"{LIST_FIELD_NAMES[action]} block",
        meta={
            "location": location,
            "source_block_id": block_id,
            "start_index": start_index,
            "end_index": start_index + 1,
            "target_block_type": target_block_type,
            "target_field_name": LIST_FIELD_NAMES[action],
            "elements": replacement_elements,
        },
    )


def build_blank_delete_proposals(
    blank_blocks: list[dict[str, Any]],
    blocks: list[dict[str, Any]],
) -> list[Proposal]:
    block_map = {block["block_id"]: block for block in blocks if block.get("block_id")}
    grouped: dict[str, list[int]] = defaultdict(list)
    for blank_block in blank_blocks:
        parent_id = blank_block.get("parent_id")
        if not parent_id:
            continue
        parent = block_map.get(parent_id)
        if not parent:
            continue
        children = parent.get("children", [])
        if blank_block["block_id"] in children:
            grouped[parent_id].append(children.index(blank_block["block_id"]))
    proposals: list[Proposal] = []
    for parent_id, indexes in grouped.items():
        for start, end in contiguous_ranges(sorted(set(indexes))):
            exclusive_end = end + 1
            proposals.append(
                Proposal(
                    proposal_type="delete_children",
                    block_id=parent_id,
                    block_type=block_map.get(parent_id, {}).get("block_type"),
                    actions=["tighten-spacing-blank-blocks"],
                    before=f"children[{start}:{exclusive_end})",
                    after="deleted blank text blocks",
                    # Feishu batch_delete uses a half-open range [start_index, end_index).
                    meta={"start_index": start, "end_index": exclusive_end},
                )
            )
    return proposals


def build_text_update_proposals(
    states: dict[str, BlockState],
    excluded_block_ids: set[str] | None = None,
) -> list[Proposal]:
    excluded_block_ids = excluded_block_ids or set()
    proposals: list[Proposal] = []
    for state in states.values():
        if state.block_id in excluded_block_ids:
            continue
        if state.updated_elements == state.original_elements:
            continue
        proposals.append(
            Proposal(
                proposal_type="update_text_elements",
                block_id=state.block_id,
                block_type=state.block_type,
                actions=list(dict.fromkeys(state.actions)),
                before=make_excerpt(state.original_elements),
                after=make_excerpt(state.updated_elements),
                request={
                    "block_id": state.block_id,
                    "update_text_elements": {"elements": state.updated_elements},
                },
            )
        )
    return proposals


def annotation_severity(intensity: str) -> str:
    if intensity == "high":
        return "high"
    if intensity == "medium":
        return "medium"
    return "low"


def block_state_summary(block: dict[str, Any] | None) -> str:
    if not block:
        return "missing_block"
    block_type = block.get("block_type")
    name = BLOCK_TYPE_NAMES.get(block_type, str(block_type))
    text = sanitize_excerpt(extract_block_visible_text(block))
    if text:
        return f"{name}: {text[:60]}"
    return name


def expected_list_block_type(action: str) -> set[int]:
    if action == "bullet_list":
        return {12}
    if action == "numbered_list":
        return {13}
    if action == "quote_block":
        return {15, 34}
    return set()


def build_table_candidate_proposals(
    page_id: str | None,
    block_map: dict[str, dict[str, Any]],
    contexts: list[dict[str, Any]],
    table_specs: list[NoteTableSpec],
) -> tuple[list[Proposal], list[dict[str, str]], list[str], set[str]]:
    proposals: list[Proposal] = []
    issues: list[dict[str, str]] = []
    notes: list[str] = []
    satisfied_locations: set[str] = set()
    if not page_id or not contexts or not table_specs:
        return proposals, issues, notes, satisfied_locations

    for spec in table_specs:
        expected_path = extract_location_path(spec.location)
        section_range = resolve_section_range(contexts, expected_path)
        if not section_range:
            issues.append(
                build_audit_issue(
                    location=spec.location,
                    expected_action="table_candidate",
                    current_state="section_not_found",
                    problem_type="location_miss",
                    severity="high",
                    evidence="Feishu 块树中没有找到与该位置路径一致的标题范围。",
                    repair="检查标题路径是否漂移，确认该表格是否被移动到别处。",
                    auto_fixable=False,
                )
            )
            continue

        start_index, end_index = section_range
        section_contexts = contexts[start_index:end_index]
        table_contexts = [
            ctx for ctx in section_contexts if ctx.get("block_type") in TABLE_BLOCK_TYPES
        ]
        pipe_contexts = [
            ctx for ctx in section_contexts if PIPE_TABLE_PATTERN.match(ctx.get("text", "").strip())
        ]
        pipe_indexes = [ctx["index"] for ctx in pipe_contexts]
        pipe_lines = [ctx["text"] for ctx in pipe_contexts]

        exact_table = None
        partial_table = None
        for ctx in table_contexts:
            rows = extract_table_rows_from_block(block_map.get(ctx["block_id"], {}), block_map)
            if table_rows_equal(rows, spec.rows):
                exact_table = (ctx, rows)
                break
            if spec.rows and rows and table_rows_equal(rows, [spec.rows[0]]):
                partial_table = (ctx, rows)

        pipe_rows = parse_pipe_table_lines(pipe_lines) if pipe_lines else []
        table_summary = table_state_summary(exact_table[1] if exact_table else (partial_table[1] if partial_table else []), pipe_lines)

        if exact_table and not pipe_contexts:
            satisfied_locations.add(spec.location)
            note = f"Preserved native table at {spec.location}."
            if note not in notes:
                notes.append(note)
            continue

        replacement_start = None
        replacement_end = None
        if exact_table and pipe_contexts:
            replacement_start = min(exact_table[0]["index"], pipe_indexes[0])
            replacement_end = max(exact_table[0]["index"] + 1, pipe_indexes[-1] + 1)
        elif partial_table and pipe_contexts and table_rows_equal(pipe_rows, spec.rows[1:]):
            replacement_start = min(partial_table[0]["index"], pipe_indexes[0])
            replacement_end = max(partial_table[0]["index"] + 1, pipe_indexes[-1] + 1)
        elif pipe_contexts and table_rows_equal(pipe_rows, spec.rows):
            replacement_start = pipe_indexes[0]
            replacement_end = pipe_indexes[-1] + 1

        if replacement_start is None or replacement_end is None:
            issues.append(
                build_audit_issue(
                    location=spec.location,
                    expected_action="table_candidate",
                    current_state=table_summary,
                    problem_type="table_miss",
                    severity="high",
                    evidence="当前位置没有完整命中目标表格，或仍保留未解析的 Markdown 管道表格。",
                    repair="按该位置重建原生 Feishu 表格，并清理残留管道文本。",
                    auto_fixable=bool(pipe_contexts or partial_table),
                )
            )
            continue

        before_parts: list[str] = []
        for ctx in section_contexts:
            if replacement_start <= ctx["index"] < replacement_end:
                before_parts.append(ctx.get("text", "") or BLOCK_TYPE_NAMES.get(ctx.get("block_type"), ""))
        proposals.append(
            Proposal(
                proposal_type="replace_pipe_table",
                block_id=page_id,
                block_type=1,
                actions=["table-candidate-rebuild"],
                before=" | ".join(part for part in before_parts if part)[:240],
                after=f"native table {len(spec.rows)}x{max((len(row) for row in spec.rows), default=0)}",
                meta={
                    "location": spec.location,
                    "start_index": replacement_start,
                    "end_index": replacement_end,
                    "rows": spec.rows,
                    "source_lines": before_parts,
                },
            )
        )
        issues.append(
            build_audit_issue(
                location=spec.location,
                expected_action="table_candidate",
                current_state=table_summary,
                problem_type="table_rebuild_required",
                severity="high",
                evidence="检测到残余 Markdown 管道表格，或只命中了部分原生表格。",
                repair="删除当前位置的残余表格文本并重建为原生 Feishu table block。",
                auto_fixable=True,
            )
        )

    return proposals, issues, notes, satisfied_locations


def build_blank_spacing_issues(
    proposals: list[Proposal],
) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []
    for proposal in proposals:
        meta = proposal.meta or {}
        issues.append(
            build_audit_issue(
                location=f"{proposal.block_id}@children[{meta.get('start_index')}:{meta.get('end_index')})",
                expected_action="tighten_spacing",
                current_state=proposal.before,
                problem_type="redundant_blank_block",
                severity="medium",
                evidence="检测到纯空文本块或连续空白块仍留在飞书文档中。",
                repair="保守删除纯空文本块，保留标题、表格、公式与引用前后的必要留白。",
                auto_fixable=True,
            )
        )
    return issues


def analyze_blocks(
    document_id: str,
    blocks: list[dict[str, Any]],
    annotations: list[dict[str, str]],
    enable_color: bool,
    table_specs: list[NoteTableSpec] | None = None,
) -> dict[str, Any]:
    table_specs = table_specs or []
    page_id, block_map, contexts = build_page_context(blocks)
    states, blank_blocks, skip_reasons = build_block_states(blocks, enable_color)
    search_index = build_search_index(states)
    child_indexes = build_child_index_map(blocks)
    matched_annotations = 0
    unmatched_annotations: list[dict[str, str]] = []
    satisfied_annotations = 0
    pending_annotations: list[dict[str, str]] = []
    list_replace_proposals: list[Proposal] = []
    seen_list_replace_keys: set[tuple[str, str]] = set()
    table_notes: list[str] = []
    table_annotations = [
        annotation for annotation in annotations if annotation[FORMAT_ACTION_FIELD] == "table_candidate"
    ]
    for annotation in annotations:
        action = annotation[FORMAT_ACTION_FIELD]
        excerpt = annotation[FORMAT_EXCERPT_FIELD]
        block_id = find_matching_block_id(excerpt, search_index)
        if action == "table_candidate":
            continue
        if action == "preserve_spacing":
            satisfied_annotations += 1
            continue
        if action == "tighten_spacing":
            satisfied_annotations += 1
            continue
        if action in EMPHASIS_ACTIONS:
            if not block_id or block_id not in states:
                unmatched_annotations.append(annotation)
                pending_annotations.append(
                    build_audit_issue(
                        location=annotation[FORMAT_LOCATION_FIELD],
                        expected_action=action,
                        current_state="missing_block",
                        problem_type="target_not_found",
                        severity=annotation_severity(annotation[FORMAT_INTENSITY_FIELD]),
                        evidence="Annotation excerpt could not be located in the current Feishu block tree.",
                        repair="Check whether the target sentence was manually rewritten or moved, then regenerate annotations.",
                        auto_fixable=False,
                    )
                )
                continue
            if apply_action_to_block_state(
                states[block_id], excerpt, action, annotation[FORMAT_INTENSITY_FIELD]
            ):
                matched_annotations += 1
                pending_annotations.append(
                    build_audit_issue(
                        location=annotation[FORMAT_LOCATION_FIELD],
                        expected_action=action,
                        current_state=block_state_summary(block_map.get(block_id)),
                        problem_type="style_not_applied",
                        severity=annotation_severity(annotation[FORMAT_INTENSITY_FIELD]),
                        evidence=f"Matched excerpt still needs `{action}` styling in Feishu.",
                        repair="Apply the missing inline emphasis at the matched location and rerun preview.",
                        auto_fixable=True,
                    )
                )
            else:
                satisfied_annotations += 1
            continue
        if action in LIST_ACTIONS:
            if not block_id or block_id not in states:
                unmatched_annotations.append(annotation)
                pending_annotations.append(
                    build_audit_issue(
                        location=annotation[FORMAT_LOCATION_FIELD],
                        expected_action=action,
                        current_state="missing_block",
                        problem_type="target_not_found",
                        severity=annotation_severity(annotation[FORMAT_INTENSITY_FIELD]),
                        evidence="Expected list or quote block is no longer stably matched in the document.",
                        repair="Check whether this paragraph was split or merged after import.",
                        auto_fixable=False,
                    )
                )
            else:
                child_info = child_indexes.get(block_id)
                parent_block_type = child_info[2] if child_info else None
                if parent_block_type in expected_list_block_type(action):
                    satisfied_annotations += 1
                    continue
                if states[block_id].block_type in expected_list_block_type(action):
                    satisfied_annotations += 1
                    continue
                matched_annotations += 1
                replacement_key = (block_id, action)
                replacement_proposal = None
                if replacement_key not in seen_list_replace_keys:
                    replacement_proposal = build_list_block_replacement_proposal(
                        action,
                        block_id,
                        annotation[FORMAT_LOCATION_FIELD],
                        block_map,
                        states,
                        child_indexes,
                    )
                if replacement_proposal:
                    seen_list_replace_keys.add(replacement_key)
                    list_replace_proposals.append(replacement_proposal)
                pending_annotations.append(
                    build_audit_issue(
                        location=annotation[FORMAT_LOCATION_FIELD],
                        expected_action=action,
                        current_state=block_state_summary(block_map.get(block_id)),
                        problem_type="block_type_mismatch",
                        severity=annotation_severity(annotation[FORMAT_INTENSITY_FIELD]),
                        evidence="The matched block is still plain text instead of the expected list or quote block.",
                        repair=(
                            "Replace the plain text block with the expected Feishu list/quote block at the same position."
                            if replacement_proposal
                            else "Current script records this for review; block-type conversion may still need manual follow-up."
                        ),
                        auto_fixable=bool(replacement_proposal),
                    )
                )
            continue

    replace_block_sources = {
        str((proposal.meta or {}).get("source_block_id"))
        for proposal in list_replace_proposals
        if (proposal.meta or {}).get("source_block_id")
    }
    proposals = build_text_update_proposals(states, excluded_block_ids=replace_block_sources)
    proposals.extend(list_replace_proposals)
    table_proposals, table_issues, table_notes, satisfied_table_locations = build_table_candidate_proposals(
        page_id,
        block_map,
        contexts,
        table_specs,
    )
    blank_delete_proposals = build_blank_delete_proposals(blank_blocks, blocks)
    proposals.extend(table_proposals)
    proposals.extend(blank_delete_proposals)
    pending_annotations.extend(table_issues)
    pending_annotations.extend(build_blank_spacing_issues(blank_delete_proposals))

    table_issue_locations = {issue[AUDIT_LOCATION_FIELD] for issue in table_issues}
    auto_fixable_table_locations = {
        issue[AUDIT_LOCATION_FIELD] for issue in table_issues if issue[AUDIT_AUTO_FIX_FIELD] == AUDIT_AUTO_FIX_TRUE
    }
    for annotation in table_annotations:
        location = annotation[FORMAT_LOCATION_FIELD]
        if location in satisfied_table_locations:
            satisfied_annotations += 1
        elif location in auto_fixable_table_locations:
            matched_annotations += 1
        elif location in table_issue_locations:
            unmatched_annotations.append(annotation)
        else:
            unmatched_annotations.append(annotation)

    action_counter: Counter[str] = Counter()
    for proposal in proposals:
        action_counter.update(proposal.actions)
    return {
        "document_id": document_id,
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "scanned_blocks": len(blocks),
        "editable_blocks": sum(1 for block in blocks if block.get("block_type") in EDITABLE_BLOCK_TYPES),
        "candidate_updates": len(proposals),
        "annotation_count": len(annotations),
        "matched_annotations": matched_annotations,
        "satisfied_annotations": satisfied_annotations,
        "unmatched_annotations": unmatched_annotations,
        "pending_annotations": pending_annotations,
        "action_counts": dict(action_counter),
        "skip_counts": dict(skip_reasons),
        "table_notes": table_notes,
        "candidates": [
            {
                "proposal_type": proposal.proposal_type,
                "block_id": proposal.block_id,
                "block_type": proposal.block_type,
                "block_type_name": BLOCK_TYPE_NAMES.get(proposal.block_type, str(proposal.block_type)),
                "actions": proposal.actions,
                "before": proposal.before,
                "after": proposal.after,
                "meta": proposal.meta or {},
            }
            for proposal in proposals
        ],
        "proposals": proposals,
    }


def strip_proposals(report: dict[str, Any]) -> dict[str, Any]:
    serializable = dict(report)
    serializable.pop("proposals", None)
    return serializable


def default_backup_dir() -> Path:
    return Path(__file__).resolve().parents[1] / "backups"


def write_backup(
    backup_root: Path,
    document_id: str,
    raw_content: str,
    blocks: list[dict[str, Any]],
    report: dict[str, Any],
    annotations: list[dict[str, str]],
) -> Path:
    stamp = datetime.now().astimezone().strftime("%Y%m%d-%H%M%S")
    backup_dir = ensure_directory(backup_root / f"{document_id}-{stamp}")
    (backup_dir / "raw_content.txt").write_text(raw_content, encoding="utf-8")
    write_json(backup_dir / "blocks.json", blocks)
    write_json(backup_dir / "preview-report.json", report)
    write_json(backup_dir / "annotations.json", annotations)
    write_json(
        backup_dir / "meta.json",
        {"document_id": document_id, "created_at": datetime.now().astimezone().isoformat()},
    )
    return backup_dir


def chunked(items: list[Any], size: int) -> list[list[Any]]:
    return [items[index : index + size] for index in range(0, len(items), size)]


def print_report(report: dict[str, Any]) -> None:
    print(f"Document: {report['document_id']}")
    print(f"Scanned blocks: {report['scanned_blocks']}")
    print(f"Editable blocks: {report['editable_blocks']}")
    print(f"Candidate updates: {report['candidate_updates']}")
    print(f"Annotations: {report['annotation_count']}")
    print(f"Matched annotations: {report['matched_annotations']}")
    print(f"Unmatched annotations: {len(report['unmatched_annotations'])}")
    print(f"Pending audit issues: {len(report.get('pending_annotations', []))}")
    if report["action_counts"]:
        print("Action counts:")
        for action, count in sorted(report["action_counts"].items()):
            print(f"  - {action}: {count}")
    if report["skip_counts"]:
        print("Skipped blocks:")
        for reason, count in sorted(report["skip_counts"].items()):
            print(f"  - {reason}: {count}")
    if report["table_notes"]:
        print("Table notes:")
        for note in report["table_notes"]:
            print(f"  - {note}")
    if report["candidates"]:
        print("Candidates:")
        for candidate in report["candidates"][:30]:
            print(
                "  - "
                + f"{candidate['proposal_type']} {candidate['block_type_name']} {candidate['block_id']}: "
                + ", ".join(candidate["actions"])
            )
            print(f"    before: {candidate['before']}")
            print(f"    after : {candidate['after']}")
        if len(report["candidates"]) > 30:
            print(f"  ... {len(report['candidates']) - 30} more candidate blocks omitted")


def build_cell_text_elements(cell_text: str) -> list[dict[str, Any]]:
    plain_text = markdown_inline_to_plain_text(cell_text)
    if not plain_text:
        return [{"text_run": {"content": ""}}]
    return split_text_run_markdown(plain_text, None) or [{"text_run": {"content": plain_text}}]


def build_descendant_table_payload(rows: list[list[str]]) -> tuple[list[str], list[dict[str, Any]], str]:
    row_count = len(rows)
    column_count = max((len(row) for row in rows), default=0)
    if row_count <= 0 or column_count <= 0:
        raise FeishuAPIError("Cannot create a Feishu table with zero rows or zero columns.")

    normalized_rows = [row + [""] * (column_count - len(row)) for row in rows]
    table_temp_id = f"table_{uuid.uuid4().hex[:12]}"
    cell_ids: list[str] = []
    descendants: list[dict[str, Any]] = [
        {
            "block_id": table_temp_id,
            "block_type": 31,
            "table": {"property": {"row_size": row_count, "column_size": column_count}},
            "children": cell_ids,
        }
    ]

    for row_index, row in enumerate(normalized_rows):
        for column_index, cell_text in enumerate(row):
            cell_temp_id = f"{table_temp_id}_cell_{row_index}_{column_index}"
            text_temp_id = f"{cell_temp_id}_text"
            cell_ids.append(cell_temp_id)
            descendants.append(
                {
                    "block_id": cell_temp_id,
                    "block_type": 32,
                    "table_cell": {},
                    "children": [text_temp_id],
                }
            )
            descendants.append(
                {
                    "block_id": text_temp_id,
                    "block_type": 2,
                    "text": {"elements": build_cell_text_elements(cell_text)},
                    "children": [],
                }
            )

    return [table_temp_id], descendants, table_temp_id


def create_native_table(
    client: FeishuDocxClient,
    document_id: str,
    access_token: str,
    parent_id: str,
    index: int,
    rows: list[list[str]],
) -> dict[str, Any]:
    row_count = len(rows)
    column_count = max((len(row) for row in rows), default=0)
    children_id, descendants, table_temp_id = build_descendant_table_payload(rows)
    result = client.create_descendant_blocks(
        document_id,
        parent_id,
        access_token,
        children_id,
        descendants,
        index=index,
    )
    data = result.get("data", result)
    relations = {
        relation.get("temporary_block_id"): relation.get("block_id")
        for relation in data.get("block_id_relations", [])
    }
    table_block_id = relations.get(table_temp_id)
    if not table_block_id:
        raise FeishuAPIError("Feishu descendant create response did not return the created table block ID.")
    return {
        "table_block_id": table_block_id,
        "row_count": row_count,
        "column_count": column_count,
        "cell_count": row_count * column_count,
        "inserted_top_level_blocks": len(children_id),
    }


def apply_report(
    client: FeishuDocxClient,
    document_id: str,
    access_token: str,
    report: dict[str, Any],
    backup_dir: Path,
) -> list[dict[str, Any]]:
    proposals: list[Proposal] = report["proposals"]
    update_requests = [proposal.request for proposal in proposals if proposal.request]
    apply_results: list[dict[str, Any]] = []
    for batch in chunked(update_requests, DEFAULT_BATCH_SIZE):
        result = client.batch_update_blocks(document_id, access_token, batch)
        apply_results.append(
            {
                "type": "update_text_elements",
                "updated_blocks": len(batch),
                "document_revision_id": result.get("data", result).get("document_revision_id"),
                "client_token": result.get("data", result).get("client_token"),
            }
        )
        time.sleep(0.4)
    structural_proposals = [
        proposal
        for proposal in proposals
        if proposal.proposal_type in {"delete_children", "replace_pipe_table", "replace_block_type"}
    ]
    structural_proposals.sort(
        key=lambda proposal: (
            proposal.block_id or "",
            -int((proposal.meta or {})["start_index"]),
            -int((proposal.meta or {})["end_index"]),
        )
    )
    for proposal in structural_proposals:
        meta = proposal.meta or {}
        parent_id = proposal.block_id or ""
        start_index = int(meta["start_index"])
        end_index = int(meta["end_index"])
        if proposal.proposal_type == "delete_children":
            result = client.batch_delete_children(
                document_id,
                parent_id,
                access_token,
                start_index,
                end_index,
            )
            apply_results.append(
                {
                    "type": "delete_children",
                    "parent_id": parent_id,
                    "start_index": start_index,
                    "end_index": end_index,
                    "document_revision_id": result.get("data", result).get("document_revision_id"),
                }
            )
            time.sleep(0.2)
            continue

        if proposal.proposal_type == "replace_pipe_table":
            create_result = create_native_table(
                client,
                document_id,
                access_token,
                parent_id,
                start_index,
                meta.get("rows", []),
            )
            inserted_top_level_blocks = int(create_result.get("inserted_top_level_blocks", 1))
            shifted_start = start_index + inserted_top_level_blocks
            shifted_end = end_index + inserted_top_level_blocks
            try:
                delete_result = client.batch_delete_children(
                    document_id,
                    parent_id,
                    access_token,
                    shifted_start,
                    shifted_end,
                )
            except FeishuAPIError as exc:
                rollback_error = None
                try:
                    client.batch_delete_children(
                        document_id,
                        parent_id,
                        access_token,
                        start_index,
                        start_index + inserted_top_level_blocks,
                    )
                except FeishuAPIError as rollback_exc:
                    rollback_error = str(rollback_exc)
                failure_details = {
                    "type": "replace_pipe_table_failed",
                    "parent_id": parent_id,
                    "location": meta.get("location"),
                    "start_index": start_index,
                    "end_index": end_index,
                    "table_block_id": create_result["table_block_id"],
                    "source_lines": meta.get("source_lines", []),
                    "error": str(exc),
                }
                if rollback_error:
                    failure_details["rollback_error"] = rollback_error
                apply_results.append(failure_details)
                if rollback_error:
                    raise FeishuAPIError(
                        f"replace_pipe_table failed and rollback also failed at {meta.get('location')}: "
                        f"{exc} | rollback: {rollback_error}"
                    ) from exc
                raise FeishuAPIError(
                    f"replace_pipe_table failed after creating a new table at {meta.get('location')}; "
                    "the inserted table was rolled back to preserve the original content."
                ) from exc
            apply_results.append(
                {
                    "type": "replace_pipe_table",
                    "parent_id": parent_id,
                    "location": meta.get("location"),
                    "start_index": start_index,
                    "end_index": end_index,
                    "deleted_start_index": shifted_start,
                    "deleted_end_index": shifted_end,
                    "deleted_revision_id": delete_result.get("data", delete_result).get(
                        "document_revision_id"
                    ),
                    "table_block_id": create_result["table_block_id"],
                    "row_count": create_result["row_count"],
                    "column_count": create_result["column_count"],
                    "source_lines": meta.get("source_lines", []),
                }
            )
            time.sleep(0.3)
            continue

        if proposal.proposal_type == "replace_block_type":
            target_block_type = int(meta["target_block_type"])
            target_field_name = str(meta["target_field_name"])
            create_result = client.create_child_blocks(
                document_id,
                parent_id,
                access_token,
                [
                    {
                        "block_type": target_block_type,
                        target_field_name: {"elements": meta.get("elements", [])},
                    }
                ],
                index=start_index,
            )
            data = create_result.get("data", create_result)
            created_children = data.get("children", [])
            created_block_id = created_children[0].get("block_id") if created_children else None
            shifted_start = start_index + 1
            shifted_end = end_index + 1
            try:
                delete_result = client.batch_delete_children(
                    document_id,
                    parent_id,
                    access_token,
                    shifted_start,
                    shifted_end,
                )
            except FeishuAPIError as exc:
                rollback_error = None
                try:
                    client.batch_delete_children(
                        document_id,
                        parent_id,
                        access_token,
                        start_index,
                        start_index + 1,
                    )
                except FeishuAPIError as rollback_exc:
                    rollback_error = str(rollback_exc)
                failure_details = {
                    "type": "replace_block_type_failed",
                    "parent_id": parent_id,
                    "location": meta.get("location"),
                    "source_block_id": meta.get("source_block_id"),
                    "target_block_type": target_block_type,
                    "error": str(exc),
                }
                if rollback_error:
                    failure_details["rollback_error"] = rollback_error
                apply_results.append(failure_details)
                if rollback_error:
                    raise FeishuAPIError(
                        f"replace_block_type failed and rollback also failed at {meta.get('location')}: "
                        f"{exc} | rollback: {rollback_error}"
                    ) from exc
                raise FeishuAPIError(
                    f"replace_block_type failed after creating a new block at {meta.get('location')}; "
                    "the inserted block was rolled back to preserve the original content."
                ) from exc
            apply_results.append(
                {
                    "type": "replace_block_type",
                    "parent_id": parent_id,
                    "location": meta.get("location"),
                    "source_block_id": meta.get("source_block_id"),
                    "target_block_type": target_block_type,
                    "target_field_name": target_field_name,
                    "new_block_id": created_block_id,
                    "deleted_revision_id": delete_result.get("data", delete_result).get(
                        "document_revision_id"
                    ),
                }
            )
            time.sleep(0.2)
    write_json(backup_dir / "apply-result.json", apply_results)
    return apply_results


def load_blocks_and_raw_content(
    args: argparse.Namespace,
    document_id: str,
) -> tuple[list[dict[str, Any]], str, str | None, FeishuDocxClient | None]:
    if args.blocks_json:
        blocks_path = Path(args.blocks_json).expanduser().resolve()
        blocks = json.loads(blocks_path.read_text(encoding="utf-8"))
        raw_content = ""
        if args.raw_content_file:
            raw_content = Path(args.raw_content_file).expanduser().resolve().read_text(encoding="utf-8")
        return blocks, raw_content, None, None
    app_id, app_secret = require_credentials()
    client = FeishuDocxClient(app_id, app_secret)
    access_token = client.get_tenant_access_token()
    raw_content = client.get_raw_content(document_id, access_token)
    blocks = client.list_blocks(document_id, access_token)
    return blocks, raw_content, access_token, client


def configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def resolve_archive_note_path(
    note_path: Path | None,
    annotations_json_path: Path | None,
) -> Path | None:
    if note_path:
        return note_path
    if annotations_json_path:
        return infer_note_path_from_annotations(annotations_json_path)
    return None


def write_report_payload(report_payload: dict[str, Any], report_file: str | None) -> None:
    if not report_file:
        return
    report_path = Path(report_file).expanduser().resolve()
    ensure_directory(report_path.parent)
    write_json(report_path, report_payload)
    print(f"Report written to: {report_path}")


def main() -> int:
    configure_stdio()
    args = parse_args()

    note_path = Path(args.note_file).expanduser().resolve() if args.note_file else None
    annotations_json_path = (
        Path(args.annotations_json).expanduser().resolve() if args.annotations_json else None
    )
    annotations: list[dict[str, str]]
    if annotations_json_path:
        annotations = read_annotations(annotations_json_path)
    else:
        if not note_path:
            raise SystemExit("Either --note-file or --annotations-json is required.")
        annotations = generate_annotation_entries(note_path)
        annotation_md = Path(args.annotations_md).expanduser().resolve() if args.annotations_md else None
        annotation_json = None
        written_md, written_json = write_annotation_artifacts(
            note_path,
            annotations,
            markdown_path=annotation_md,
            json_path=annotation_json,
        )
        print(f"Annotation Markdown written to: {written_md}")
        print(f"Annotation JSON written to: {written_json}")

    archive_note_path = resolve_archive_note_path(note_path, annotations_json_path)
    table_specs = build_note_table_specs(note_path, annotations)

    if args.mode == "annotate":
        return 0

    document_id = resolve_document_id(args.doc_url, args.doc_token, args.blocks_json)
    blocks, raw_content, access_token, client = load_blocks_and_raw_content(args, document_id)
    report = analyze_blocks(
        document_id,
        blocks,
        annotations,
        enable_color=args.enable_color,
        table_specs=table_specs,
    )
    print_report(report)
    report_payload = strip_proposals(report)
    write_report_payload(report_payload, args.report_file)

    if args.mode == "preview":
        return 0
    if args.mode == "audit":
        if not archive_note_path:
            raise SystemExit("Audit mode requires --note-file or --annotations-json to infer audit output paths.")
        audit_md = Path(args.audit_md).expanduser().resolve() if args.audit_md else None
        audit_json = Path(args.audit_json).expanduser().resolve() if args.audit_json else None
        written_md, written_json = write_audit_artifacts(
            archive_note_path,
            report.get("pending_annotations", []),
            markdown_path=audit_md,
            json_path=audit_json,
        )
        print(f"Audit Markdown written to: {written_md}")
        print(f"Audit JSON written to: {written_json}")
        return 0
    if args.blocks_json:
        raise SystemExit(f"{args.mode} mode cannot run with --blocks-json; use live Feishu credentials.")
    if not client or not access_token:
        raise SystemExit(f"{args.mode} mode requires live Feishu credentials.")

    backup_root = Path(args.backup_dir).expanduser().resolve() if args.backup_dir else default_backup_dir()
    if args.mode == "apply":
        if not report["candidates"]:
            print("No safe finalization updates were detected; nothing was written.")
            return 0
        backup_dir = write_backup(backup_root, document_id, raw_content, blocks, report_payload, annotations)
        print(f"Backup created at: {backup_dir}")
        results = apply_report(client, document_id, access_token, report, backup_dir)
        print(f"Applied {len(results)} Feishu finalization operations.")
        return 0

    backup_dir: Path | None = None
    current_report = report
    current_blocks = blocks
    current_raw_content = raw_content
    final_round = 0
    while True:
        auto_fixable_issues = [
            issue
            for issue in current_report.get("pending_annotations", [])
            if issue.get(AUDIT_AUTO_FIX_FIELD) == AUDIT_AUTO_FIX_TRUE
        ]
        if not current_report["candidates"] or not auto_fixable_issues:
            break
        if final_round >= DEFAULT_FINALIZE_ROUNDS:
            break
        if backup_dir is None:
            backup_dir = write_backup(
                backup_root,
                document_id,
                current_raw_content,
                current_blocks,
                strip_proposals(current_report),
                annotations,
            )
            print(f"Backup created at: {backup_dir}")
        results = apply_report(client, document_id, access_token, current_report, backup_dir)
        print(f"Finalize round {final_round + 1}: applied {len(results)} operations.")
        final_round += 1
        current_blocks, current_raw_content, access_token, client = load_blocks_and_raw_content(
            args,
            document_id,
        )
        if not client or not access_token:
            raise SystemExit("Finalize mode requires live Feishu credentials after apply.")
        current_report = analyze_blocks(
            document_id,
            current_blocks,
            annotations,
            enable_color=args.enable_color,
            table_specs=table_specs,
        )
        print_report(current_report)

    final_report_payload = strip_proposals(current_report)
    write_report_payload(final_report_payload, args.report_file)
    if archive_note_path:
        audit_md = Path(args.audit_md).expanduser().resolve() if args.audit_md else None
        audit_json = Path(args.audit_json).expanduser().resolve() if args.audit_json else None
        written_md, written_json = write_audit_artifacts(
            archive_note_path,
            current_report.get("pending_annotations", []),
            markdown_path=audit_md,
            json_path=audit_json,
        )
        print(f"Audit Markdown written to: {written_md}")
        print(f"Audit JSON written to: {written_json}")

    residual_auto_fixable = [
        issue
        for issue in current_report.get("pending_annotations", [])
        if issue.get(AUDIT_AUTO_FIX_FIELD) == AUDIT_AUTO_FIX_TRUE
    ]
    if residual_auto_fixable:
        print(
            f"Finalize stopped with {len(residual_auto_fixable)} auto-fixable audit issues still pending after {final_round} rounds."
        )
        return 1
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except FeishuAPIError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
