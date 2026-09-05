from pathlib import Path
import tempfile

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
 for p in ['README.md','docs/framework/phase-1.md','docs/framework/lifecycle.md','docs/framework/capture.md','docs/framework/compile.md','docs/reference-architecture.md','docs/falsification-criteria.md','docs/decisions.md','docs/roadmap.md','LICENSE','LICENSE-DOCS','LICENSE-CODE','SECURITY.md']:
  assert (ROOT/p).exists(), p
