# 交付文件

- `作品书_OpenRSI-Calibrator.docx`：可编辑 Word，唯一正式源（由 `workspace/document_writing/正式稿.md` 经 `docx_export.py` 生成，Word 已更新目录域）。
- `作品书_OpenRSI-Calibrator.pdf`：由 Microsoft Word 从上面的 DOCX 导出，版式与 Word 一致。前置 6 页（罗马页码）、正文 41 页、参考文献 2 页。
- `作品书_OpenRSI-Calibrator.预览.html`：浏览器预览，不作为正式版式。

质量记录见 `../workspace/quality/`：`auto-check.json`（自动版式检查）、`human-review.json`（人工视觉与语义审查）、`qa-status.json`（哈希校验结果）。页面渲染可用
`python workflow/scripts/qa_ledger.py render-pages examples/ovd-rsi --pdf examples/ovd-rsi/output/作品书_OpenRSI-Calibrator.pdf` 由 PDF 逐字节一致地重新生成。
