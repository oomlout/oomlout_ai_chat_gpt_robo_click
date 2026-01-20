import re
import sys
from pathlib import Path


def extract_actions(path):
    text = Path(path).read_text(encoding='utf-8')
    # capture @action("command", ...) - robust to whitespace and extra args
    pattern = re.compile(r"@action\(\s*['\"]([^'\"]+)['\"]", re.MULTILINE)
    return set(m.group(1) for m in pattern.finditer(text))


def main(old_path, new_path):
    old = extract_actions(old_path)
    new = extract_actions(new_path)

    only_old = sorted(old - new)
    only_new = sorted(new - old)
    both = sorted(old & new)

    print(f"Old file: {old_path} -> {len(old)} actions")
    print(f"New file: {new_path} -> {len(new)} actions\n")

    print("Actions only in OLD:")
    for c in only_old:
        print(f"  - {c}")
    if not only_old:
        print("  (none)")

    print("\nActions only in NEW:")
    for c in only_new:
        print(f"  - {c}")
    if not only_new:
        print("  (none)")

    print(f"\nActions in BOTH ({len(both)}):")
    for c in both:
        print(f"  - {c}")


if __name__ == '__main__':
    old = sys.argv[1] if len(sys.argv) > 1 else 'old_1_oomlout_ai_roboclick.py'
    new = sys.argv[2] if len(sys.argv) > 2 else 'oomlout_ai_roboclick.py'
    if not Path(old).exists() or not Path(new).exists():
        print("Error: one or both files not found.")
        sys.exit(1)
    main(old, new)
