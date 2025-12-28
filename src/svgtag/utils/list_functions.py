# scan_py_funcs_to_txt.py
# Usage:
#   python scan_py_funcs_to_txt.py "C:\TOOLS\perso\svgtag\src" "report.txt"
# If args omitted: root = current folder, out = "py_functions_report.txt"

from __future__ import annotations
from pathlib import Path
import ast
import sys

SEP_FILE = "\n" + "=" * 100 + "\n"
SEP_FUNC = "\n" + "-" * 100 + "\n"

def safe_read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")

def fmt_default(expr):
    if expr is None:
        return None
    try:
        return ast.unparse(expr)  # Python 3.9+
    except Exception:
        return "<default>"

def fmt_signature(args: ast.arguments) -> str:
    parts = []

    # Positional-only args (py3.8+)
    posonly = getattr(args, "posonlyargs", [])
    normal = list(args.args)

    # Defaults align to last N of (posonly + normal)
    all_pos = list(posonly) + normal
    defaults = list(args.defaults or [])
    pad = [None] * (len(all_pos) - len(defaults)) + defaults

    for a, d in zip(all_pos, pad):
        s = a.arg
        dv = fmt_default(d)
        if dv is not None:
            s += f"={dv}"
        parts.append(s)

    if posonly:
        # insert "/" after posonly args
        parts.insert(len(posonly), "/")

    # *args or bare *
    if args.vararg is not None:
        parts.append(f"*{args.vararg.arg}")
    elif args.kwonlyargs:
        parts.append("*")

    # kw-only
    kw_defaults = list(args.kw_defaults or [])
    for a, d in zip(args.kwonlyargs, kw_defaults):
        s = a.arg
        dv = fmt_default(d)
        if dv is not None:
            s += f"={dv}"
        parts.append(s)

    # **kwargs
    if args.kwarg is not None:
        parts.append(f"**{args.kwarg.arg}")

    return "(" + ", ".join(parts) + ")"

def collect_defs(tree: ast.AST):
    """
    Returns list of tuples: (kind, qualname, lineno, signature, docstring)
    kind: "function" or "method"
    """
    out = []
    for node in getattr(tree, "body", []):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node) or ""
            out.append(("function", node.name, node.lineno, fmt_signature(node.args), doc))
        elif isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    doc = ast.get_docstring(sub) or ""
                    qn = f"{node.name}.{sub.name}"
                    out.append(("method", qn, sub.lineno, fmt_signature(sub.args), doc))
    return out

def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("py_functions_report.txt")

    py_files = sorted([p for p in root.rglob("*.py") if p.is_file()])

    lines = []
    lines.append(f"ROOT: {root.resolve()}\n")
    lines.append(f"FILES FOUND: {len(py_files)}\n")
    lines.append("PY FILE LIST:\n")
    for p in py_files:
        lines.append(f"  - {p.resolve()}")
    lines.append("\n")

    for p in py_files:
        text = safe_read(p)
        try:
            tree = ast.parse(text, filename=str(p))
        except SyntaxError as e:
            lines.append(SEP_FILE)
            lines.append(f"FILE: {p.resolve()}\n")
            lines.append(f"[SYNTAX ERROR] {e}\n")
            continue

        defs = collect_defs(tree)

        lines.append(SEP_FILE)
        lines.append(f"FILE: {p.resolve()}\n")
        lines.append(f"DEFS FOUND: {len(defs)}\n")

        if not defs:
            lines.append("(no top-level functions or class methods found)\n")
            continue

        for kind, name, lineno, sig, doc in defs:
            lines.append(SEP_FUNC)
            lines.append(f"{kind.upper()}: {name}{sig}\n")
            lines.append(f"LINE: {lineno}\n")
            lines.append("DOCSTRING:\n")
            lines.append((doc.strip() if doc.strip() else "(none)") + "\n")

    out_path.write_text("".join(lines), encoding="utf-8")
    print(f"OK -> wrote: {out_path.resolve()}")

if __name__ == "__main__":
    main()