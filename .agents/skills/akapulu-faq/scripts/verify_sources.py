#!/usr/bin/env python3
"""Check exact source provenance and scenario shape; never claim live correctness."""
import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import re
from uuid import UUID
from validate_scenario import check

def normalize(text):
    return re.sub(r'\s+', ' ', text).strip()

def verify(project, ready=False):
    root = Path(project).resolve() / 'akapulu'
    knowledge = (root / 'knowledge.txt').read_text(encoding='utf-8')
    if not knowledge.strip() or len(knowledge.encode()) > 130 * 1024:
        raise ValueError('Knowledge must be nonempty UTF-8 text under 130 KiB.')
    lines = [normalize(x) for x in knowledge.splitlines() if x.strip() and not x.startswith('# ')]
    entries = json.loads((root / 'sources.json').read_text())['entries']
    if Counter(lines) != Counter(normalize(e['text']) for e in entries):
        raise ValueError('Every non-heading knowledge line must have exactly one matching evidence entry.')
    for entry in entries:
        path = (root / entry['source']).resolve()
        if not path.is_relative_to(root):
            raise ValueError('Source snapshot path must stay inside akapulu/.')
        snapshot = json.loads(path.read_text())
        if sha256(snapshot['text'].encode()).hexdigest() != snapshot['sha256']:
            raise ValueError('Source snapshot changed; capture and review it again.')
        if not snapshot.get('source') or not snapshot.get('captured_at'):
            raise ValueError('Source snapshot needs source and captured_at.')
        claim, quote = normalize(entry['text']), normalize(entry['quote'])
        if claim != quote or quote not in normalize(snapshot['text']):
            raise ValueError(f'Knowledge line is not an exact supported passage: {claim[:100]}')
    scenario = json.loads((root / 'scenario.json').read_text())
    problems = check(scenario)
    if problems:
        raise ValueError(str(problems))
    functions = [f for node in scenario['nodes'].values() for f in node.get('functions', [])]
    if len(functions) != 1 or functions[0].get('type') != 'rag':
        raise ValueError('This FAQ starter expects exactly one RAG tool and no action/vision tools.')
    value = functions[0].get('knowledge_base_id', '')
    if value == 'PLACEHOLDER_CREATE_KNOWLEDGE_BASE_FIRST' and not ready:
        state = 'DRAFT — placeholder KB; not connected'
    else:
        UUID(value)
        state = 'LOCAL CHECKS PASSED — verify resource IDs and document completion through API'
    return f'{state}. {len(lines)} exact source passages. Live retrieval, answers and latency remain untested.'

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('project')
    p.add_argument('--ready', action='store_true', help='Reject draft placeholder IDs; does not prove live connection')
    args = p.parse_args()
    try:
        print(verify(args.project, args.ready))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        p.exit(1, f'CHECK FAILED: {exc}\n')
