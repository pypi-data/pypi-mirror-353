# system modules
import unittest
import json
import subprocess

# internal modules
import json2tex


class Json2TexTest(unittest.TestCase):
    maxDiff = None

    def test_atomic(self):
        self.assertSequenceEqual(
            list(json2tex.json2texcommands(d := "bla")),
            [rf"\newcommand{{\Unnamed}}{{{d}}}"],
        )

    def test_collision(self):
        self.assertSequenceEqual(
            list(json2tex.json2texcommands({"x": 1, "X": 2, "x_": 3, "b": 4})),
            [
                r"\newcommand{\X}{1}",
                r"\newcommand{\XCollisionOne}{2}",
                r"\newcommand{\XCollisionTwo}{3}",
                r"\newcommand{\B}{4}",
            ],
        )

    def test_str2ascii(self):
        for s, (r1, r2) in {
            "σ_x": ("SIGMA_x", "_SIGMA__x"),
            "📝 bla": ("MEMO bla", "_MEMO_ bla"),
            "ΔV/Δt": ("DELTAV/DELTAt", "_DELTA_V/_DELTA_t"),
        }.items():
            self.assertEqual(json2tex.str2ascii(s), r1)
            self.assertEqual(json2tex.str2ascii(s, modifier="_{}_".format), r2)

    def test_list(self):
        self.assertSequenceEqual(
            tuple(json2tex.json2texcommands([1, 2, 3, 4])),
            (
                r"\newcommand{\First}{1}",
                r"\newcommand{\Second}{2}",
                r"\newcommand{\Third}{3}",
                r"\newcommand{\Fourth}{4}",
            ),
        )

    def test_dict(self):
        self.assertSequenceEqual(
            tuple(
                json2tex.json2texcommands(
                    {"bla": 1, "bli": {"blar": 2}, "blubb": 3}
                )
            ),
            (
                r"\newcommand{\Bla}{1}",
                r"\newcommand{\BliBlar}{2}",
                r"\newcommand{\Blubb}{3}",
            ),
        )

    def test_cli_stdio(self):
        p = subprocess.Popen(
            ["json2tex"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        d = [{"asdf": ["blar", 1, 2, "blubb"], "z": {}}, 1, ["b", 4]]
        stdout, stderr = p.communicate((inputjson := json.dumps(d)).encode())
        self.assertEqual(
            stdout.decode().strip(),
            "\n".join(outputtex := sorted(json2tex.json2texcommands(d))),
        )
