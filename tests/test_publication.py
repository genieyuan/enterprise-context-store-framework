from pathlib import Path
import tempfile
import re

ROOT=Path(__file__).parents[1]

_NON_PUBLISHABLE_DIRS={'.git', '.pytest_cache', '__pycache__', '.mypy_cache',
                       '.ruff_cache', '.tox', '.venv', 'venv', 'build', 'dist',
                       'coverage', 'htmlcov', 'node_modules'}
_NON_PUBLISHABLE_SUFFIXES={'.pyc', '.pyo', '.class', '.o', '.so', '.dylib',
                           '.a', '.gcda', '.gcno'}

def _publishable_files(root=ROOT):
    """Yield repository content that could be included in a publication."""
    for path in root.rglob('*'):
        if not path.is_file():
            continue
        relative=path.relative_to(root)
        if any(part in _NON_PUBLISHABLE_DIRS or part == 'tests' for part in relative.parts):
            continue
        if path.suffix.lower() in _NON_PUBLISHABLE_SUFFIXES:
            continue
        yield path

def _private_markers(root=ROOT):
    content='\n'.join(path.read_text(errors='ignore') for path in _publishable_files(root))
    return [marker for marker in ['private-source-path-marker', 'private-network-marker']
            if marker.lower() in content.lower()]

def test_no_private_markers():
 assert _private_markers() == []

def test_private_marker_in_publishable_content_fails():
 with tempfile.TemporaryDirectory() as directory:
  root=Path(directory)
  (root/'docs').mkdir()
  (root/'docs'/'leak.md').write_text('private-network-marker')
  assert _private_markers(root) == ['private-network-marker']

def test_required_docs():
 for p in ['README.md','docs/framework/cover-page.md','docs/framework/phase-1.md','docs/framework/lifecycle.md','docs/framework/capture.md','docs/framework/compile.md','docs/reference-architecture.md','docs/falsification-criteria.md','docs/decisions.md','docs/roadmap.md','LICENSE','LICENSE-DOCS','LICENSE-CODE','SECURITY.md']:
  assert (ROOT/p).exists(), p

def test_public_lifecycle_is_canonical_and_has_no_preserve_stage():
 lifecycle=(ROOT/'docs/framework/lifecycle.md').read_text()
 canonical='Capture → Compile → Serve → Continuous Learning'
 assert canonical in lifecycle
 assert not re.search(r'Capture\s*→\s*Preserve\s*→', lifecycle)
 assert 'five lifecycle stages' not in lifecycle

def test_phase_one_uses_compile_not_store_as_a_lifecycle_stage():
 phase=(ROOT/'docs/framework/phase-1.md').read_text()
 assert 'Capture → Compile → Serve → Continuous Learning' in phase
 assert all(stage in phase for stage in ['1. CAPTURE', '2. COMPILE', '3. SERVE', '4. CONTINUOUS LEARNING'])
 assert '### 3.2 Compile' in phase
 assert 'The three stages inside the store' not in phase
 assert not re.search(r'Capture\s*→\s*Store\s*→\s*Serve', phase, re.I)

def test_publication_docs_do_not_reintroduce_stale_storage_lifecycle_wording():
    stale = re.compile(r'from capture,?\s+through storage,?\s+to consumption', re.I)
    offenders = []
    for path in _publishable_files():
        if path.suffix.lower() not in {'.md', '.rst', '.txt'}:
            continue
        if stale.search(path.read_text(errors='ignore')):
            offenders.append(str(path.relative_to(ROOT)))
    assert offenders == []

def test_phase_one_lifecycle_has_four_first_class_stages_and_cross_cutting_trust():
 phase=(ROOT/'docs/framework/phase-1.md').read_text()
 diagram=phase.split('### The lifecycle stages inside the store', 1)[1].split('### 3.1 Capture', 1)[0]
 assert re.search(r'1\. CAPTURE\s+│──▶│ 2\. COMPILE\s+│──▶│ 3\. SERVE\s+│──▶│ 4\. CONTINUOUS LEARNING', diagram)
 assert '### 3.4 Continuous Learning' in phase
 assert 'Continuous Learning is a first-class lifecycle stage' in phase
 assert re.search(r'Governance & Trust — cross-cutting across Capture, Compile, Serve and Continuous.*Learning', diagram, re.I | re.S)
 assert 'Governance & Trust is not a fifth lifecycle stage' in phase
 assert 'through storage' not in phase.lower()

def test_public_cover_preserves_approved_framework_content():
 cover=(ROOT/'docs/framework/cover-page.md').read_text()
 required_sections=[
  '## The problem ECS addresses',
  '## What the ECS framework does',
  '## Why ECS matters',
  '## How an enterprise can leverage ECS',
  '## Who should apply the framework',
  '## When ECS is most relevant',
  '## How success should be measured',
  '## Current maturity and scope',
  '## Closing statement',
 ]
 for section in required_sections:
  assert section in cover
 assert 'AI-native SaaS reduces context gaps inside each application.' in cover
 assert 'ECS should be adopted as a framework' in cover
 assert 'AI agents are the consumers of the context ECS serves.' in cover
 assert 'unsupported assumptions per AI task' in cover
 assert 'technology-agnostic, pre-product framework' in cover
 assert 'The first generation of enterprise AI connected models to data.' in cover
 assert '[CC BY 4.0](../../LICENSE-DOCS)' in cover

def test_public_navigation_and_lifecycle_terms():
 readme=(ROOT/'README.md').read_text()
 assert '[Framework cover page](docs/framework/cover-page.md)' in readme
 for name in ['phase-1.md','lifecycle.md','capture.md','compile.md','../reference-architecture.md']:
  text=(ROOT/'docs/framework'/name).read_text()
  assert 'Capture → Compile → Serve → Continuous Learning' in text
  assert 'Governance & Trust' in text

def test_cover_page_is_public_and_cc_by_licensed():
 cover=(ROOT/'docs/framework/cover-page.md').read_text()
 assert not cover.startswith('---')
 assert 'CC BY 4.0' in cover
 assert 'vault' not in cover.lower()
 assert '/Users/' not in cover

def test_exact_public_manifest_has_no_private_artifact():
 forbidden={'evidence/done-checklist.md'}
 assert forbidden.isdisjoint({str(p.relative_to(ROOT)) for p in _publishable_files()})
