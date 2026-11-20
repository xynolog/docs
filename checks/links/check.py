#!/usr/bin/env python3
"""Every link, anchor, repository path, npm script and make target the docs name
resolves, at main of the repository that has it.

    python3 checks/links/check.py --clones DIR

Run from the root of a docs checkout; the docs are its tracked Markdown files.
Each xynolog repository they link is cloned into DIR, which must not exist
yet: at depth 1 and anonymously, as a reader reaches it, so a repository a
reader cannot open fails to clone. Then:

- every link (inline, reference definition, href and src) resolves: a
  relative one in this checkout, and never into a submodule, which GitHub
  does not show; a github.com/xynolog URL at main of the repository it names;
  and an anchor to a heading of the Markdown file it names;
- every github.com/xynolog/<repo>/(blob|tree|raw)/<ref>/<path> URL resolves
  too, a code span's included;
- a path in a code span that names a repository, by its first segment or as
  "<repo>'s `path`", is a file or directory of that repository;
- `npm run X` names a script of some package.json, and `make X` a target of
  some Makefile, of this checkout or a clone.

Each failure is printed as file:line, and any fails the run.
"""

import argparse
import fnmatch
import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote

OWNER = "xynolog"
THIS = "docs"


class Tree:
    """What git tracks at a commit: each path's kind, and the text of a file."""

    def __init__(self, kinds, read):
        self.kinds = kinds
        self._read = read

    @classmethod
    def of(cls, root):
        listing = git(root, "ls-tree", "-r", "-t", "-z", "HEAD")
        kinds = {}
        for entry in listing.split("\0"):
            if entry:
                meta, path = entry.split("\t", 1)
                kinds[path] = meta.split()[1]
        return cls(kinds, lambda path: (Path(root) / path).read_text(encoding="utf-8"))

    def kind(self, path):
        """'blob', 'tree', 'submodule:<path>' or None."""
        path = path.strip("/")
        if path in ("", "."):
            return "tree"
        if path in self.kinds:
            kind = self.kinds[path]
            return f"submodule:{path}" if kind == "commit" else kind
        parts = path.split("/")
        for i in range(1, len(parts)):
            prefix = "/".join(parts[:i])
            if self.kinds.get(prefix) == "commit":
                return f"submodule:{prefix}"
        return None

    def matches(self, pattern):
        """Whether some tracked path matches a pattern with * or {a,b} in it."""
        braced = re.fullmatch(r"(.*)\{([^}]*)\}(.*)", pattern)
        patterns = [braced[1] + alt + braced[3] for alt in braced[2].split(",")] if braced else [pattern]
        return all(any(fnmatch.fnmatchcase(path, p) for path in self.kinds) for p in patterns)

    def read(self, path):
        return self._read(path)

    def files(self, suffix=""):
        return sorted(p for p, k in self.kinds.items() if k == "blob" and p.endswith(suffix))


def git(root, *args):
    return subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True).stdout


# --- Markdown ---------------------------------------------------------------

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)", re.S)
REFDEF = re.compile(r"^[ ]{0,3}\[[^\]]+\]:[ \t]*<?(\S+?)>?(?:[ \t]+.*)?$", re.M)
HTML = re.compile(r"(?:href|src)\s*=\s*\"([^\"]+)\"")
CODE_SPAN = re.compile(r"`([^`]+)`")


def _blank(match):
    return re.sub(r"[^\n]", " ", match[0])


def prose(text):
    """The text with fenced blocks, code spans and comments blanked, lines kept."""
    lines = text.split("\n")
    fenced = False
    for i, line in enumerate(lines):
        if FENCE.match(line):
            fenced = not fenced
            lines[i] = ""
        elif fenced:
            lines[i] = ""
    body = CODE_SPAN.sub(_blank, "\n".join(lines))
    return re.sub(r"<!--.*?-->", _blank, body, flags=re.S)


def links(text):
    """(line, target) of every link, across hard wraps."""
    body = prose(text)
    found = []
    for pattern in (INLINE, REFDEF, HTML):
        for match in pattern.finditer(body):
            found.append((body.count("\n", 0, match.start(1)) + 1, match[1]))
    return sorted(found)


def code(text):
    """(line, text, what precedes it, fenced) of every code span and every fenced line."""
    fenced = False
    for number, line in enumerate(text.split("\n"), 1):
        if FENCE.match(line):
            fenced = not fenced
        elif fenced:
            yield number, line, "", True
        else:
            for match in CODE_SPAN.finditer(line):
                yield number, match[1], line[: match.start()], False


def slugs(text):
    """The anchors GitHub gives a Markdown file's headings, and its named anchors."""
    seen = {}
    found = set()
    fenced = False
    for line in text.splitlines():
        if FENCE.match(line):
            fenced = not fenced
            continue
        heading = None if fenced else re.match(r"^\s{0,3}#{1,6}\s+(.*?)\s*#*\s*$", line)
        if not heading:
            continue
        title = re.sub(r"!?\[([^\]]*)\]\([^)]*\)", r"\1", heading[1])
        title = re.sub(r"<[^>]+>", "", title)
        slug = re.sub(r"[^\w\- ]", "", title.strip().lower()).replace(" ", "-")
        if slug in seen:
            seen[slug] += 1
            found.add(f"{slug}-{seen[slug]}")
        else:
            seen[slug] = 0
            found.add(slug)
    found.update(re.findall(r"<a\s+(?:name|id)=\"([^\"]+)\"", text))
    return found


# --- What the docs name -------------------------------------------------------

REPO_URL = re.compile(rf"https?://github\.com/{OWNER}/([\w.-]+?)(?:\.git)?(?=[/#?)\s\"'`>\]<]|$)(/[^\s)\"'`>\]<|]*)?")
FILE_URL = re.compile(r"/(blob|tree|raw)/([^/]+)/([^#?]*)(?:#(.*))?")
PATH = re.compile(r"(?<![\w@./-])([\w.-]+(?:/[\w.*{},-]+)+)/?(?![\w@/-])")
REPO_OF = re.compile(r"\b([\w.-]+)'s\s*$")
COMMAND = re.compile(r"(?:^|&&|\|\||;|\|)\s*(?:\$\s+)?(make|npm run)((?:[ \t]+[^\s;&|#]+)*)")


def named_repositories(tree):
    """The xynolog repositories other than this one that the docs name."""
    names = set()
    for path in tree.files(".md"):
        names.update(m[1] for m in REPO_URL.finditer(tree.read(path)))
    names.discard(THIS)
    return sorted(names)


def commands(text):
    """(verb, name) of each `make X` and `npm run X` that starts a command."""
    for match in COMMAND.finditer(text):
        verb, words = match[1], match[2].split()
        if verb == "npm run":
            if words and not words[0].startswith(("-", "<")):
                yield verb, words[0]
            continue
        skip = False
        for word in words:
            if skip:
                skip = False
            elif word in ("-C", "-f"):
                skip = True
            elif word.startswith("-") or "=" in word:
                continue
            elif re.fullmatch(r"[a-z][\w-]*", word):
                yield verb, word
            else:
                break


def scripts(trees):
    found = set()
    for tree in trees:
        for path in tree.files("package.json"):
            if "node_modules/" not in path:
                found.update(json.loads(tree.read(path)).get("scripts", {}))
    return found


def targets(roots):
    """Every .PHONY target of each root's Makefile, as make reads it."""
    found = set()
    for root in roots:
        if (Path(root) / "Makefile").is_file():
            database = subprocess.run(
                ["make", "-pRrq", "-f", "Makefile", ":"], cwd=root, capture_output=True, text=True
            ).stdout
            for phony in re.findall(r"^\.PHONY: (.*)$", database, re.M):
                found.update(phony.split())
    return found


# --- Resolution ---------------------------------------------------------------


class Checker:
    def __init__(self, docs, repos, scripts, targets):
        self.docs = docs
        self.repos = repos
        self.scripts = scripts
        self.targets = targets
        self._slugs = {}

    def anchored(self, tree, path, anchor):
        key = (id(tree), path)
        if key not in self._slugs:
            self._slugs[key] = slugs(tree.read(path))
        return unquote(anchor) in self._slugs[key]

    def target(self, tree, path, anchor, where):
        """Why [path#anchor] does not resolve in [tree], or None."""
        kind = tree.kind(path)
        if kind is None:
            return f"names {path}, which {where} does not have"
        if kind.startswith("submodule:"):
            sub = kind.split(":", 1)[1]
            return f"names {path}, inside the {sub} submodule, which GitHub does not show; link {OWNER}/{sub}"
        if anchor and kind == "blob" and path.endswith(".md") and not self.anchored(tree, path, anchor):
            return f"names #{anchor}, which no heading of {path} in {where} has"
        return None

    def url(self, name, rest):
        tree = self.docs if name == THIS else self.repos[name]
        where = f"{OWNER}/{name}"
        file = FILE_URL.fullmatch(rest.rstrip(".,;:"))
        if not file:
            return None
        _, ref, path, anchor = file.groups()
        if ref != "main":
            return f"names {ref} of {where}; the docs link main"
        return self.target(tree, unquote(path), anchor, where)

    def link(self, file, target):
        repo = REPO_URL.fullmatch(target)
        if repo:
            return self.url(repo[1], repo[2] or "")
        if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
            return None
        path, _, anchor = target.partition("#")
        if not path:
            if anchor and not self.anchored(self.docs, file, anchor):
                return f"names #{anchor}, which no heading of this file has"
            return None
        path = unquote(path.split("?")[0])
        if path.startswith("/"):
            resolved = path.lstrip("/")
        else:
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(file), path))
        if resolved.startswith(".."):
            return f"names {target}, outside this repository; link the repository that has it"
        return self.target(self.docs, resolved, anchor, "this repository")

    def path(self, token, before):
        """Why a code span's [token] does not resolve; None when it names no repository."""
        if "<" in token:
            return None
        owner = REPO_OF.search(before)
        if owner and owner[1] in self.repos:
            name, path = owner[1], token
        else:
            first, _, path = token.partition("/")
            if first not in self.repos or self.docs.kind(first) == "tree":
                return None
            name = first
        tree = self.repos[name]
        found = tree.matches(path.rstrip("/")) if re.search(r"[*{]", path) else tree.kind(path) is not None
        return None if found else f"names {token}, which {OWNER}/{name} does not have"

    def command(self, verb, name):
        if verb == "npm run" and name not in self.scripts:
            return f"runs npm script {name}, which no package.json has"
        if verb == "make" and name not in self.targets:
            return f"runs make {name}, which no Makefile has"
        return None

    def check(self):
        failures = set()
        for file in self.docs.files(".md"):
            text = self.docs.read(file)
            for line, target in links(text):
                failures.add((file, line, self.link(file, target)))
            for line, snippet, before, fenced in code(text):
                for verb, name in commands(snippet):
                    failures.add((file, line, self.command(verb, name)))
                if not fenced:
                    for match in PATH.finditer(snippet):
                        failures.add((file, line, self.path(match[1], before)))
            for match in REPO_URL.finditer(text):
                line = text.count("\n", 0, match.start()) + 1
                failures.add((file, line, self.url(match[1], match[2] or "")))
        return sorted(f for f in failures if f[2])


def clone(names, into):
    """Clone each repository as a reader reaches it; why each that does not clone failed."""
    into.mkdir(parents=True)
    anonymous = {**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "", "SSH_ASKPASS": ""}
    refused = []
    for name in names:
        cloned = subprocess.run(
            ["git", "-c", "credential.helper=", "clone", "--quiet", "--depth", "1",
             f"https://github.com/{OWNER}/{name}.git", str(into / name)],
            capture_output=True, text=True, env=anonymous,
        )
        if cloned.returncode != 0:
            refused.append(f"{OWNER}/{name} does not clone anonymously, so a reader cannot open what the docs link there")
    return refused


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--clones", type=Path, required=True, help="where to clone the named repositories; must not exist")
    into = parser.parse_args().clones
    if into.exists():
        sys.exit(f"{into} exists; the check clones into a directory of its own")
    docs = Tree.of(".")
    names = named_repositories(docs)
    refused = clone(names, into)
    if refused:
        sys.exit("\n".join(refused))
    repos = {name: Tree.of(into / name) for name in names}
    checker = Checker(docs, repos, scripts([docs, *repos.values()]), targets([".", *(into / n for n in names)]))
    failures = checker.check()
    if failures:
        sys.exit("\n".join(f"{file}:{line}: {why}" for file, line, why in failures))
    print(f"Every link, anchor, repository path, npm script and make target resolves, in {OWNER}/{THIS} and {', '.join(names)}")


if __name__ == "__main__":
    main()
