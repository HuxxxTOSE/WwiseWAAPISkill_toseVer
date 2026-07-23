#!/usr/bin/env python3
"""Search / retrieve Wwise C++ SDK 2024.1.13 (Windows) reference docs.

The corpus is a JSONL file where every line is a JSON object {"text": "..."}
holding one Markdown documentation page. This tool lets the agent locate the
few relevant pages (search) and then pull their full text (get) WITHOUT loading
the ~19 MB file into context.

Record ID == 1-based line number in the JSONL file.

Performance model
-----------------
A sidecar index (``<corpus>.idx``, JSON) is built once and reused. It stores,
per record: byte offset + length (so ``--get`` seeks directly instead of
scanning) and pre-computed page type / title / breadcrumb (so those heuristics
run at build time, not per query). The index auto-rebuilds when the corpus size
or mtime changes. Substring search memory-maps the corpus and pre-filters on
raw bytes, decoding (``json.loads``) only the handful of candidate records that
already contain every term -- instead of parsing all ~9,400 lines each query.

Usage
-----
  # keyword search (all terms must match, case-insensitive substring by default)
  python search.py IAkPlugin factory

  # regex search
  python search.py --regex "AK_STATIC_LINK_PLUGIN\\(.*\\)"

  # filter by page type and/or owning header file
  python search.py Malloc --type FileReference
  python search.py Realloc --file AkAllocator.h

  # limit / snippet controls
  python search.py Volume --limit 30 --context 200

  # retrieve full text of one or more pages by ID
  python search.py --get 4
  python search.py --get 4,6,12

  # force a fresh index (normally automatic)
  python search.py --rebuild-index

  # flag ak.* URIs in a doc that no longer exist in the corpus (drift check)
  python search.py --drift-check references/waapi-procedures.md
"""
import argparse
import json
import os
import re
import sys

try:  # ensure UTF-8 output regardless of console codepage (e.g. Windows cp936)
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

DATA = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    "data", "WwiseSDK-Windows.jsonl")
INDEX = DATA + ".idx"
INDEX_VERSION = 2

# Page-type taxonomy (also the allowed values for --type).
_REF_SUFFIXES = ("File Reference", "Class Reference", "Struct Reference",
                 "Namespace Reference", "Union Reference")
_TYPE_CHOICES = ["FileReference", "ClassReference", "StructReference",
                 "NamespaceReference", "UnionReference", "MemberDetail",
                 "SourceListing", "Procedure", "other"]

_PROC_RE = re.compile(r"^ak\.(?:wwise|soundengine)\.[\w.]+$")


# --------------------------------------------------------------------------- #
# Page classification / titling (run once at index-build time, then cached).
# --------------------------------------------------------------------------- #
def _member_line(lines):
    """Return the '# ◆ Name' detail-header line if present (scans whole page)."""
    for ln in lines:
        s = ln.strip()
        if s.startswith("# \u25c6"):
            return s
    return None


def breadcrumb(lines):
    """Collect the '* X' breadcrumb bullets near the top."""
    crumbs = []
    for ln in lines[:16]:
        s = ln.strip()
        if s.startswith("* "):
            crumbs.append(s[2:].strip())
        elif crumbs and not s:
            break
    return crumbs


def classify(lines):
    """Return the page type. Scans a generous window so classification does not
    depend on the exact header position (more robust than peeking at line 0)."""
    head = lines[:24]
    for ln in head:
        s = ln.strip()
        if s == "Go to the documentation of this file.":
            return "SourceListing"
        for suf in _REF_SUFFIXES:
            if s.endswith(suf):
                return suf.replace(" ", "")  # "File Reference" -> "FileReference"
    # WAAPI / sound-engine procedure page: an ak.* URI used as the title/heading.
    for ln in head:
        s = ln.strip().lstrip("# ").strip()
        if _PROC_RE.match(s):
            return "Procedure"
    if _member_line(lines):
        return "MemberDetail"
    return "other"


def title(lines, ptype, crumbs):
    """Deterministic short title for a result line, keyed off the page type."""
    if ptype == "MemberDetail":
        m = _member_line(lines)
        if m:
            return m.lstrip("# ").strip()
    elif ptype == "SourceListing":
        for i, ln in enumerate(lines):
            if ln.strip() == "Go to the documentation of this file." and i > 0:
                return lines[i - 1].strip() + " (source)"
    elif ptype in ("FileReference", "ClassReference", "StructReference",
                   "NamespaceReference", "UnionReference"):
        for ln in lines[:24]:
            s = ln.strip()
            if s.endswith(_REF_SUFFIXES):
                return s
    elif ptype == "Procedure":
        for ln in lines[:24]:
            s = ln.strip().lstrip("# ").strip()
            if _PROC_RE.match(s):
                return s
    if crumbs:
        return " / ".join(crumbs)
    # Fallback: first real content line after the version header / '---'.
    for ln in lines[1:24]:
        s = ln.strip()
        if not s or s == "---" or s.startswith(("* ", "#", "|")):
            continue
        return s[:100]
    return "(untitled)"


# --------------------------------------------------------------------------- #
# Index build / load.  Records: [id, offset, length, ptype, title, crumbs].
# --------------------------------------------------------------------------- #
def _build_records(blob):
    """Build the record index from the raw file bytes (single pass)."""
    records = []
    offset = 0
    lineno = 0
    for raw in blob.splitlines(keepends=True):
        lineno += 1
        length = len(raw)
        stripped = raw.strip()
        if stripped:
            try:
                obj = json.loads(stripped.decode("utf-8"))
                text = obj.get("text", "")
            except Exception:
                text = None
            if text:
                lines = text.split("\n")
                ptype = classify(lines)
                crumbs = breadcrumb(lines)
                records.append([lineno, offset, length, ptype,
                                title(lines, ptype, crumbs), " / ".join(crumbs)])
        offset += length
    return records


def load_index(blob, force_rebuild=False):
    """Return (records, by_id). Rebuild + persist when stale or forced."""
    st = os.stat(DATA)
    meta = {"version": INDEX_VERSION, "size": st.st_size, "mtime": int(st.st_mtime)}
    if not force_rebuild and os.path.exists(INDEX):
        try:
            with open(INDEX, "r", encoding="utf-8") as f:
                cached = json.load(f)
            if all(cached.get(k) == v for k, v in meta.items()):
                recs = cached["records"]
                return recs, {r[0]: r for r in recs}
        except Exception:
            pass
    records = _build_records(blob)
    try:
        with open(INDEX, "w", encoding="utf-8") as f:
            json.dump({**meta, "records": records}, f, ensure_ascii=False)
    except Exception:
        pass  # read-only location: fall back to building in memory each run
    return records, {r[0]: r for r in records}


def _decode(blob, offset, length):
    """Decode the record body stored at [offset, offset+length)."""
    return json.loads(blob[offset:offset + length].decode("utf-8")).get("text", "")


# --------------------------------------------------------------------------- #
# Matching.
# --------------------------------------------------------------------------- #
def _raw_safe(term):
    """A term is pre-filterable on raw JSON bytes only if it survives JSON
    escaping unchanged (plain ASCII, no quote/backslash)."""
    return term.isascii() and '"' not in term and "\\" not in term


def make_snippet(text, matcher, context):
    """Return a one-line snippet around the first match."""
    m = matcher(text)
    if not m:
        return ""
    start = max(0, m.start() - context // 2)
    end = min(len(text), m.end() + context // 2)
    snip = re.sub(r"\s+", " ", text[start:end].replace("\n", " ")).strip()
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return prefix + snip + suffix


def _substring_matcher(terms, ignore_case):
    """Return (first_match_fn, all_match_fn) over decoded text."""
    lowered = [t.lower() for t in terms] if ignore_case else terms

    # Lightweight match object (start/end) without regex overhead.
    class _M:
        __slots__ = ("_s", "_e")

        def __init__(self, s, e):
            self._s, self._e = s, e

        def start(self):
            return self._s

        def end(self):
            return self._e

    def first(text):
        hay = text.lower() if ignore_case else text
        idx = hay.find(lowered[0])
        return _M(idx, idx + len(lowered[0])) if idx >= 0 else None

    def all_match(text):
        hay = text.lower() if ignore_case else text
        return all(t in hay for t in lowered)

    return first, all_match


def search(args, blob, records):
    """Yield result tuples (id, ptype, crumbs_list, title, snippet)."""
    type_filter = args.type
    file_filter = args.file.lower() if args.file else None
    limit = args.limit
    ignore_case = not args.case_sensitive

    if args.regex:
        pat = re.compile(args.terms[0], 0 if args.case_sensitive else re.IGNORECASE)
        first_fn = pat.search
        match_fn = lambda text: pat.search(text) is not None  # noqa: E731
        pre_terms = []  # regex cannot be pre-filtered on raw bytes
    elif args.terms:
        first_fn, match_fn = _substring_matcher(args.terms, ignore_case)
        # Raw-byte pre-filter with the JSON-safe terms; the precise matcher on
        # decoded text still confirms every term (incl. unsafe ones) afterwards.
        haystack = blob.lower() if ignore_case else blob
        safe = [t for t in args.terms if _raw_safe(t)]
        pre_terms = [(t.lower() if ignore_case else t).encode("ascii") for t in safe]
    else:
        # No query terms: match everything, rely on --type / --file filters.
        first_fn = lambda text: None            # noqa: E731  (no snippet anchor)
        match_fn = lambda text: True            # noqa: E731
        pre_terms = []

    results = []
    for rid, off, length, ptype, ttl, crumbs in records:
        if type_filter and ptype != type_filter:
            continue
        if file_filter and file_filter not in ttl.lower() and file_filter not in crumbs.lower():
            continue
        if pre_terms:
            end = off + length
            if any(haystack.find(pb, off, end) < 0 for pb in pre_terms):
                continue
        text = _decode(blob, off, length)
        if not match_fn(text):
            continue
        results.append((rid, ptype, crumbs.split(" / ") if crumbs else [],
                        ttl, make_snippet(text, first_fn, args.context)))
        if len(results) >= limit:
            break
    return results


# --------------------------------------------------------------------------- #
# Commands.
# --------------------------------------------------------------------------- #
def cmd_get(ids, blob, by_id):
    for rid in ids:
        entry = by_id.get(rid)
        if entry is None:
            print(f"# [id {rid}] NOT FOUND\n", file=sys.stderr)
            continue
        print(f"===== id {rid} =====")
        print(_decode(blob, entry[1], entry[2]))
        print()


def cmd_drift_check(md_path, records):
    """Report ak.* URIs referenced in a markdown file that no longer correspond
    to a procedure page in the corpus (i.e. renamed/removed/typo'd)."""
    corpus = set()
    for rid, off, length, ptype, ttl, cr in records:
        if ptype == "Procedure":
            corpus.add(ttl.strip())
    try:
        md = open(md_path, "r", encoding="utf-8").read()
    except OSError as exc:
        print(f"cannot read {md_path}: {exc}", file=sys.stderr)
        sys.exit(2)
    uris = sorted(set(re.findall(r"ak\.(?:wwise|soundengine)\.[A-Za-z0-9_.]+", md)))
    # A token that is a parent namespace of some real procedure (e.g. `ak.wwise.core`,
    # a prefix of `ak.wwise.core.object.get`) is prose, not a missing procedure.
    missing = [u for u in uris
               if u not in corpus and not any(c.startswith(u + ".") for c in corpus)]
    print(f"{md_path}: {len(uris)} ak.* tokens, {len(corpus)} procedure pages in corpus")
    if not missing:
        print("OK - every procedure URI referenced exists in the corpus.")
        return
    print(f"DRIFT - {len(missing)} URI(s) not found as a procedure page "
          f"(renamed/removed/typo, or verify via live getSchema):")
    for u in missing:
        print(f"  {u}")
    sys.exit(1)


def cmd_search(args, blob, records):
    if args.regex and not args.terms:
        print("error: --regex requires a pattern term", file=sys.stderr)
        sys.exit(2)
    if args.regex and len(args.terms) > 1:
        print(f"warning: --regex uses only the first term as the pattern; "
              f"ignoring {len(args.terms) - 1} extra term(s): {args.terms[1:]}",
              file=sys.stderr)
    results = search(args, blob, records)
    if not results:
        print("No matches.")
        return
    print(f"{len(results)} match(es) (showing up to --limit {args.limit}):\n")
    for rid, ptype, crumbs, ttl, snip in results:
        print(f"[id {rid}] ({ptype}) {ttl}")
        if crumbs:
            print(f"    path: {' / '.join(crumbs)}")
        if snip:
            print(f"    ...  {snip}")
        print()
    print("Use:  python search.py --get <id>   to read a full page.")


def main():
    p = argparse.ArgumentParser(description="Search Wwise C++ SDK 2024.1.13 docs.")
    p.add_argument("terms", nargs="*", help="search terms (AND). With --regex, first term is the pattern.")
    p.add_argument("--regex", action="store_true", help="treat the query as a regular expression")
    p.add_argument("--case-sensitive", action="store_true", help="case-sensitive matching")
    p.add_argument("--type", choices=_TYPE_CHOICES, help="restrict to a page type")
    p.add_argument("--file", help="restrict to pages whose title/path contains this (e.g. AkAllocator.h)")
    p.add_argument("--limit", type=int, default=25, help="max results (default 25)")
    p.add_argument("--context", type=int, default=160, help="snippet width in chars (default 160)")
    p.add_argument("--get", help="comma-separated record IDs to print in full")
    p.add_argument("--rebuild-index", action="store_true", help="force a fresh sidecar index")
    p.add_argument("--drift-check", metavar="FILE",
                   help="report ak.* URIs in FILE that no longer exist in the corpus")
    args = p.parse_args()

    if not os.path.exists(DATA):
        print(f"Data file not found: {DATA}", file=sys.stderr)
        sys.exit(2)

    with open(DATA, "rb") as f:
        blob = f.read()
    records, by_id = load_index(blob, force_rebuild=args.rebuild_index)

    if args.drift_check:
        cmd_drift_check(args.drift_check, records)
        return

    if args.rebuild_index and not (args.terms or args.get or args.type or args.file):
        print(f"Index rebuilt: {len(records)} records -> {INDEX}")
        return

    if args.get:
        try:
            ids = [int(x) for x in args.get.split(",") if x.strip()]
        except ValueError:
            print("--get expects comma-separated integers", file=sys.stderr)
            sys.exit(2)
        cmd_get(ids, blob, by_id)
        return

    if not args.terms and not args.type and not args.file:
        p.print_help()
        sys.exit(1)
    cmd_search(args, blob, records)


if __name__ == "__main__":
    main()
