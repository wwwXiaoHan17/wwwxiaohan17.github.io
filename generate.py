#!/usr/bin/env python3
"""Documentation generator for pyera — creates trilingual HTML docs."""

from __future__ import annotations

import ast
import inspect
import json
import os
import re
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

BASE = Path(__file__).parent
SRC = BASE.parent / "pyera"


# ---------------------------------------------------------------------------
# Translation dictionary
# ---------------------------------------------------------------------------

I18N = {
    "zh": {
        "home": "首页",
        "getting_started": "快速开始",
        "api_reference": "API 参考",
        "examples": "示例",
        "parameters": "参数",
        "returns": "返回值",
        "raises": "抛出异常",
        "see_also": "参见",
        "example": "示例",
        "module": "模块",
        "function": "函数",
        "class": "类",
        "type": "类型",
        "default": "默认值",
        "description": "说明",
        "copy": "复制",
        "search_hint": "Ctrl+K 搜索",
        "nav_guide": "指南",
        "nav_api": "API 文档",
        "nav_examples": "示例",
        "footer": "Pyera 文档 — 基于 MIT 协议开源",
        "quick_install": "快速安装",
        "features": "特性",
        "modules": "模块概览",
        "read_more": "查看更多 →",
    },
    "en": {
        "home": "Home",
        "getting_started": "Getting Started",
        "api_reference": "API Reference",
        "examples": "Examples",
        "parameters": "Parameters",
        "returns": "Returns",
        "raises": "Raises",
        "see_also": "See Also",
        "example": "Example",
        "module": "Module",
        "function": "Function",
        "class": "Class",
        "type": "Type",
        "default": "Default",
        "description": "Description",
        "copy": "Copy",
        "search_hint": "Ctrl+K Search",
        "nav_guide": "Guides",
        "nav_api": "API Docs",
        "nav_examples": "Examples",
        "footer": "Pyera Docs — Open source under MIT License",
        "quick_install": "Quick Install",
        "features": "Features",
        "modules": "Module Overview",
        "read_more": "Read more →",
    },
    "ja": {
        "home": "ホーム",
        "getting_started": "クイックスタート",
        "api_reference": "API リファレンス",
        "examples": "サンプル",
        "parameters": "パラメータ",
        "returns": "戻り値",
        "raises": "例外",
        "see_also": "関連項目",
        "example": "使用例",
        "module": "モジュール",
        "function": "関数",
        "class": "クラス",
        "type": "型",
        "default": "デフォルト",
        "description": "説明",
        "copy": "コピー",
        "search_hint": "Ctrl+K で検索",
        "nav_guide": "ガイド",
        "nav_api": "API ドキュメント",
        "nav_examples": "サンプル",
        "footer": "Pyera ドキュメント — MIT ライセンスで公開",
        "quick_install": "クイックインストール",
        "features": "特徴",
        "modules": "モジュール一覧",
        "read_more": "詳細を見る →",
    },
}


# ---------------------------------------------------------------------------
# Module metadata
# ---------------------------------------------------------------------------

MODULE_META = {
    "_display": {
        "zh": {"title": "显示 / 输出", "desc": "PRINT、DRAWLINE、SETCOLOR 等显示控制指令"},
        "en": {"title": "Display / Output", "desc": "PRINT, DRAWLINE, SETCOLOR and other display commands"},
        "ja": {"title": "表示 / 出力", "desc": "PRINT、DRAWLINE、SETCOLOR などの表示制御命令"},
    },
    "_input": {
        "zh": {"title": "输入", "desc": "INPUT、TINPUT、BINPUT 等输入等待指令"},
        "en": {"title": "Input", "desc": "INPUT, TINPUT, BINPUT and other input commands"},
        "ja": {"title": "入力", "desc": "INPUT、TINPUT、BINPUT などの入力待機命令"},
    },
    "_flow": {
        "zh": {"title": "流程控制", "desc": "BEGIN、CALL、QUIT、JUMP 等流程控制指令"},
        "en": {"title": "Flow Control", "desc": "BEGIN, CALL, QUIT, JUMP and other flow control commands"},
        "ja": {"title": "フロー制御", "desc": "BEGIN、CALL、QUIT、JUMP などのフロー制御命令"},
    },
    "_chara_ops": {
        "zh": {"title": "角色操作", "desc": "ADDCHARA、DELCHARA、SWAPCHARA 等角色操作指令"},
        "en": {"title": "Character Operations", "desc": "ADDCHARA, DELCHARA, SWAPCHARA and other character commands"},
        "ja": {"title": "キャラクター操作", "desc": "ADDCHARA、DELCHARA、SWAPCHARA などのキャラクター操作命令"},
    },
    "_array_ops": {
        "zh": {"title": "数组操作", "desc": "VARSET、ARRAYCOPY、ARRAYSORT、SETBIT 等数组指令"},
        "en": {"title": "Array Operations", "desc": "VARSET, ARRAYCOPY, ARRAYSORT, SETBIT and other array commands"},
        "ja": {"title": "配列操作", "desc": "VARSET、ARRAYCOPY、ARRAYSORT、SETBIT などの配列命令"},
    },
    "_csv_ops": {
        "zh": {"title": "CSV 数据", "desc": "CSV 角色模板数据查询指令"},
        "en": {"title": "CSV Data", "desc": "CSV character template data query commands"},
        "ja": {"title": "CSV データ", "desc": "CSV キャラクターテンプレートデータクエリ命令"},
    },
    "_save_load": {
        "zh": {"title": "存档 / 读档", "desc": "SAVEGAME、LOADGAME、SAVEDATA 等存档指令"},
        "en": {"title": "Save / Load", "desc": "SAVEGAME, LOADGAME, SAVEDATA and other save commands"},
        "ja": {"title": "セーブ / ロード", "desc": "SAVEGAME、LOADGAME、SAVEDATA などのセーブ命令"},
    },
    "_builtin": {
        "zh": {"title": "内置函数", "desc": "MAX、MIN、LIMIT、MATCH、RAND 等数学与字符串函数"},
        "en": {"title": "Built-in Functions", "desc": "MAX, MIN, LIMIT, MATCH, RAND and other math/string functions"},
        "ja": {"title": "組み込み関数", "desc": "MAX、MIN、LIMIT、MATCH、RAND などの数学・文字列関数"},
    },
    "_sound": {
        "zh": {"title": "音效 / BGM", "desc": "PLAYSOUND、PLAYBGM、音量控制等音频指令"},
        "en": {"title": "Sound / BGM", "desc": "PLAYSOUND, PLAYBGM, volume control and other audio commands"},
        "ja": {"title": "効果音 / BGM", "desc": "PLAYSOUND、PLAYBGM、音量制御などの音声命令"},
    },
    "vars": {
        "zh": {"title": "变量代理", "desc": "FLAG、MONEY、DAY 等全局变量的字典式访问"},
        "en": {"title": "Variable Proxies", "desc": "Dict-style access to FLAG, MONEY, DAY and other global variables"},
        "ja": {"title": "変数プロキシ", "desc": "FLAG、MONEY、DAY などのグローバル変数への辞書式アクセス"},
    },
    "chara": {
        "zh": {"title": "角色类", "desc": "Chara 类封装单个角色的所有变量访问"},
        "en": {"title": "Chara Class", "desc": "Chara class encapsulates all variable access for a single character"},
        "ja": {"title": "キャラクタークラス", "desc": "Chara クラスは単一キャラクターの全変数アクセスをカプセル化"},
    },
    "_async_utils": {
        "zh": {"title": "异步工具", "desc": "asyncio 集成与主线程安全调用工具"},
        "en": {"title": "Async Utilities", "desc": "asyncio integration and main-thread safe calling tools"},
        "ja": {"title": "非同期ユーティリティ", "desc": "asyncio 統合とメインスレッド安全呼び出しツール"},
    },
    "_events": {
        "zh": {"title": "事件注册", "desc": "@event 装饰器与事件注册系统"},
        "en": {"title": "Event Registration", "desc": "@event decorator and event registration system"},
        "ja": {"title": "イベント登録", "desc": "@event デコレータとイベント登録システム"},
    },
    "_logging": {
        "zh": {"title": "日志系统", "desc": "调试日志记录与缓冲区管理"},
        "en": {"title": "Logging", "desc": "Debug logging and buffer management"},
        "ja": {"title": "ログシステム", "desc": "デバッグログ記録とバッファ管理"},
    },
    "types": {
        "zh": {"title": "类型定义", "desc": "枚举、常量和颜色解析工具"},
        "en": {"title": "Type Definitions", "desc": "Enums, constants and color parsing utilities"},
        "ja": {"title": "型定義", "desc": "列挙型、定数、色解析ユーティリティ"},
    },
    "utils": {
        "zh": {"title": "工具函数", "desc": "纯 Python 实现的辅助函数集合"},
        "en": {"title": "Utilities", "desc": "Pure-Python helper functions"},
        "ja": {"title": "ユーティリティ", "desc": "純粋な Python 実装のヘルパー関数群"},
    },
    "exceptions": {
        "zh": {"title": "异常", "desc": "Pyera 异常体系"},
        "en": {"title": "Exceptions", "desc": "Pyera exception hierarchy"},
        "ja": {"title": "例外", "desc": "Pyera 例外階層"},
    },
    "core": {
        "zh": {"title": "核心桥接", "desc": "Python ↔ C# 引擎桥接层"},
        "en": {"title": "Core Bridge", "desc": "Python ↔ C# engine bridge layer"},
        "ja": {"title": "コアブリッジ", "desc": "Python ↔ C# エンジンブリッジ層"},
    },
}


NAV_ORDER = [
    ("_display", "display.html"),
    ("_input", "input.html"),
    ("_flow", "flow.html"),
    ("_chara_ops", "chara-ops.html"),
    ("_array_ops", "array-ops.html"),
    ("_csv_ops", "csv.html"),
    ("_save_load", "save-load.html"),
    ("_builtin", "builtin.html"),
    ("_sound", "sound.html"),
    ("vars", "vars.html"),
    ("chara", "chara-class.html"),
    ("_async_utils", "async.html"),
    ("_events", "events.html"),
    ("_logging", "logging.html"),
    ("types", "types.html"),
    ("utils", "utils.html"),
    ("exceptions", "exceptions.html"),
    ("core", "core.html"),
]


# ---------------------------------------------------------------------------
# HTML skeleton
# ---------------------------------------------------------------------------

HTML_HEAD = '''<!DOCTYPE html>
<html lang="zh" data-theme="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<link rel="stylesheet" href="{css_path}css/style.css">
</head>
<body>
<div class="layout">
<aside class="sidebar" id="sidebar">
  <div class="sidebar-header">
    <a href="{root}index.html">Pyera</a>
    <div class="version">v0.3.0</div>
  </div>
  <nav class="sidebar-nav">
    <div class="nav-section">
      <div class="nav-section-title">{nav_guide}</div>
      <a class="nav-link" href="{root}index.html" data-key="index">{home}</a>
      <a class="nav-link" href="{root}getting-started.html" data-key="getting-started">{getting_started}</a>
    </div>
    <div class="nav-section">
      <div class="nav-section-title">{nav_api}</div>
{api_links}
    </div>
    <div class="nav-section">
      <div class="nav-section-title">{nav_examples}</div>
      <a class="nav-link" href="{root}examples/basic-game.html" data-key="ex-basic">Basic Game</a>
      <a class="nav-link" href="{root}examples/async-integration.html" data-key="ex-async">Async</a>
    </div>
  </nav>
</aside>
<main class="main">
  <div class="topbar">
    <div class="topbar-left">
      <button class="mobile-toggle">☰</button>
      <div class="breadcrumb">{breadcrumb}</div>
    </div>
    <div class="topbar-right">
      <div class="search-wrapper">
        <svg class="search-icon" width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M7.333 12.667A5.333 5.333 0 1 0 7.333 2a5.333 5.333 0 0 0 0 10.667zM14 14l-2.9-2.9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <input class="search-input" type="text" placeholder="Ctrl+K 搜索...">
        <kbd class="search-kbd">Ctrl K</kbd>
      </div>
      <div class="lang-switcher">
        <button class="lang-btn" data-lang="zh">中</button>
        <button class="lang-btn" data-lang="en">En</button>
        <button class="lang-btn" data-lang="ja">日</button>
      </div>
      <button class="theme-toggle">☀</button>
    </div>
  </div>
  <div class="content">
'''

HTML_FOOT = '''  </div>
  <div class="footer">{footer}</div>
</main>
</div>
<script id="search-data" type="application/json">{search_data}</script>
<script src="{js_path}js/lang.js"></script>
</body>
</html>
'''


def make_nav_links(active: str, root: str) -> str:
    lines = []
    for mod, page in NAV_ORDER:
        meta = MODULE_META.get(mod, {})
        zh = meta.get("zh", {}).get("title", mod)
        en = meta.get("en", {}).get("title", mod)
        lines.append(f'      <a class="nav-link" href="{root}api/{page}" data-key="{mod}">{zh}</a>')
    return "\n".join(lines)


def page_skeleton(
    title: str,
    breadcrumb: str,
    body: str,
    active: str = "",
    depth: int = 0,
    search_data: list | None = None,
) -> str:
    root = "../" * depth
    css_path = "../" * depth
    js_path = "../" * depth
    links = make_nav_links(active, root)
    search_json = json.dumps(search_data or [], ensure_ascii=False)

    t = I18N["zh"]
    head = HTML_HEAD.format(
        title=title,
        css_path=css_path,
        js_path=js_path,
        root=root,
        nav_guide=t["nav_guide"],
        nav_api=t["nav_api"],
        nav_examples=t["nav_examples"],
        home=t["home"],
        getting_started=t["getting_started"],
        api_links=links,
        breadcrumb=breadcrumb,
    )
    foot = HTML_FOOT.format(
        footer=t["footer"],
        search_data=search_json,
        js_path=js_path,
    )
    return head + body + foot


# ---------------------------------------------------------------------------
# Parse Python source
# ---------------------------------------------------------------------------

@dataclass
class Param:
    name: str
    type_hint: str = ""
    default: str = ""
    desc: str = ""


@dataclass
class ApiItem:
    kind: str  # "function" | "class"
    name: str
    signature: str
    params: list[Param] = field(default_factory=list)
    doc_zh: str = ""
    doc_en: str = ""
    doc_ja: str = ""
    erb_cmd: str = ""
    returns: str = ""
    raises: list[str] = field(default_factory=list)
    see_also: list[str] = field(default_factory=list)
    examples: list[str] = field(default_factory=list)


def extract_docstring(node) -> str:
    doc = ast.get_docstring(node)
    return doc or ""


def parse_type_annotation(node) -> str:
    if node is None:
        return ""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Constant):
        return repr(node.value)
    if isinstance(node, ast.Attribute):
        return f"{parse_type_annotation(node.value)}.{node.attr}"
    if isinstance(node, ast.Subscript):
        return f"{parse_type_annotation(node.value)}[{parse_type_annotation(node.slice)}]"
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.BitOr):
        return f"{parse_type_annotation(node.left)} | {parse_type_annotation(node.right)}"
    if isinstance(node, ast.Tuple):
        return ", ".join(parse_type_annotation(e) for e in node.elts)
    if isinstance(node, ast.List):
        return "["
        + ", ".join(parse_type_annotation(e) for e in node.elts)
        + "]"
    if isinstance(node, ast.expr):
        return ast.unparse(node)
    return ""


def parse_signature(node: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str, list[Param]]:
    args = node.args
    params = []
    sig_parts = [node.name, "("]

    # Extract parameter descriptions from docstring
    doc = extract_docstring(node)
    param_descs = extract_param_descriptions(doc)

    # positional / positional-only
    all_args = []
    for i, arg in enumerate(args.args):
        default_idx = i - (len(args.args) - len(args.defaults))
        default = ""
        if default_idx >= 0 and args.defaults:
            default = ast.unparse(args.defaults[default_idx])
        hint = parse_type_annotation(arg.annotation)
        desc = param_descs.get(arg.arg, "")
        params.append(Param(arg.arg, hint, default, desc))
        all_args.append((arg.arg, hint, default))

    # kwonly
    for i, arg in enumerate(args.kwonlyargs):
        default = ""
        if i < len(args.kw_defaults) and args.kw_defaults[i]:
            default = ast.unparse(args.kw_defaults[i])
        hint = parse_type_annotation(arg.annotation)
        desc = param_descs.get(arg.arg, "")
        params.append(Param(arg.arg, hint, default, desc))
        all_args.append((arg.arg, hint, default))

    # vararg
    if args.vararg:
        all_args.append((f"*{args.vararg.arg}", "", ""))
        params.append(Param(f"*{args.vararg.arg}", "", ""))

    # kwarg
    if args.kwarg:
        all_args.append((f"**{args.kwarg.arg}", "", ""))
        params.append(Param(f"**{args.kwarg.arg}", "", ""))

    # Build signature string
    parts = []
    for name, hint, default in all_args:
        s = name
        if hint:
            s += f": {hint}"
        if default:
            s += f" = {default}"
        parts.append(s)

    ret = parse_type_annotation(node.returns)
    sig = f"{node.name}({', '.join(parts)})"
    if ret:
        sig += f" -> {ret}"

    return sig, params


def parse_module(path: Path) -> list[ApiItem]:
    text = path.read_text(encoding="utf-8")
    tree = ast.parse(text)
    items = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("_") and not node.name.startswith("__"):
                continue
            if node.name.startswith("__") and node.name != "__init__":
                continue

            sig, params = parse_signature(node)
            doc = extract_docstring(node)

            # Try to find ERB command from docstring
            erb = ""
            m = re.search(r"([A-Z][A-Z_0-9]+)\s*指令", doc)
            if m:
                erb = m.group(1)
            else:
                m = re.search(r"([A-Z][A-Z_0-9]+)\s*命令", doc)
                if m:
                    erb = m.group(1)

            item = ApiItem(
                kind="function",
                name=node.name,
                signature=sig,
                params=params,
                doc_zh=doc,
                erb_cmd=erb,
            )
            items.append(item)

        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("_"):
                continue
            doc = extract_docstring(node)
            item = ApiItem(
                kind="class",
                name=node.name,
                signature=node.name,
                doc_zh=doc,
            )
            items.append(item)

    return items


# ---------------------------------------------------------------------------
# Generate HTML content
# ---------------------------------------------------------------------------

SECTION_TITLES = {
    "Parameters",
    "Returns",
    "Raises",
    "See Also",
    "Examples",
    "Example",
    "Notes",
    "Warnings",
    "Yields",
    "Members",
    "Attributes",
}


def extract_param_descriptions(doc: str) -> dict[str, str]:
    """从 docstring 的 Parameters 部分提取参数描述。

    格式::

        Parameters
        ----------
        text : str
            要输出的文本字符串。
        value : int
            要写入的值。
    """
    result: dict[str, str] = {}
    if not doc:
        return result

    lines = doc.strip().split("\n")
    in_params = False
    current_param = ""
    current_desc: list[str] = []

    for i, line in enumerate(lines):
        stripped = line.strip()
        # Detect Parameters section start
        if stripped == "Parameters":
            in_params = True
            continue
        if in_params and stripped.startswith("-") and set(stripped) <= set("-"):
            continue
        if in_params:
            # Check if we've hit another section
            if stripped in SECTION_TITLES and stripped != "Parameters":
                if current_param and current_desc:
                    result[current_param] = "\n".join(current_desc).strip()
                break

            # Check if this line starts a new parameter definition
            # Format: "name : type" or "name: type" at the start of the line
            param_match = re.match(r"^(\w[\w_]*)\s*:\s*(.+)$", stripped)
            if param_match and (not line.startswith(" ") or line.startswith("    ")):
                # Save previous param if exists
                if current_param and current_desc:
                    result[current_param] = "\n".join(current_desc).strip()
                current_param = param_match.group(1)
                current_desc = []
                continue

            # Check if this is a description line (indented)
            if current_param and (line.startswith(" ") or line.startswith("\t")):
                desc_text = stripped
                if desc_text:
                    current_desc.append(desc_text)

    # Save last param
    if current_param and current_desc:
        result[current_param] = "\n".join(current_desc).strip()

    return result


def escape_html(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def strip_doc_markup(text: str) -> str:
    """Return a short plain-text version of a docstring for search snippets."""
    text = textwrap.dedent(text or "").strip()
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"(?m)^(Parameters|Returns|Raises|See Also|Examples?)\n-+\n.*$", "", text, flags=re.S)
    text = re.sub(r":(?:func|class|meth|mod|attr|data|exc):`([^`]+)`", r"\1", text)
    text = re.sub(r"``([^`]+)``", r"\1", text)
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def render_inline_markup(text: str) -> str:
    """Render the small Markdown/RST inline subset used by pyera docstrings."""
    placeholders: list[str] = []

    def stash(html: str) -> str:
        placeholders.append(html)
        return f"\x00{len(placeholders) - 1}\x00"

    text = re.sub(
        r":(?:func|class|meth|mod|attr|data|exc):`([^`]+)`",
        lambda m: stash(f"<code>{escape_html(m.group(1))}</code>"),
        text,
    )
    text = re.sub(r"``([^`]+)``", lambda m: stash(f"<code>{escape_html(m.group(1))}</code>"), text)
    text = re.sub(r"`([^`]+)`", lambda m: stash(f"<code>{escape_html(m.group(1))}</code>"), text)
    text = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda m: stash(f'<a href="{escape_html(m.group(2))}">{escape_html(m.group(1))}</a>'),
        text,
    )

    text = escape_html(text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", text)

    for i, html in enumerate(placeholders):
        text = text.replace(f"\x00{i}\x00", html)
    return text


def is_section_heading(lines: list[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    heading = lines[index].strip()
    underline = lines[index + 1].strip()
    return heading in SECTION_TITLES and bool(underline) and set(underline) <= {"-"}


def split_doc_description(doc: str) -> str:
    """Remove NumPy-style API sections from the prose summary."""
    lines = textwrap.dedent(doc or "").strip().splitlines()
    kept: list[str] = []
    i = 0
    while i < len(lines):
        if is_section_heading(lines, i):
            break
        kept.append(lines[i])
        i += 1
    return "\n".join(kept).strip()


def render_markdown_blocks(text: str) -> str:
    """Render a conservative Markdown/RST subset without external dependencies."""
    lines = textwrap.dedent(text or "").strip().splitlines()
    html_parts: list[str] = []
    paragraph: list[str] = []
    list_items: list[tuple[str, str]] = []
    in_fence = False
    fence_lang = ""
    code_lines: list[str] = []
    literal_next = False

    def flush_paragraph() -> None:
        nonlocal paragraph
        if paragraph:
            html_parts.append(f"<p>{render_inline_markup(' '.join(line.strip() for line in paragraph))}</p>")
            paragraph = []

    def flush_list() -> None:
        nonlocal list_items
        if not list_items:
            return
        tag = "ol" if list_items[0][0] == "ol" else "ul"
        body = "".join(f"<li>{render_inline_markup(item)}</li>" for _, item in list_items)
        html_parts.append(f"<{tag}>{body}</{tag}>")
        list_items = []

    def flush_code() -> None:
        nonlocal code_lines, fence_lang, literal_next
        if code_lines:
            lang_class = f" language-{escape_html(fence_lang)}" if fence_lang else ""
            html_parts.append(
                f'<pre><code class="{lang_class.strip()}">{escape_html("\n".join(code_lines).rstrip())}</code>'
                f'<button class="copy-btn">复制</button></pre>'
            )
            code_lines = []
        fence_lang = ""
        literal_next = False

    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if in_fence:
            if stripped.startswith("```"):
                in_fence = False
                flush_code()
            else:
                code_lines.append(line)
            i += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            flush_list()
            in_fence = True
            fence_lang = stripped[3:].strip()
            i += 1
            continue

        if literal_next:
            if line.startswith(("    ", "\t")):
                code_lines.append(line[4:] if line.startswith("    ") else line[1:])
                i += 1
                continue
            if code_lines:
                flush_code()

        if is_section_heading(lines, i):
            flush_paragraph()
            flush_list()
            html_parts.append(f"<h5>{escape_html(stripped)}</h5>")
            i += 2
            continue

        if stripped == "":
            flush_paragraph()
            flush_list()
            i += 1
            continue

        if stripped.endswith("::"):
            paragraph.append(stripped[:-1].rstrip())
            literal_next = True
            i += 1
            continue

        if stripped.startswith((">>> ", "... ")):
            flush_paragraph()
            flush_list()
            code_lines.append(stripped)
            i += 1
            while i < len(lines) and lines[i].strip().startswith((">>> ", "... ")):
                code_lines.append(lines[i].strip())
                i += 1
            flush_code()
            continue

        bullet = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if bullet or ordered:
            flush_paragraph()
            list_items.append(("ul", bullet.group(1)) if bullet else ("ol", ordered.group(1)))
            i += 1
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            flush_paragraph()
            flush_list()
            level = min(len(heading.group(1)) + 1, 5)
            html_parts.append(f"<h{level}>{render_inline_markup(heading.group(2))}</h{level}>")
            i += 1
            continue

        flush_list()
        paragraph.append(line)
        i += 1

    flush_paragraph()
    flush_list()
    if code_lines:
        flush_code()
    return "\n".join(html_parts)


def render_docstring(doc: str, summary_only: bool = True) -> str:
    """Convert the summary part of a docstring to HTML."""
    return render_markdown_blocks(split_doc_description(doc) if summary_only else doc)


def build_global_search_index(parsed_modules: dict[str, list[ApiItem]]) -> list[dict[str, str]]:
    index: list[dict[str, str]] = []
    page_by_module = dict(NAV_ORDER)
    for mod, _ in NAV_ORDER:
        meta = MODULE_META.get(mod, {})
        zh_title = meta.get("zh", {}).get("title", mod)
        page = page_by_module[mod]
        for item in parsed_modules.get(mod, []):
            if item.kind not in {"function", "class"}:
                continue
            index.append({
                "name": item.name,
                "kind": item.kind,
                "module": zh_title,
                "moduleEn": meta.get("en", {}).get("title", mod),
                "signature": item.signature,
                "desc": strip_doc_markup(item.doc_zh)[:180],
                "url": f"api/{page}#{item.kind}-{item.name}",
            })
    return index


def generate_api_page(
    module_name: str,
    items: list[ApiItem],
    out_path: Path,
    search_index: list[dict[str, str]],
) -> None:
    meta = MODULE_META.get(module_name, {})
    zh_title = meta.get("zh", {}).get("title", module_name)
    en_title = meta.get("en", {}).get("title", module_name)
    ja_title = meta.get("ja", {}).get("title", module_name)

    # Breadcrumb
    bc_zh = f'<a href="../index.html">Pyera</a> / API / {zh_title}'
    bc_en = f'<a href="../index.html">Pyera</a> / API / {en_title}'
    bc_ja = f'<a href="../index.html">Pyera</a> / API / {ja_title}'

    body_parts = []
    for lang, title in [("zh", zh_title), ("en", en_title), ("ja", ja_title)]:
        body_parts.append(f'<div class="lang-content" data-lang="{lang}" id="content-{lang}">')
        body_parts.append(f'<h1>{title}</h1>')

        for item in items:
            anchor = f"{item.kind}-{item.name}"
            body_parts.append(f'<div class="api-card" id="{anchor}">')
            body_parts.append('<div class="api-header">')
            body_parts.append(f'<div><span class="api-name">{item.name}</span>')
            if item.erb_cmd:
                body_parts.append(f' <span class="api-erb">{item.erb_cmd}</span>')
            body_parts.append('</div>')
            body_parts.append(f'<div class="api-sig">{escape_html(item.signature)}</div>')
            body_parts.append('</div>')

            body_parts.append('<div class="api-body">')

            # Description
            if item.doc_zh:
                body_parts.append(f'<div class="api-desc">{render_docstring(item.doc_zh, summary_only=item.kind == "function")}</div>')

            # Parameters
            if item.params:
                t = I18N[lang]
                body_parts.append(f'<h4>{t["parameters"]}</h4>')
                body_parts.append('<div class="param-list">')
                for p in item.params:
                    required = not p.default and not p.name.startswith("*")
                    req_badge = '<span class="param-required">必填</span>' if required else '<span class="param-optional">可选</span>'
                    type_hint = escape_html(p.type_hint) if p.type_hint else "Any"
                    default_text = escape_html(p.default) if p.default else "无默认值" if required else "None"
                    desc_html = (
                        f'<div class="param-desc-text">{render_markdown_blocks(p.desc)}</div>'
                        if p.desc
                        else '<div class="param-desc-text muted">暂无详细说明，请参考函数签名和上方说明。</div>'
                    )
                    body_parts.append(
                        f'<div class="param-item">'
                        f'<div class="param-topline">'
                        f'<span class="param-name">{escape_html(p.name)}</span>'
                        f'<span class="param-required-wrap">{req_badge}</span>'
                        f'</div>'
                        f'<div class="param-facts">'
                        f'<div><span>类型</span><code>{type_hint}</code></div>'
                        f'<div><span>默认值</span><code>{default_text}</code></div>'
                        f'</div>'
                        f'{desc_html}'
                        f'</div>'
                    )
                body_parts.append('</div>')

            body_parts.append('</div>')  # api-body
            body_parts.append('</div>')  # api-card

        body_parts.append('</div>')  # lang-content

    body = "\n".join(body_parts)
    html = page_skeleton(
        f"Pyera — {zh_title}",
        bc_zh,
        body,
        active=module_name,
        depth=1,
        search_data=search_index,
    )
    out_path.write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Generate index page
# ---------------------------------------------------------------------------

def generate_index(search_index: list[dict[str, str]]) -> None:
    features = [
        ("API", "Pythonic API", "Pythonic API", "Pythonic API",
         "用 Python 语法替代繁琐的 ERB，享受现代 IDE 的自动补全和类型检查。",
         "Replace tedious ERB with Python syntax, enjoy IDE autocompletion and type checking.",
         "面倒な ERB を Python 構文で置き換え、IDE の自動補完と型チェックを享受。"),
        ("STUB", "Stub 模式", "Stub Mode", "スタブモード",
         "无需 C# 运行时即可开发和测试，完整兼容 pytest 和 CI 流水线。",
         "Develop and test without C# runtime. Fully compatible with pytest and CI pipelines.",
         "C# ランタイムなしで開発・テスト可能。pytest や CI パイプラインと完全互換。"),
        ("ASYNC", "异步集成", "Async Integration", "非同期統合",
         "内置 asyncio 支持，可在事件处理器中安全调用 aiohttp、httpx 等第三方库。",
         "Built-in asyncio support. Safely call aiohttp, httpx and other third-party libraries from event handlers.",
         "asyncio サポートを内蔵。aiohttp、httpx などのサードパーティライブラリをイベントハンドラから安全に呼び出し可能。"),
        ("SAFE", "线程安全", "Thread-Safe", "スレッドセーフ",
         "事件注册表和日志系统均使用线程锁保护，后台线程与主线程安全协作。",
         "Event registry and logging system are protected by thread locks. Background threads cooperate safely with the main thread.",
         "イベント登録表とログシステムはスレッドロックで保護。バックグラウンドスレッドがメインスレッドと安全に協調。"),
    ]

    modules_html = ""
    for mod, page in NAV_ORDER:
        m = MODULE_META.get(mod, {})
        zh = m.get("zh", {})
        modules_html += (
            f'<a class="module-card" href="api/{page}">'
            f'<div class="name">{zh.get("title", mod)}</div>'
            f'<div class="desc">{zh.get("desc", "")}</div>'
            f'</a>\n'
        )

    def lang_block(lang):
        t = I18N[lang]
        return f'''<div class="lang-content" data-lang="{lang}" id="content-{lang}">
<div class="hero">
  <h1 class="hero-title">Pyera</h1>
  <p class="tagline">{"用 Python 语法编写 Emuera 游戏" if lang=="zh" else "Write Emuera games in Python" if lang=="en" else "Python で Emuera ゲームを作成"}</p>
  <div class="version-pill">v0.3.0</div>
</div>
<div class="features">
{chr(10).join(f"""<div class="feature-card">
  <div class="feature-icon"><span>{icon}</span></div>
  <h3>{title_zh if lang=="zh" else title_en if lang=="en" else title_ja}</h3>
  <p>{desc_zh if lang=="zh" else desc_en if lang=="en" else desc_ja}</p>
</div>""" for icon, title_zh, title_en, title_ja, desc_zh, desc_en, desc_ja in features)}
</div>
<div class="quick-start">
  <div class="quick-start-inner">
    <h2>{t["quick_install"]}</h2>
    <pre><code class="language-python"># py/main.py
import pyera

def system_title():
    pyera.clear_display()
    pyera.print_line("Hello Pyera!")
    pyera.print_button("[0] Start", 0)
    pyera.new_line()
    pyera.refresh(True)</code><button class="copy-btn">📋</button></pre>
    <p><a href="getting-started.html">{t["read_more"]}</a></p>
  </div>
</div>
<div class="content">
  <h2>{t["modules"]}</h2>
  <div class="module-grid">
    {modules_html}
  </div>
</div>
</div>'''

    body = lang_block("zh") + lang_block("en") + lang_block("ja")

    html = page_skeleton(
        "Pyera — Python scripting layer for Emuera",
        "Pyera",
        body,
        active="index",
        depth=0,
        search_data=search_index,
    )
    (BASE / "index.html").write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Generate getting-started
# ---------------------------------------------------------------------------

def generate_getting_started(search_index: list[dict[str, str]]) -> None:
    def lang_block(lang):
        t = I18N[lang]
        if lang == "zh":
            return f'''<div class="lang-content" data-lang="zh">
<div class="page-header">
  <h1>快速开始</h1>
  <p class="page-subtitle">从零开始构建你的第一个 Pyera 项目</p>
</div>
<div class="gs-grid">
  <div class="gs-card">
    <div class="gs-step">1</div>
    <h3>项目结构</h3>
    <p>在 Emuera 游戏根目录下创建 <code>py/</code> 文件夹，将 Python 脚本放在其中：</p>
    <pre><code>game_root/
  py/
    main.py          # 主入口
    my_module.py     # 可选模块
  csv/
  era/
  emuera.config</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">2</div>
    <h3>编写第一个事件</h3>
    <pre><code class="language-python">import pyera

def system_title():
    pyera.clear_display()
    pyera.print_line("=== My Game ===")
    pyera.print_button("[0] Start", 0)
    pyera.new_line()
    pyera.print_button("[1] Load", 1)
    pyera.new_line()
    pyera.refresh(True)

def event_first():
    pyera.clear_display()
    pyera.print_line("Welcome!")
    pyera.read_any_key()
    pyera.begin("title")</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">3</div>
    <h3>角色数据访问</h3>
    <pre><code class="language-python">count = pyera.chara_count()
for i in range(count):
    c = pyera.chara(i)
    pyera.print_line(f"[{{i}}] {{c.name}}: ABL[0]={{c.abl[0]}}")</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">4</div>
    <h3>异步与第三方库</h3>
    <pre><code class="language-python">import asyncio
from pyera._async_utils import run_on_main, ensure_main_loop

async def fetch_and_display():
    data = await some_async_http_call()
    await run_on_main(pyera.print_line, data["message"])

def event_shop():
    ensure_main_loop(fetch_and_display())</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card gs-card-wide">
    <div class="gs-step">5</div>
    <h3>调试技巧</h3>
    <ul>
      <li>设置环境变量 <code>PYERA_DEBUG=1</code> 启用调试输出</li>
      <li>使用 <code>pyera.enable_trace(True)</code> 记录 C# 调用序列</li>
      <li>使用 <code>pyera.log("message")</code> 输出调试日志</li>
      <li>stub 模式下可直接运行 pytest 测试</li>
    </ul>
  </div>
</div>
</div>'''
        elif lang == "en":
            return f'''<div class="lang-content" data-lang="en">
<div class="page-header">
  <h1>Getting Started</h1>
  <p class="page-subtitle">Build your first Pyera project from scratch</p>
</div>
<div class="gs-grid">
  <div class="gs-card">
    <div class="gs-step">1</div>
    <h3>Project Structure</h3>
    <p>Create a <code>py/</code> folder in the Emuera game root and place Python scripts inside:</p>
    <pre><code>game_root/
  py/
    main.py          # Main entry
    my_module.py     # Optional modules
  csv/
  era/
  emuera.config</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">2</div>
    <h3>Write Your First Event</h3>
    <pre><code class="language-python">import pyera

def system_title():
    pyera.clear_display()
    pyera.print_line("=== My Game ===")
    pyera.print_button("[0] Start", 0)
    pyera.new_line()
    pyera.print_button("[1] Load", 1)
    pyera.new_line()
    pyera.refresh(True)

def event_first():
    pyera.clear_display()
    pyera.print_line("Welcome!")
    pyera.read_any_key()
    pyera.begin("title")</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">3</div>
    <h3>Character Data Access</h3>
    <pre><code class="language-python">count = pyera.chara_count()
for i in range(count):
    c = pyera.chara(i)
    pyera.print_line(f"[{{i}}] {{c.name}}: ABL[0]={{c.abl[0]}}")</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">4</div>
    <h3>Async & Third-Party Libraries</h3>
    <pre><code class="language-python">import asyncio
from pyera._async_utils import run_on_main, ensure_main_loop

async def fetch_and_display():
    data = await some_async_http_call()
    await run_on_main(pyera.print_line, data["message"])

def event_shop():
    ensure_main_loop(fetch_and_display())</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card gs-card-wide">
    <div class="gs-step">5</div>
    <h3>Debugging Tips</h3>
    <ul>
      <li>Set env var <code>PYERA_DEBUG=1</code> to enable debug output</li>
      <li>Use <code>pyera.enable_trace(True)</code> to record C# call sequences</li>
      <li>Use <code>pyera.log("message")</code> for debug logging</li>
      <li>Run pytest directly in stub mode</li>
    </ul>
  </div>
</div>
</div>'''
        else:
            return f'''<div class="lang-content" data-lang="ja">
<div class="page-header">
  <h1>クイックスタート</h1>
  <p class="page-subtitle">最初の Pyera プロジェクトをゼロから構築</p>
</div>
<div class="gs-grid">
  <div class="gs-card">
    <div class="gs-step">1</div>
    <h3>プロジェクト構成</h3>
    <p>Emuera ゲームのルートに <code>py/</code> フォルダを作成し、Python スクリプトを配置：</p>
    <pre><code>game_root/
  py/
    main.py          # メインエントリ
    my_module.py     # オプションモジュール
  csv/
  era/
  emuera.config</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">2</div>
    <h3>最初のイベントを書く</h3>
    <pre><code class="language-python">import pyera

def system_title():
    pyera.clear_display()
    pyera.print_line("=== My Game ===")
    pyera.print_button("[0] Start", 0)
    pyera.new_line()
    pyera.print_button("[1] Load", 1)
    pyera.new_line()
    pyera.refresh(True)

def event_first():
    pyera.clear_display()
    pyera.print_line("Welcome!")
    pyera.read_any_key()
    pyera.begin("title")</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">3</div>
    <h3>キャラクターデータへのアクセス</h3>
    <pre><code class="language-python">count = pyera.chara_count()
for i in range(count):
    c = pyera.chara(i)
    pyera.print_line(f"[{{i}}] {{c.name}}: ABL[0]={{c.abl[0]}}")</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card">
    <div class="gs-step">4</div>
    <h3>非同期とサードパーティライブラリ</h3>
    <pre><code class="language-python">import asyncio
from pyera._async_utils import run_on_main, ensure_main_loop

async def fetch_and_display():
    data = await some_async_http_call()
    await run_on_main(pyera.print_line, data["message"])

def event_shop():
    ensure_main_loop(fetch_and_display())</code><button class="copy-btn">📋</button></pre>
  </div>
  <div class="gs-card gs-card-wide">
    <div class="gs-step">5</div>
    <h3>デバッグのヒント</h3>
    <ul>
      <li>環境変数 <code>PYERA_DEBUG=1</code> を設定してデバッグ出力を有効化</li>
      <li><code>pyera.enable_trace(True)</code> で C# 呼び出しシーケンスを記録</li>
      <li><code>pyera.log("message")</code> でデバッグログを出力</li>
      <li>stub モードで pytest を直接実行可能</li>
    </ul>
  </div>
</div>
</div>'''

    body = lang_block("zh") + lang_block("en") + lang_block("ja")
    html = page_skeleton(
        "Pyera — Getting Started",
        '<a href="index.html">Pyera</a> / Getting Started',
        body,
        active="getting-started",
        depth=0,
        search_data=search_index,
    )
    (BASE / "getting-started.html").write_text(html, encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print("Generating pyera documentation...")

    parsed_modules: dict[str, list[ApiItem]] = {}
    api_dir = BASE / "api"
    for mod, page in NAV_ORDER:
        path = SRC / f"{mod}.py"
        if not path.exists():
            print(f"  SKIP (not found): {path}")
            continue
        parsed_modules[mod] = parse_module(path)

    global_search_index = build_global_search_index(parsed_modules)

    # Generate API pages
    for mod, page in NAV_ORDER:
        if mod not in parsed_modules:
            continue
        print(f"  {mod} -> {page}")
        generate_api_page(mod, parsed_modules[mod], api_dir / page, global_search_index)

    # Generate global search index
    print("  api/search-index.json")
    (api_dir / "search-index.json").write_text(
        json.dumps(global_search_index, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Generate index
    print("  index.html")
    generate_index(global_search_index)

    # Generate getting-started
    print("  getting-started.html")
    generate_getting_started(global_search_index)

    # Generate example pages (basic)
    print("  examples/basic-game.html")
    (BASE / "examples" / "basic-game.html").write_text(
        page_skeleton(
            "Pyera — Example: Basic Game",
            '<a href="../index.html">Pyera</a> / Examples / Basic Game',
            '<div class="lang-content active" data-lang="zh"><h1>基础游戏示例</h1><p>请查看 <code>py/main.py</code> 获取完整示例代码。</p></div>',
            depth=1,
            search_data=global_search_index,
        ),
        encoding="utf-8",
    )

    print("  examples/async-integration.html")
    (BASE / "examples" / "async-integration.html").write_text(
        page_skeleton(
            "Pyera — Example: Async Integration",
            '<a href="../index.html">Pyera</a> / Examples / Async',
            '<div class="lang-content active" data-lang="zh"><h1>异步集成示例</h1><p>参考 getting-started 中的异步示例。</p></div>',
            depth=1,
            search_data=global_search_index,
        ),
        encoding="utf-8",
    )

    print("Done!")


if __name__ == "__main__":
    main()
