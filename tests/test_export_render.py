"""Regression tests for the Word-as-source delivery chain and its gates.

Each test pins down a defect found in the 2026-10 audit (see
docs/audit-2026-10.md) so that it cannot silently return.
"""
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workflow" / "scripts"))

from content_depth import content_metrics  # noqa: E402
from delivery_contract import build_figure_table_gate  # noqa: E402
from docx_export import _split_scripts, export_docx  # noqa: E402
from manuscript_lint import lint  # noqa: E402
from run_document_export import _image_data_uri, markdown_to_html  # noqa: E402
from word_pipeline import classify_pages, evaluate  # noqa: E402

FIGURE = ROOT / "examples" / "ovd-rsi" / "workspace" / "document_assets" / "figures" / "s_validation_visual_4.png"

GOOD = """## 第1章 绪论

### 1.1 问题

遥感检测基准覆盖的类别有限，DOTA 标注了 15 个类别[1]，DIOR 标注了 20 个类别[2]。表1-1 列出了两者的差异，这一差异说明扩大标注规模并没有带来词汇覆盖的同步增长，因此需要研究开放词汇方法在遥感影像中的表现与可靠性。

表1-1 基准比较

| 基准 | 类别数 |
|---|---|
| DOTA | 15 |
| DIOR | 20 |

注：数据来源为原论文摘要[1-2]。

## 参考文献

[1] XIA GS. DOTA[C]. 2018.
[2] LI K. DIOR[J]. 2020.
"""


def page(n, fill=0.9, chars=900, images=0):
    return {"page": n, "fill": fill, "chars": chars, "images": images, "overflow": [], "head": ""}


class ManuscriptLintTests(unittest.TestCase):
    def test_clean_manuscript_passes(self):
        result = lint(GOOD)
        self.assertEqual(result["verdict"], "pass", result["failures"])

    def test_generic_and_repeated_headings_fail(self):
        text = GOOD.replace("### 1.1 问题", "### 核心内容\n\n正文。\n\n### 核心内容")
        failures = " ".join(lint(text)["failures"])
        self.assertIn("重复标题", failures)
        self.assertIn("空泛标题", failures)

    def test_workflow_meta_text_in_body_fails(self):
        text = GOOD.replace("因此需要研究", "本节通过门禁与 manifest 校验，因此需要研究")
        self.assertIn("元信息", " ".join(lint(text)["failures"]))

    def test_citation_order_and_dangling_numbers_fail(self):
        swapped = GOOD.replace("15 个类别[1]", "15 个类别[2]").replace("20 个类别[2]", "20 个类别[1]")
        self.assertIn("首次出现顺序", " ".join(lint(swapped)["failures"]))
        dangling = GOOD.replace("20 个类别[2]", "20 个类别[7]")
        self.assertIn("不存在的文献编号", " ".join(lint(dangling)["failures"]))

    def test_math_interval_is_not_a_citation(self):
        text = GOOD.replace("因此需要研究", "门控系数 $g∈[0,1]$，因此需要研究")
        self.assertEqual(lint(text)["verdict"], "pass", lint(text)["failures"])

    def test_uncited_table_and_unmarked_result_number_fail(self):
        uncited = GOOD.replace("表1-1 列出了两者的差异，", "")
        self.assertIn("未在正文中被引用", " ".join(lint(uncited)["failures"]))
        claim = GOOD.replace("因此需要研究", "本方法使 mAP 提升 5.2%，因此需要研究")
        self.assertIn("结果数字", " ".join(lint(claim)["failures"]))


class ContentDepthTests(unittest.TestCase):
    def test_comparison_signs_do_not_swallow_text(self):
        # "<[^>]+>" used to delete everything between "p < τ" and a later ">".
        text = "阈值 $p < τ$ 的候选。\n\n" + "中间段落有实际论证内容。" * 20 + "\n\n长宽比 >4 的目标。"
        self.assertGreater(content_metrics(text)["prose_units"], 200)

    def test_real_html_tags_are_still_removed(self):
        self.assertEqual(content_metrics("<b>粗</b>")["prose_units"], 1)


class LayoutEvaluationTests(unittest.TestCase):
    def facts(self, headings, pages):
        return {"pages": pages, "headings": headings, "figure_captions": [], "tables": []}

    def pdf(self, pages, fonts=None, size=12.0):
        return {"pages": pages, "fonts": fonts or {"SimSun": 1, "TimesNewRomanPSMT": 1}, "dominant_font_size_pt": size}

    def test_body_pages_counted_separately_and_no_upper_limit(self):
        headings = [{"text": "第1章 绪论", "level": "1", "page": 3, "next_block_page": 3},
                    {"text": "参考文献", "level": "1", "page": 55, "next_block_page": 55}]
        pages = [page(i) for i in range(1, 57)]
        result = evaluate(self.facts(headings, 56), self.pdf(pages), {"target_pages": [40, None], "min_body_fill": 0.75})
        self.assertEqual(result["layout"]["counts"]["body"], 52)
        self.assertEqual(result["layout"]["counts"]["front"], 2)
        self.assertEqual(result["failures"], [])

    def test_too_few_body_pages_fail_even_if_total_is_large(self):
        headings = [{"text": "第1章 绪论", "level": "1", "page": 10, "next_block_page": 10},
                    {"text": "参考文献", "level": "1", "page": 40, "next_block_page": 40}]
        pages = [page(i) for i in range(1, 50)]
        result = evaluate(self.facts(headings, 49), self.pdf(pages), {"target_pages": [40, None]})
        self.assertTrue(any("低于下限" in f for f in result["failures"]))

    def test_scaled_text_fallback_font_and_sparse_pages_fail(self):
        headings = [{"text": "第1章 绪论", "level": "1", "page": 1, "next_block_page": 1}]
        pages = [page(i) for i in range(1, 42)]
        pages[5]["fill"] = 0.4
        result = evaluate(self.facts(headings, 41), self.pdf(pages, {"SimSun": 1, "Calibri": 3}, size=8.5),
                          {"target_pages": [40, None], "min_body_fill": 0.75})
        joined = " ".join(result["failures"])
        self.assertIn("Calibri", joined)
        self.assertIn("8.5pt", joined)
        self.assertIn("填充率", joined)

    def test_stranded_heading_fails(self):
        headings = [{"text": "第1章 绪论", "level": "1", "page": 1, "next_block_page": 1},
                    {"text": "1.2 孤立标题", "level": "2", "page": 7, "next_block_page": 8}]
        pages = [page(i) for i in range(1, 42)]
        result = evaluate(self.facts(headings, 41), self.pdf(pages), {"target_pages": [40, None]})
        self.assertTrue(any("孤立" in f for f in result["failures"]))

    def test_classify_pages_maps_front_body_refs(self):
        headings = [{"text": "第1章 绪论", "level": "1", "page": 6},
                    {"text": "参考文献", "level": "1", "page": 47},
                    {"text": "附录A 数据", "level": "1", "page": 49}]
        layout = classify_pages([page(i) for i in range(1, 51)], headings)
        self.assertEqual(layout["counts"], {"front": 5, "body": 41, "references": 2, "appendix": 2})


class CodeHashTests(unittest.TestCase):
    def test_code_hash_ignores_line_endings_but_not_content(self):
        from word_pipeline import sha256_code

        with tempfile.TemporaryDirectory() as tmp:
            lf, crlf, edited = (Path(tmp) / n for n in ("a.py", "b.py", "c.py"))
            lf.write_bytes(b"x = 1\ny = 2\n")
            crlf.write_bytes(b"x = 1\r\ny = 2\r\n")
            edited.write_bytes(b"x = 1\ny = 3\n")
            self.assertEqual(sha256_code(lf), sha256_code(crlf))
            self.assertNotEqual(sha256_code(lf), sha256_code(edited))


class ExporterTests(unittest.TestCase):
    def test_nested_subscripts_parse(self):
        pieces = _split_scripts("Σ_{k∈{attr,scene}} g_k·cos(f_r, t_k)")
        self.assertIn(("_", "k∈{attr,scene}"), pieces)
        self.assertIn(("_", "r"), pieces)

    def test_missing_figure_raises_instead_of_placeholder_text(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                export_docx("# 题目\n\n## 第1章 绪论\n\n![图1-1 缺失](missing.png)\n", Path(tmp) / "a.docx", base_dirs=[Path(tmp)])

    def test_docx_has_no_theme_fonts_and_three_line_tables(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "a.docx"
            meta = export_docx("# 题目：副题\n\n" + GOOD, out, title="短题")
            self.assertEqual(meta["tables"], 1)
            import zipfile

            with zipfile.ZipFile(out) as archive:
                styles = archive.read("word/styles.xml").decode("utf-8")
                document = archive.read("word/document.xml").decode("utf-8")
            self.assertNotIn("asciiTheme", styles)
            self.assertIn('w:val="nil"', document)  # vertical rules removed

    def test_html_preview_inlines_figures(self):
        self.assertTrue(_image_data_uri(str(FIGURE)).startswith("data:image/png;base64,"))
        self.assertIn("<img", markdown_to_html(f"![图1-1 示意]({FIGURE})", "t"))


class FigureGateTests(unittest.TestCase):
    def test_chart_without_provenance_is_rejected_and_with_provenance_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            topic = Path(tmp)
            charts = topic / "charts"
            charts.mkdir()
            image = charts / "scale_chart.png"
            shutil.copyfile(FIGURE, image)
            draft = "如图1-1 所示。\n\n![图1-1 数据](charts/scale_chart.png)\n"
            gate = build_figure_table_gate(topic, draft)
            self.assertFalse(gate["passed"])
            data = topic / "d.csv"
            data.write_text("a,b\n1,2\n", encoding="utf-8")
            script = topic / "s.py"
            script.write_text("pass\n", encoding="utf-8")
            sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
            text_sha = lambda p: hashlib.sha256(p.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
            image.with_suffix(".provenance.json").write_text(json.dumps({
                "data": "d.csv", "data_sha256": text_sha(data), "script": "s.py", "script_sha256": text_sha(script),
                "image_sha256": sha(image), "sources": ["x"], "argument_role": "data"}), encoding="utf-8")
            self.assertTrue(build_figure_table_gate(topic, draft)["passed"])
            data.write_text("a,b\n1,3\n", encoding="utf-8")  # data changed -> chart stale
            self.assertFalse(build_figure_table_gate(topic, draft)["passed"])

    def test_table_without_source_note_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            draft = GOOD.replace("注：数据来源为原论文摘要[1-2]。", "")
            gate = build_figure_table_gate(Path(tmp), draft)
            self.assertTrue(any("表注" in f for f in gate["failures"]))


if __name__ == "__main__":
    unittest.main()
