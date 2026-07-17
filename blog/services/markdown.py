from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from typing import Any

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.footnote import footnote_plugin
from mdit_py_plugins.tasklists import tasklists_plugin


@dataclass(frozen=True)
class TocItem:
    """文章目录中的一项。"""

    id: str
    text: str
    level: int


@dataclass(frozen=True)
class MarkdownResult:
    """Markdown 渲染结果。"""

    html: str
    toc: list[TocItem]


def create_markdown_parser() -> MarkdownIt:
    """
    创建博客使用的 Markdown 解析器。

    html=False：
    不允许正文中的原始 HTML 被直接输出。

    linkify=False：
    暂时不自动识别裸链接，减少不可控行为。
    """

    parser = MarkdownIt(
        "commonmark",
        {
            "html": False,
            "linkify": False,
            "typographer": True,
            "breaks": False,
        },
    )

    parser.enable("table")
    parser.enable("strikethrough")

    parser.use(footnote_plugin)

    parser.use(
        tasklists_plugin,
        enabled=True,
        label=True,
        label_after=True,
    )

    return parser


def render_markdown(source: str) -> MarkdownResult:
    """
    将 Markdown 渲染为 HTML，同时生成二、三级标题目录。
    """

    parser = create_markdown_parser()
    environment: dict[str, Any] = {}

    tokens = parser.parse(source or "", environment)

    toc = _add_heading_ids(tokens)

    html = parser.renderer.render(
        tokens,
        parser.options,
        environment,
    )

    return MarkdownResult(
        html=html,
        toc=toc,
    )


def _add_heading_ids(tokens: list[Token]) -> list[TocItem]:
    """
    为 h2/h3 添加稳定且不重复的 id，并提取目录。
    """

    toc: list[TocItem] = []
    used_ids: dict[str, int] = {}

    for index, token in enumerate(tokens):
        if token.type != "heading_open":
            continue

        try:
            level = int(token.tag.removeprefix("h"))
        except ValueError:
            continue

        if level not in {2, 3}:
            continue

        if index + 1 >= len(tokens):
            continue

        inline_token = tokens[index + 1]

        if inline_token.type != "inline":
            continue

        heading_text = _plain_inline_text(inline_token).strip()

        if not heading_text:
            continue

        base_id = _slugify_heading(heading_text)
        occurrence = used_ids.get(base_id, 0)

        used_ids[base_id] = occurrence + 1

        heading_id = (
            base_id
            if occurrence == 0
            else f"{base_id}-{occurrence + 1}"
        )

        token.attrSet("id", heading_id)

        toc.append(
            TocItem(
                id=heading_id,
                text=heading_text,
                level=level,
            )
        )

    return toc


def _plain_inline_text(token: Token) -> str:
    """
    从标题的 inline token 中提取纯文本。
    """

    if not token.children:
        return token.content

    parts: list[str] = []

    for child in token.children:
        if child.type in {
            "text",
            "code_inline",
            "math_inline",
        }:
            parts.append(child.content)

        elif child.type in {
            "softbreak",
            "hardbreak",
        }:
            parts.append(" ")

        elif child.type == "image":
            parts.append(child.content)

    return "".join(parts)


def _slugify_heading(text: str) -> str:
    """
    生成标题锚点。

    英文标题尽量保留可读 slug；
    中文或无法生成 slug 时使用短哈希，保证稳定。
    """

    normalized = text.strip().lower()

    ascii_slug = re.sub(
        r"[^a-z0-9]+",
        "-",
        normalized,
    ).strip("-")

    if ascii_slug:
        digest = hashlib.sha1(
            text.encode("utf-8"),
        ).hexdigest()[:6]

        return f"{ascii_slug}-{digest}"

    digest = hashlib.sha1(
        text.encode("utf-8"),
    ).hexdigest()[:10]

    return f"section-{digest}"