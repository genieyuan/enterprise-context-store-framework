from pathlib import Path
ROOT=Path(__file__).parents[1]
def test_no_private_markers():
 s='\n'.join(p.read_text(errors='ignore') for p in ROOT.rglob('*') if p.is_file() and '.git' not in p.parts and p.parent.name != 'tests')
 for x in ['private-source-path-marker','private-network-marker']:
  assert x.lower() not in s.lower(), x
def test_required_docs():
 for p in ['README.md','docs/framework/phase-1.md','docs/framework/lifecycle.md','docs/framework/capture.md','docs/framework/compile.md','docs/reference-architecture.md','docs/falsification-criteria.md','docs/decisions.md','docs/roadmap.md','LICENSE','LICENSE-DOCS','LICENSE-CODE','SECURITY.md']:
  assert (ROOT/p).exists(), p
