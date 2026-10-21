# ShellCheck Report Action

[English](README.md) | 简体中文

在 GitHub Actions 中运行 ShellCheck 并报告检查结果。

## 使用

ShellCheck Report Action 可以通过多种方式执行静态检查，结果以表格形式呈现。
- `path` 参数扫描特定的文件，默认值: `.`，必选项。
- `severity` 参数指定要检查的最低错误级别，[style、info、warning、error]，默认值: `style`, 可选项。
- `exclude-issues` 参数指定扫描期间要排除的 shellcheck 问题。默认值：扫描所有问题，可选项。问题号用逗号分隔。
- `exclude-paths` 参数从 shellcheck 扫描中排除指定文件，可选项

### 示例
```yml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v6
      - name: Run ShellCheck
        uses: Cai-Code/shellcheck-report-action@v1.0
        with:
          path: "test/**.sh"
          severity: style
          exclude-issues: "SC2006,SC1068"
          exclude-paths: "test/bad.sh"
```
