from __future__ import annotations
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
TOOLS=ROOT/'workflow'/'scripts'
def main():
 p=argparse.ArgumentParser(description='运行一次文档审查并把结果写入迭代数据库')
 p.add_argument('document',type=Path); p.add_argument('--project',required=True); p.add_argument('--round',type=int,required=True); p.add_argument('--db',type=Path,required=True); p.add_argument('--trigger',required=True); p.add_argument('--changes',default=''); args=p.parse_args()
 review=args.document.with_name(args.document.stem+f'-review-r{args.round}.json')
 evaluation = subprocess.run([sys.executable,str(TOOLS/'evaluate_document.py'),str(args.document),'--out',str(review)],check=False)
 report=json.loads(review.read_text(encoding='utf-8')); checks=report['generated_checks']; strengths=[f"coverage_score={report['coverage_score']}",f"citations={checks['citation_count']}"]
 defects=list(report.get('missing_sections',[]))+list(report.get('ai_style_risks',{}).keys())+list(report.get('text_quality',{}).get('failures',[]))
 subprocess.run([sys.executable,str(TOOLS/'iteration_memory.py'),str(args.db),'add','--project',args.project,'--round',str(args.round),'--trigger',args.trigger,'--strengths','|'.join(strengths),'--defects','|'.join(defects),'--changes',args.changes,'--evidence',str(review),'--metrics',json.dumps(checks,ensure_ascii=False)],check=True)
 print(json.dumps({'review':str(review),'verdict':report['verdict'],'coverage_score':report['coverage_score'],'defects':defects,'evaluation_exit_code':evaluation.returncode},ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
