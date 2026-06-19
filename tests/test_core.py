from __future__ import annotations

import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from word_a11y_fixer.core import audit_and_fix_docx


def _write_minimal_docx(path: Path) -> None:
    document = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing">
  <w:body>
    <w:p><w:pPr><w:pStyle w:val="Heading1"/></w:pPr><w:r><w:t>Titolo</w:t></w:r></w:p>
    <w:p><w:pPr><w:pStyle w:val="Heading3"/></w:pPr><w:r><w:t>Sottotitolo</w:t></w:r></w:p>
    <w:p/>
    <w:p><w:hyperlink><w:r><w:t>clicca qui</w:t></w:r></w:hyperlink></w:p>
    <w:p><w:r><w:drawing><wp:inline><wp:docPr id="1" name="Picture 1"/></wp:inline></w:drawing></w:r></w:p>
    <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Colonna</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
  </w:body>
</w:document>'''
    core = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title></dc:title></cp:coreProperties>'''
    with zipfile.ZipFile(path, "w") as package:
        package.writestr("[Content_Types].xml", "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\"/>")
        package.writestr("word/document.xml", document)
        package.writestr("docProps/core.xml", core)


def test_audit_and_fix_docx_creates_accessible_copy_and_report(tmp_path: Path) -> None:
    source = tmp_path / "origine.docx"
    output = tmp_path / "corretto.docx"
    report = tmp_path / "report.json"
    _write_minimal_docx(source)

    result = audit_and_fix_docx(source, output, report)

    assert output.exists()
    assert result.fixed_count >= 6
    report_data = json.loads(report.read_text(encoding="utf-8"))
    assert {issue["code"] for issue in report_data["issues"]} >= {
        "document-language",
        "document-title",
        "image-alt-text",
        "table-header",
        "heading-order",
        "hyperlink-text",
        "empty-paragraphs",
    }

    with zipfile.ZipFile(output) as package:
        document = ET.fromstring(package.read("word/document.xml"))
        xml = package.read("word/document.xml").decode("utf-8")

    assert "descr=\"Immagine" in xml
    assert "Apri collegamento: contenuto correlato" in xml
    assert "Heading2" in xml
    assert document.find(".//{http://schemas.openxmlformats.org/wordprocessingml/2006/main}tblHeader") is not None
