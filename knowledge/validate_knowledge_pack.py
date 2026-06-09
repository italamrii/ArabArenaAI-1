#!/usr/bin/env python3
"""Validate Saudi Knowledge Pack v1 manifest and document coverage."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from knowledge.pack_loader import validate_knowledge_pack


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate Saudi Knowledge Pack v1")
    parser.add_argument(
        "--manifest",
        default=None,
        help="Path to manifest JSON (default: knowledge/manifests/saudi_knowledge_pack_v1.json)",
    )
    parser.add_argument(
        "--knowledge-root",
        default=None,
        help="Path to knowledge/ directory",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    knowledge_root = Path(args.knowledge_root) if args.knowledge_root else None
    manifest_path = Path(args.manifest) if args.manifest else None

    report = validate_knowledge_pack(
        knowledge_root=knowledge_root,
        manifest_path=manifest_path,
    )

    print(f"manifest={report.manifest_path}")
    print(f"ok={report.ok}")
    print(f"domains={report.domains_registered}")
    print(f"sources={report.sources_count}")
    print(f"documents_checked={report.documents_checked}")

    if report.issues:
        print("issues:")
        for issue in report.issues:
            prefix = f"[{issue.source_id}] " if issue.source_id else ""
            print(f"  - {issue.code}: {prefix}{issue.message}")
        return 1

    print("validation=passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
