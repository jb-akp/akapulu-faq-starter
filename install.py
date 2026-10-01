#!/usr/bin/env python3
"""Install the FAQ skill for one coding agent; preserve existing project files."""
import argparse
from pathlib import Path
import shutil
import sys

TARGETS = {
    'codex': ('.agents/skills/akapulu-faq', 'AGENTS.md', '$akapulu-faq'),
    'claude': ('.claude/skills/akapulu-faq', 'CLAUDE.md', '/akapulu-faq'),
    'cursor': ('.agents/skills/akapulu-faq', 'AGENTS.md', 'the akapulu-faq skill'),
}


def install(target, agent='codex'):
    if sys.version_info < (3, 10):
        raise SystemExit('Python 3.10 or newer is required. No files changed.')
    relative, instruction_name, invocation = TARGETS[agent]
    target = Path(target).expanduser().resolve()
    source = Path(__file__).resolve().parent / '.agents/skills/akapulu-faq'
    dest = target / relative
    # Inspect conflicts before writing project instructions, credentials, or files.
    if dest.exists():
        for path in source.rglob('*'):
            if path.is_file() and '__pycache__' not in path.parts:
                existing = dest / path.relative_to(source)
                if not existing.is_file() or existing.read_bytes() != path.read_bytes():
                    raise SystemExit('Existing akapulu-faq differs. Nothing overwritten; review the update first.')
        print('Identical skill already installed.')
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, dest, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    instructions = target / instruction_name
    if not instructions.exists():
        instructions.write_text(f'For website FAQ avatar work, read `{relative}/SKILL.md`.\n', encoding='utf-8')
    env = target / '.env'
    if not env.exists():
        with env.open('x', encoding='utf-8') as handle:
            handle.write('# Add your Akapulu API key locally. Never paste it into a video or commit it.\nAKAPULU_API_KEY=\n')
        env.chmod(0o600)
    ignore = target / '.gitignore'
    content = ignore.read_text(encoding='utf-8') if ignore.exists() else ''
    needed = [x for x in ('.env', 'akapulu/deployment.json', '__pycache__/') if x not in content.splitlines()]
    if needed:
        with ignore.open('a', encoding='utf-8') as handle:
            handle.write(('\n' if content and not content.endswith('\n') else '') + '\n'.join(needed) + '\n')
    print(f'Installed for {agent}: {dest}\nExisting instructions and credentials preserved.\nOpen this project in your coding agent and use {invocation} with your website URL.\nIf the skill is not listed, start a new chat or explicitly ask it to read {relative}/SKILL.md.')
    return dest


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('project')
    parser.add_argument('--agent', choices=TARGETS, default='codex', help='Coding agent used for setup (default: codex)')
    args = parser.parse_args()
    install(args.project, args.agent)
