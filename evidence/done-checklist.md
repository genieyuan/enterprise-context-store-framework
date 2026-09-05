# Publication disclosure fix — completion evidence

- [x] Scope: publication scanner ignores generated caches/bytecode and common build artifacts.
- [x] Disclosure protection retained: publishable files remain scanned for both private markers.
- [x] Regression: `test_private_marker_in_publishable_content_fails` detects a real sentinel in `docs/leak.md`.
- [x] Local full suite: `python3 -m pytest -q` → 3 passed.
- [x] Formatting: `git diff --check` passed.
- [x] Commit: `3585eb21e7a92a3db3f4f81b163710651fe26234`.
- [x] GitHub CI: run 33942435452, https://github.com/genieyuan/enterprise-context-store-framework/actions/runs/33942435452, success.
- [x] Anonymous clone and raw fetch succeeded; framework visibility is public.
- [x] `genieyuan/enterprise-context-store` verified PRIVATE and unchanged at `38a53f3c5a44599b29f05b9e4eca7102c99ef6ff`.
