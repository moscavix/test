"""Core DOCX accessibility audit and repair logic.

The implementation works directly on the Office Open XML package used by
``.docx`` files.  Legacy binary ``.doc`` files must be converted to ``.docx``
first (for example with Microsoft Word or LibreOffice) before they can be
processed safely.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import copy
import json
import zipfile
from xml.etree import ElementTree as ET

NS = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "pic": "http://schemas.openxmlformats.org/drawingml/2006/picture",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

W = f"{{{NS['w']}}}"
WP = f"{{{NS['wp']}}}"
PIC = f"{{{NS['pic']}}}"

DOCUMENT_XML = "word/document.xml"
CORE_XML = "docProps/core.xml"
APP_XML = "docProps/app.xml"


@dataclass(slots=True)
class Issue:
    """A single accessibility issue found in the document."""

    code: str
    severity: str
    location: str
    message: str
    fix: str | None = None


@dataclass(slots=True)
class FixResult:
    """Result returned by :func:`audit_and_fix_docx`."""

    input_path: Path
    output_path: Path
    report_path: Path | None
    issues: list[Issue] = field(default_factory=list)
    fixed_count: int = 0

    def to_json(self) -> str:
        return json.dumps(
            {
                "input": str(self.input_path),
                "output": str(self.output_path),
                "fixed_count": self.fixed_count,
                "issues": [asdict(issue) for issue in self.issues],
            },
            ensure_ascii=False,
            indent=2,
        )


def audit_and_fix_docx(input_path: Path, output_path: Path, report_path: Path | None = None) -> FixResult:
    """Create an accessible copy of ``input_path`` at ``output_path``.

    The fixer targets common checks also surfaced by Word's Accessibility
    Checker: missing document language/title, missing image alternative text,
    empty paragraphs, tables without a header row, skipped heading levels, and
    ambiguous hyperlink text.  It preserves the original file and writes all
    changes to a new DOCX package.
    """

    input_path = input_path.expanduser().resolve()
    output_path = output_path.expanduser().resolve()
    if input_path.suffix.lower() != ".docx":
        raise ValueError("Only .docx files are supported; convert legacy .doc files to .docx first.")
    if not input_path.exists():
        raise FileNotFoundError(input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = FixResult(input_path=input_path, output_path=output_path, report_path=report_path)
    with zipfile.ZipFile(input_path, "r") as source_package:
        package_entries = {name: source_package.read(name) for name in source_package.namelist()}

    document = ET.fromstring(package_entries[DOCUMENT_XML])
    result.fixed_count += _fix_document_language(document, result.issues)
    result.fixed_count += _remove_empty_paragraphs(document, result.issues)
    result.fixed_count += _fix_images(document, result.issues)
    result.fixed_count += _fix_tables(document, result.issues)
    result.fixed_count += _fix_heading_levels(document, result.issues)
    result.fixed_count += _fix_hyperlinks(document, result.issues)
    package_entries[DOCUMENT_XML] = _xml_bytes(document)

    if CORE_XML in package_entries:
        core = ET.fromstring(package_entries[CORE_XML])
        result.fixed_count += _fix_core_title(core, input_path.stem, result.issues)
        package_entries[CORE_XML] = _xml_bytes(core)

    if APP_XML in package_entries:
        app = ET.fromstring(package_entries[APP_XML])
        result.fixed_count += _fix_app_properties(app, result.issues)
        package_entries[APP_XML] = _xml_bytes(app)

    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as fixed_package:
        for name, payload in package_entries.items():
            fixed_package.writestr(name, payload)

    if report_path:
        report_path = report_path.expanduser().resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(result.to_json() + "\n", encoding="utf-8")
        result.report_path = report_path
    return result


def _xml_bytes(root: ET.Element) -> bytes:
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def _text(element: ET.Element) -> str:
    return "".join(node.text or "" for node in element.findall(f".//{W}t")).strip()


def _paragraphs(root: ET.Element) -> list[ET.Element]:
    return root.findall(f".//{W}p")


def _fix_document_language(root: ET.Element, issues: list[Issue]) -> int:
    settings = root.find(f".{W}body/{W}p/{W}pPr/{W}rPr/{W}lang")
    if settings is not None and settings.get(f"{W}val"):
        return 0
    first_para = root.find(f".{W}body/{W}p")
    if first_para is None:
        return 0
    ppr = first_para.find(f"{W}pPr")
    if ppr is None:
        ppr = ET.SubElement(first_para, f"{W}pPr")
    rpr = ppr.find(f"{W}rPr")
    if rpr is None:
        rpr = ET.SubElement(ppr, f"{W}rPr")
    lang = rpr.find(f"{W}lang")
    if lang is None:
        lang = ET.SubElement(rpr, f"{W}lang")
    lang.set(f"{W}val", "it-IT")
    issues.append(Issue("document-language", "error", "document", "Lingua del documento mancante.", "Impostata lingua it-IT."))
    return 1


def _remove_empty_paragraphs(root: ET.Element, issues: list[Issue]) -> int:
    fixed = 0
    for parent in root.iter():
        for child in list(parent):
            if child.tag == f"{W}p" and not _text(child) and child.find(f".//{W}drawing") is None:
                parent.remove(child)
                fixed += 1
    if fixed:
        issues.append(Issue("empty-paragraphs", "warning", "document", f"Trovati {fixed} paragrafi vuoti usati come spaziatura.", "Rimossi i paragrafi vuoti."))
    return fixed


def _fix_images(root: ET.Element, issues: list[Issue]) -> int:
    fixed = 0
    for idx, c_nv_pr in enumerate(root.findall(f".//{PIC}cNvPr") + root.findall(f".//{WP}docPr"), start=1):
        descr = (c_nv_pr.get("descr") or "").strip()
        title = (c_nv_pr.get("title") or "").strip()
        if not descr and not title:
            c_nv_pr.set("descr", f"Immagine {idx}: descrizione alternativa generata automaticamente da verificare.")
            issues.append(Issue("image-alt-text", "error", f"image {idx}", "Immagine senza testo alternativo.", "Aggiunto testo alternativo descrittivo provvisorio."))
            fixed += 1
    return fixed


def _fix_tables(root: ET.Element, issues: list[Issue]) -> int:
    fixed = 0
    for idx, table in enumerate(root.findall(f".//{W}tbl"), start=1):
        first_row = table.find(f"{W}tr")
        if first_row is None or first_row.find(f"{W}trPr/{W}tblHeader") is not None:
            continue
        trpr = first_row.find(f"{W}trPr")
        if trpr is None:
            trpr = ET.Element(f"{W}trPr")
        if first_row.find(f"{W}trPr") is None:
            first_row.insert(0, trpr)
        ET.SubElement(trpr, f"{W}tblHeader").set(f"{W}val", "true")
        issues.append(Issue("table-header", "error", f"table {idx}", "Tabella senza riga di intestazione.", "Marcata la prima riga come intestazione."))
        fixed += 1
    return fixed


def _fix_heading_levels(root: ET.Element, issues: list[Issue]) -> int:
    fixed = 0
    previous = 0
    for idx, paragraph in enumerate(_paragraphs(root), start=1):
        style = paragraph.find(f"{W}pPr/{W}pStyle")
        if style is None:
            continue
        value = style.get(f"{W}val") or ""
        if not value.startswith("Heading") and not value.startswith("Titolo"):
            continue
        digits = "".join(ch for ch in value if ch.isdigit())
        if not digits:
            continue
        level = int(digits)
        if previous and level > previous + 1:
            new_level = previous + 1
            style.set(f"{W}val", value.replace(str(level), str(new_level), 1))
            issues.append(Issue("heading-order", "error", f"paragraph {idx}", f"Livello titolo saltato da {previous} a {level}.", f"Corretto a livello {new_level}."))
            level = new_level
            fixed += 1
        previous = level
    return fixed


def _fix_hyperlinks(root: ET.Element, issues: list[Issue]) -> int:
    fixed = 0
    bad_text = {"clicca qui", "qui", "link", "leggi", "continua"}
    for idx, hyperlink in enumerate(root.findall(f".//{W}hyperlink"), start=1):
        label = _text(hyperlink).lower()
        if label in bad_text:
            for text_node in hyperlink.findall(f".//{W}t"):
                text_node.text = "Apri collegamento: contenuto correlato"
                break
            issues.append(Issue("hyperlink-text", "warning", f"hyperlink {idx}", f"Testo link ambiguo: '{label}'.", "Sostituito con testo più descrittivo."))
            fixed += 1
    return fixed


def _fix_core_title(root: ET.Element, fallback: str, issues: list[Issue]) -> int:
    ns_dc = "{http://purl.org/dc/elements/1.1/}"
    title = root.find(f"{ns_dc}title")
    if title is None:
        title = ET.SubElement(root, f"{ns_dc}title")
    if (title.text or "").strip():
        return 0
    title.text = fallback.replace("_", " ").replace("-", " ").title()
    issues.append(Issue("document-title", "error", "properties", "Titolo documento mancante.", "Aggiunto titolo dalle proprietà del file."))
    return 1


def _fix_app_properties(root: ET.Element, issues: list[Issue]) -> int:
    fixed = 0
    for tag in ("Company", "Manager"):
        node = root.find(f"{{http://schemas.openxmlformats.org/officeDocument/2006/extended-properties}}{tag}")
        if node is not None and (node.text or "").strip().lower() in {"", "todo", "unknown"}:
            node.text = None
            fixed += 1
    if fixed:
        issues.append(Issue("metadata-cleanup", "warning", "properties", "Metadati non significativi trovati.", "Ripuliti metadati vuoti o provvisori."))
    return fixed


def clone_issue(issue: Issue) -> Issue:
    """Return a copy of an issue for integrations that need immutable snapshots."""

    return copy.copy(issue)
