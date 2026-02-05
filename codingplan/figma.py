"""从需求文件中解析 Figma 设计链接与交互说明"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# Figma URL 匹配（支持 design、file、proto 等，含 query）
FIGMA_URL_PATTERN = re.compile(
    r"https?://(?:www\.)?figma\.com/(?:design|file|proto)/[^\s\)\]\"']+(?:\?[^\s\)\]\"']*)?",
    re.IGNORECASE,
)

# 匹配 ## Figma 设计 / ## 设计 / ## 交互说明 等标题下的内容
FIGMA_SECTION_HEADERS = [
    r"^#+\s*(?:Figma\s*)?设计\s*$",
    r"^#+\s*Figma\s*$",
    r"^#+\s*交互(?:说明)?\s*$",
    r"^#+\s*UI\s*设计\s*$",
    r"^#+\s*设计(?:稿|链接)?\s*$",
]


@dataclass
class FigmaInfo:
    """Figma 设计信息"""

    links: list[str]
    interaction_desc: str

    def is_empty(self) -> bool:
        return not self.links and not self.interaction_desc.strip()


def extract_figma_info(content: str) -> FigmaInfo:
    """
    从需求文件内容中提取 Figma 链接和交互说明

    支持的格式示例：
    - 正文中的 Figma URL
    - ## Figma 设计 或 ## 交互说明 标题下的内容
    - 链接: https://figma.com/...
    - 交互说明: 点击卡片进入详情...
    """
    content = content.replace("\x00", "")
    links: list[str] = []
    interaction_parts: list[str] = []

    # 1. 提取所有 Figma URL
    for m in FIGMA_URL_PATTERN.finditer(content):
        url = m.group(0).rstrip(".,;:)")
        if url not in links:
            links.append(url)

    # 2. 提取「交互说明」标题下的内容
    lines = content.split("\n")
    in_figma_section = False
    section_content: list[str] = []
    header_pattern = re.compile("|".join(FIGMA_SECTION_HEADERS), re.IGNORECASE)

    for line in lines:
        stripped = line.strip()
        if header_pattern.match(stripped):
            if section_content and in_figma_section:
                interaction_parts.append("\n".join(section_content).strip())
            in_figma_section = True
            section_content = []
            continue
        if in_figma_section:
            # 遇到同级或更高级标题则结束
            if stripped.startswith("#") and not stripped.startswith("###"):
                if section_content:
                    interaction_parts.append("\n".join(section_content).strip())
                in_figma_section = False
                section_content = []
            else:
                section_content.append(line)

    if section_content and in_figma_section:
        interaction_parts.append("\n".join(section_content).strip())

    # 3. 提取「链接:」「交互说明:」这类键值对
    for line in lines:
        if re.match(r"^\s*链接\s*[:：]\s*", line, re.IGNORECASE):
            rest = re.sub(r"^\s*链接\s*[:：]\s*", "", line, flags=re.I).strip()
            url_match = FIGMA_URL_PATTERN.search(rest)
            if url_match:
                u = url_match.group(0).rstrip(".,;:)")
                if u not in links:
                    links.append(u)
        if re.match(r"^\s*交互说明\s*[:：]\s*", line, re.IGNORECASE):
            rest = re.sub(r"^\s*交互说明\s*[:：]\s*", "", line, flags=re.I).strip()
            if rest and rest not in interaction_parts:
                interaction_parts.append(rest)

    interaction_desc = "\n\n".join(p for p in interaction_parts if p).strip()
    return FigmaInfo(links=links, interaction_desc=interaction_desc or "")


def extract_from_file(file_path: Path) -> FigmaInfo:
    """从文件中提取 Figma 信息"""
    if not file_path.exists():
        return FigmaInfo(links=[], interaction_desc="")
    try:
        content = file_path.read_text(encoding="utf-8", errors="replace")
        return extract_figma_info(content)
    except Exception:
        return FigmaInfo(links=[], interaction_desc="")


def _merge_figma_info(info: FigmaInfo, extra: FigmaInfo) -> None:
    """合并 extra 到 info"""
    for link in extra.links:
        if link not in info.links:
            info.links.append(link)
    if extra.interaction_desc:
        info.interaction_desc = (info.interaction_desc + "\n\n" + extra.interaction_desc).strip()


def extract_from_req_dir(req_dir: Path, req_file: Path, ui_dir: Optional[Path] = None) -> FigmaInfo:
    """
    从需求目录及 UI 设计目录提取 Figma 信息。

    查找顺序：
    1. 需求文件内容
    2. 需求目录下的 {需求名}.figma.md
    3. UI 设计目录下的 {需求名}.md 或 {需求名}.figma.md（若指定 ui_dir）
    """
    base = req_file.stem

    info = extract_from_file(req_file)

    # 需求目录下的 .figma.md
    figma_file = req_dir / f"{base}.figma.md"
    if figma_file.exists():
        _merge_figma_info(info, extract_from_file(figma_file))

    # UI 设计目录（默认 uidesign）
    if ui_dir and ui_dir.exists():
        for name in [f"{base}.md", f"{base}.figma.md"]:
            ui_file = ui_dir / name
            if ui_file.exists():
                _merge_figma_info(info, extract_from_file(ui_file))
                break

    return info
