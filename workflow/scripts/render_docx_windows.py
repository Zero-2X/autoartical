#!/usr/bin/env python3
"""Render a DOCX with installed Microsoft Word on Windows for visual QA.

The documents skill's LibreOffice renderer is preferred when available.  This
small fallback uses Word's own fixed-layout export, so tables, fonts, fields,
and editable image objects are measured by the application users will open.
"""
from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("docx", type=Path)
    parser.add_argument("pdf", type=Path)
    args = parser.parse_args()
    if not args.docx.exists():
        raise SystemExit(f"DOCX 不存在：{args.docx}")
    if __import__("sys").platform != "win32":
        raise SystemExit("该 fallback 只在 Windows 上调用已安装的 Microsoft Word。")
    try:
        import win32com.client
    except ImportError as exc:  # pragma: no cover - host dependent
        raise SystemExit("缺少 pywin32；请先使用 documents skill 的 render_docx.py。") from exc
    args.pdf.parent.mkdir(parents=True, exist_ok=True)
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    document = None
    try:
        document = word.Documents.Open(str(args.docx.resolve()), ReadOnly=True, AddToRecentFiles=False)
        # 17 = wdExportFormatPDF; the remaining arguments keep the full
        # document, update fields, and preserve document tags where supported.
        document.ExportAsFixedFormat(str(args.pdf.resolve()), 17, False, 0, 0, 0, 0, 0, True, False, False, False, False, False)
    finally:
        if document is not None:
            document.Close(False)
        word.Quit()
    print(args.pdf)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

