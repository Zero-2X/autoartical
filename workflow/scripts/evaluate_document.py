from __future__ import annotations
import argparse,json,re
from pathlib import Path
REQUIRED=['摘要','问题','方案','创新','实施','风险','参考文献']
GENERIC=['本文将','综上所述','具有重要意义','赋能','打造','助力','显著提升','值得注意的是']
def main():
 p=argparse.ArgumentParser(description='按论文、竞赛说明书和基金申报书维度审查文档'); p.add_argument('document',type=Path); p.add_argument('--out',type=Path); a=p.parse_args()
 text=a.document.read_text(encoding='utf-8'); paragraphs=[x.strip() for x in re.split(r'\n\s*\n',text) if x.strip()]; headings=re.findall(r'^#{1,4}\s+(.+)$',text,re.M); tables=[x for x in text.splitlines() if '|' in x and x.count('|')>=2]; cites=re.findall(r'\[[0-9]+\]|\(.*?\d{4}.*?\)',text); table_quality={'has_units': '单位' in text, 'has_sources': ('来源' in text or '数据来源' in text), 'has_statistical_basis': ('统计' in text or '置信区间' in text)}; mermaid='```mermaid' in text; images=bool(re.search(r'!\[[^]]*\]\([^)]*\)',text)); generic={w:text.count(w) for w in GENERIC if text.count(w)}; repeated=[]
 for p1 in paragraphs:
  if len(p1)>60 and paragraphs.count(p1)>1: repeated.append(p1[:80])
 rubric={'论文': {'问题与贡献':any(k in text for k in ['研究问题','贡献']), '方法与验证':any(k in text for k in ['方法','验证','实验']), '引用可追溯':len(cites)>=3}, '竞赛说明书': {'需求覆盖':any(k in text for k in ['需求','用户']), '方案闭环':all(k in text for k in ['方案','实施','风险']), '评审友好':len(tables)>=1}, '基金申报书': {'科学问题':any(k in text for k in ['科学问题','关键问题']), '技术路线':any(k in text for k in ['技术路线','研究内容']), '可行性与风险':all(k in text for k in ['可行性','风险'])}}
 score=sum(sum(bool(v) for v in x.values()) for x in rubric.values())/(sum(len(x) for x in rubric.values()) or 1); report={'document':str(a.document),'generated_checks':{'heading_count':len(headings),'paragraph_count':len(paragraphs),'table_line_count':len(tables),'citation_count':len(cites),'has_mermaid':mermaid,'has_embedded_image':images,'table_quality':table_quality,'generic_phrase_counts':generic,'repeated_paragraphs':repeated},'rubric':rubric,'coverage_score':round(score,3),'ai_style_risks':generic,'verdict':'pass' if score>=0.75 and not repeated else 'revise','missing_sections':[x for x in REQUIRED if x not in text]}; out=a.out or a.document.with_name(a.document.stem+'-review.json'); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
