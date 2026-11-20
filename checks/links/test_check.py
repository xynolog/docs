"""The link check's own cases: python3 -m unittest discover -s checks/links"""

import unittest

from check import Checker, Tree, code, commands, links, slugs


def tree(files, submodules=()):
    kinds = {}
    for path in files:
        parts = path.split("/")
        for i in range(1, len(parts)):
            kinds["/".join(parts[:i])] = "tree"
        kinds[path] = "blob"
    for path in submodules:
        kinds[path] = "commit"
    return Tree(kinds, files.__getitem__)


def checker(docs, repos=None, scripts=(), targets=()):
    return Checker(tree(docs, ("build-tools",)), {n: tree(f) for n, f in (repos or {}).items()}, set(scripts), set(targets))


class Slugs(unittest.TestCase):
    def test_a_heading_is_its_text_lowered_and_hyphened(self):
        self.assertIn("calls-to-the-archivist", slugs("## Calls to the Archivist\n"))

    def test_punctuation_and_code_go_and_links_keep_their_text(self):
        self.assertIn("jobcreate", slugs("## `job:create`\n"))
        self.assertIn("see-the-spec", slugs("### See [the spec](x.md)\n"))

    def test_a_repeated_heading_is_numbered(self):
        self.assertEqual(slugs("# Usage\n## Usage\n"), {"usage", "usage-1"})

    def test_a_heading_in_a_fence_is_none(self):
        self.assertEqual(slugs("```\n# not a heading\n```\n"), set())


class Links(unittest.TestCase):
    def test_a_link_wrapped_across_lines_is_found_on_its_target_line(self):
        self.assertEqual(links("see [the\nguide](a/b.md) here"), [(2, "a/b.md")])

    def test_a_fence_and_a_code_span_hold_no_link(self):
        self.assertEqual(links("```\n[x](gone.md)\n```\n`[y](gone.md)`\n"), [])

    def test_reference_definitions_and_html_are_links(self):
        self.assertEqual(links('[a]: ref.md\n<img src="i.svg">\n'), [(1, "ref.md"), (2, "i.svg")])


class Commands(unittest.TestCase):
    def test_make_and_npm_run_at_a_command_start(self):
        self.assertEqual(list(commands("make -C sdk generate check-generated")), [("make", "generate"), ("make", "check-generated")])
        self.assertEqual(list(commands("cd e2e && npm run test:slow")), [("npm run", "test:slow")])

    def test_make_in_a_comment_or_mid_sentence_is_not_a_command(self):
        self.assertEqual(list(commands("xynolog settings config x   # make it the default")), [])
        self.assertEqual(list(commands("this would make sense")), [])

    def test_variables_and_placeholders_name_no_target(self):
        self.assertEqual(list(commands("make SDK_ARTIFACTS=/tmp test")), [("make", "test")])
        self.assertEqual(list(commands("npm run <script>")), [])


class Resolution(unittest.TestCase):
    def test_a_relative_link_resolves_in_this_checkout_with_its_anchor(self):
        c = checker({"a/x.md": "[g](../b.md#two)\n", "b.md": "## Two\n"})
        self.assertEqual(c.check(), [])

    def test_a_missing_file_and_a_missing_anchor_fail(self):
        c = checker({"x.md": "[g](gone.md) [h](y.md#nope)\n", "y.md": "# Yes\n"})
        self.assertEqual(
            [why for _, _, why in c.check()],
            ["names #nope, which no heading of y.md in this repository has", "names gone.md, which this repository does not have"],
        )

    def test_a_link_into_a_submodule_fails(self):
        c = checker({"x.md": "[t](build-tools/advisories.py)\n"})
        self.assertIn("inside the build-tools submodule", c.check()[0][2])

    def test_a_link_outside_the_checkout_fails(self):
        c = checker({"d/x.md": "[t](../../images/README.md)\n"})
        self.assertIn("outside this repository", c.check()[0][2])

    def test_a_url_resolves_at_main_of_its_repository(self):
        docs = {"x.md": "[s](https://github.com/xynolog/protocol/blob/main/specs/a.json) [t](https://github.com/xynolog/protocol/tree/main/gone)\n"}
        c = checker(docs, {"protocol": {"specs/a.json": "{}"}})
        self.assertEqual([why for _, _, why in c.check()], ["names gone, which xynolog/protocol does not have"])

    def test_a_url_of_another_ref_fails(self):
        c = checker({"x.md": "[s](https://github.com/xynolog/protocol/blob/v1/a.json)\n"}, {"protocol": {"a.json": "{}"}})
        self.assertEqual(c.check()[0][2], "names v1 of xynolog/protocol; the docs link main")

    def test_a_code_span_path_that_names_a_repository_resolves_there(self):
        docs = {"x.md": "`protocol/specs/a.json`, `protocol/gone.json`, sdk's `go/api`, `notarepo/x.y`\n"}
        c = checker(docs, {"protocol": {"specs/a.json": "{}"}, "sdk": {"go/api/types.go": ""}})
        self.assertEqual([why for _, _, why in c.check()], ["names protocol/gone.json, which xynolog/protocol does not have"])

    def test_a_script_and_a_target_must_exist(self):
        c = checker({"x.md": "`npm run gone` `npm run there` `make gone` `make there`\n"}, scripts={"there"}, targets={"there"})
        self.assertEqual(
            [why for _, _, why in c.check()],
            ["runs make gone, which no Makefile has", "runs npm script gone, which no package.json has"],
        )


if __name__ == "__main__":
    unittest.main()
