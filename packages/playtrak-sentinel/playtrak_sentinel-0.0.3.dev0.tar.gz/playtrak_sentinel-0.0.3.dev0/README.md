<p align="center">
  <a href="https://osv.dev">
    <img src="https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel/-/raw/master/docs/assets/header-playtrak-sentinel.png" alt="Sentinel Header" />
  </a>
</p>

<p align="center">
  <a href="https://pypi.org/project/playtrak-sentinel/"><img alt="PyPI" src="https://img.shields.io/pypi/v/sentinel"></a>
  <a href="https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue"></a>
  <img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/playtrak-sentinel">
</p>

> **Note**  
> Sentinel is free and open-source. Contributions welcome!

---

# 📚 Table of Contents

- [Introduction](#-introduction)
- [Key Features](#-key-features)
- [Getting Started](#-getting-started)
  - [GitHub Action](#-github-action)
  - [GitLab CI](#-gitlab-ci)
  - [Command Line Interface](#-command-line-interface)
    - [1. Installation](#1-installation)
    - [2. Running Your First Scan](#2-running-your-first-scan)
  - [Basic Commands](#-basic-commands)
- [CI Exit Codes](#-ci-exit-codes)
- [License](#-license)
- [Supported Python Versions](#-supported-python-versions)
- [Resources](#-resources)
- [Author](#-author)

---

# 🔍 Introduction

**Sentinel** is a Python dependency vulnerability scanner powered by [OSV.dev](https://osv.dev).  It scans installed packages or requirements files for known security issues.

Sentinel is ideal for developers and teams who want to **automate security checks** in their local development and CI/CD pipelines.

---

# ✨ Key Features

- 🔍 Scan installed dependencies or `requirements.txt`
- 🚫 Detect known vulnerabilities via OSV.dev
- 🧾 Supports `.trakignore` to skip known issues
- 📄 Export reports to JSON and CSV
- 🚨 CI-ready: exits with `1` when vulnerabilities are found
- ⚡ Simple CLI, fast results

---

# 🚀 Getting Started

> The job fails if any vulnerabilities are found.  
> Add a `.trakignore` file to suppress specific known issues.  
> You can also export scan results with `--json` and `--csv` for reporting.

## ✅ GitHub Action

Use Sentinel in CI pipelines easily with GitHub Actions:

```yaml
name: Sentinel Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Sentinel
        run: pip install playtrak-sentinel

      - name: Run scan
        run: sentinel -r requirements.txt
```

---

## ✅ GitLab CI

You can integrate Sentinel in GitLab CI pipelines using the following example:

```yaml
stages:
  - test

scan_vulnerabilities:
  image: python:3.10
  stage: test
  before_script:
    - pip install playtrak-sentinel
  script:
    - sentinel -r requirements.txt
```

---

## 🖥️ Command Line Interface

### 1. Installation

Install via pip:

```bash
pip install playtrak-sentinel
```

### 2. Running Your First Scan

Basic usage with default environment:

```bash
sentinel
```

Scan specific files:

```bash
sentinel -r requirements.txt
sentinel -r requirements.txt -r dev-requirements.txt
```

Export reports:

```bash
sentinel -r requirements.txt --json report.json --csv report.csv
```

Ignore specific vulnerabilities with `.trakignore`:

```text
GHSA-xxxx-yyyy-zzzz
PYSEC-2023-0001
```

---

## ⚙️ Basic Commands

- `sentinel`: Scan installed environment  
- `sentinel -r file.txt`: Scan specific requirements file  
- `--json`: Export to JSON  
- `--csv`: Export to CSV  
- Uses `.trakignore` (optional) to skip vulnerabilities  

---

## 🚦 CI Exit Codes

| Code | Meaning                        |
|------|--------------------------------|
| 0    | No vulnerabilities found       |
| 1    | Vulnerabilities detected       |
| 2    | Usage error (e.g., no files)   |

---

## 📜 License

[MIT License](https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel/-/blob/master/LICENSE)

---

## 🐍 Supported Python Versions

Supports Python 3.7 and above. We recommend using the latest LTS version of Python for compatibility and security.

---

## 🤝 Contributing & Conduct

- [Contributing Guidelines](https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel/-/blob/master/CONTRIBUTING.md)
- [Code of Conduct](https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel/-/blob/master/CoC.md)

---

## 🔗 Resources

- [OSV.dev vulnerability database](https://osv.dev)
- [PyPI: playtrak-sentinel](https://pypi.org/project/playtrak-sentinel/)
- [GitLab Repository](https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel)
- [Website](https://playtrak.com/)
- [Documentation](https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel)
- [Issues & Feedback](https://git.playtrak.com.mx/public-content/PLAYTRAK.Sentinel/-/issues)

## 👤 Author

Created by **[Eder Ramos](https://gitlab.com/eder2597)** for **PLAYTRAK Sistemas de Monitoreo**.