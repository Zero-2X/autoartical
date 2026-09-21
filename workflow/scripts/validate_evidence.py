from __future__ import annotations
import argparse,json
from pathlib import Path
from citation_checker import check_citations
from evidence_verifier import verify_evidence_items
from conflict_detector import detect_conflicts
def main():
 p=argparse.ArgumentParser(description='核验证据台账的引用、完整性和数值冲突'); p.add_argument('ledger',type=Path); p.add_argument('--out',type=Path); a=p.parse_args(); data=json.loads(a.ledger.read_text(encoding='utf-8')); items=data.get('items',data if isinstance(data,list) else []); report={'citation_check':check_citations(items),'evidence_check':verify_evidence_items(items),'conflict_check':detect_conflicts(items)}; report['verdict']='pass' if all(x['verdict']=='pass' for x in report.values()) else 'warn'; out=a.out or a.ledger.with_name('evidence-review.json'); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0
if __name__=='__main__': raise SystemExit(main())
