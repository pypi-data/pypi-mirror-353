# 📝 json2tex - Convert JSON to LaTeX

[![pipeline status](https://gitlab.com/nobodyinperson/json2tex/badges/master/pipeline.svg)](https://gitlab.com/nobodyinperson/json2tex/-/pipelines)
[![coverage report](https://gitlab.com/nobodyinperson/json2tex/badges/master/coverage.svg)](https://nobodyinperson.gitlab.io/json2tex/coverage-report/)
[![documentation](https://img.shields.io/badge/documentation-here%20on%20GitLab-brightgreen.svg)](https://nobodyinperson.gitlab.io/json2tex)

This Python script can read multiple JSON files, merge them and outputs LaTeX-`\newcommand`-definitions to access all elements.

### Installation

```bash
# from PyPI
pip install json2tex
# or directly from GitLab
pip install git+https://gitlab.com/nobodyinperson/json2tex
```

### Usage

#### JSON file → TeX file

With a JSON file `values.json` like this:

```json
[
  {
    "_id": "5f1570db9d5aa0b6df3823f8",
    "index": 0,
    "guid": "0fdfb3c5-1f0a-4c2a-8fed-75861742b588",
    "isActive": true,
    "balance": "$1,652.14",
    "picture": "http://placehold.it/32x32",
    "age": 22,
    "eyeColor": "blue",
    "name": {
      "first": "Harrington",
      "last": "Emerson"
    },
    "company": "ISOSURE"
  }
]
```

_(generated with [JSONGenerator](https://twitter.com/JSONGenerator) btw.)_

You can then convert that JSON to TeX-definitions like this:

```bash
json2tex -i values.json -o values.tex
```

... which generates the following `values.tex` file:

```tex
\newcommand{\FirstId}{5f1570db9d5aa0b6df3823f8}
\newcommand{\FirstIndex}{0}
\newcommand{\FirstGuid}{0fdfb3c5-1f0a-4c2a-8fed-75861742b588}
\newcommand{\FirstIsactive}{True}
\newcommand{\FirstBalance}{\$1,652.14}
\newcommand{\FirstPicture}{http://placehold.it/32x32}
\newcommand{\FirstAge}{22}
\newcommand{\FirstEyecolor}{blue}
\newcommand{\FirstNameFirst}{Harrington}
\newcommand{\FirstNameLast}{Emerson}
\newcommand{\FirstCompany}{ISOSURE}
```

#### Python dict/list → TeX file

```python
import json2tex json2texfile
json2tex.json2texfile({
    "experiment": "Free Fall",
    "g": 9.81,
    "duration_s": 3,
    "equation": r"h(t) = \frac{1}{2}gt^2",
    "results": [0.0, 4.9, 19.6],
    "valid": True
},"experiment.tex")
# produces experiment.tex:
# \newcommand{\Experiment}{Free Fall}
# \newcommand{\G}{9.81}
# \newcommand{\Duration_S}{3}
# \newcommand{\Equation}{h(t) = \textbackslash frac\{1\}\{2\}gt\textasciicircum 2}
# \newcommand{\ResultsFirst}{0.0}
# \newcommand{\ResultsSecond}{4.9}
# \newcommand{\ResultsThird}{19.6}
# \newcommand{\Valid}{True}
```
