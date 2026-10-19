# ShellCheck Report

English | [简体中文](README.zh-CN.md)

Run ShellCheck and generate a report in the GitHub Actions Job Summary.

## Usage

```yaml
- uses: JCai-Code/shellcheck-report-action@v1.0.0
  with:
    path: "**/*.sh"
    severity: warning
```
