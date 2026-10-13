import fnmatch
import glob
import json
import os
import re
import subprocess

def split_input(value):
    return [
        item.strip()
        for item in re.split(r"[,\r\n]+", value)
        if item.strip()
    ]

def is_excluded_path(file, patterns):
    file = os.path.normpath(file)

    for pattern in patterns:
        pattern = os.path.normpath(pattern)

        # Match a file, a directory and its descendants, or a glob.
        if (
            file == pattern
            or file.startswith(pattern.rstrip(os.sep) + os.sep)
            or fnmatch.fnmatch(file, pattern)
        ):
            return True

    return False

def main():
    pattern = os.environ.get("INPUT_PATH", "**/*.sh")
    severity = os.environ.get("INPUT_SEVERITY", "style")
    exclude_paths = os.environ.get("INPUT_EXCLUDE-PATHS", "")
    exclude_issues = os.environ.get("INPUT_EXCLUDE-ISSUES", "")

    excluded_paths = split_input(exclude_paths)
    files = [
        file
        for file in glob.glob(pattern, recursive=True)
        if not is_excluded_path(file, excluded_paths)
    ]

    if not files:
        print(f"::warning::No files matched pattern: {pattern}")
        set_output("issues", "0")
        return

    print(f"Matched {len(files)} file(s):")

    for file in files:
        print(f"  - {file}")

    command = [
        "shellcheck",
        "--format=json",
        f"--severity={severity}",
    ]

    excluded_codes = []
    for issue in split_input(exclude_issues):
        code = issue.upper().removeprefix("SC")
        if not code.isascii() or not code.isdigit():
            raise ValueError(f"Invalid ShellCheck issue code: {issue}")
        excluded_codes.append(code)

    if excluded_codes:
        command.append(f"--exclude={','.join(excluded_codes)}")

    command.extend(files)

    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
    )

    # ShellCheck:
    # 0 = no issues
    # 1 = issues found
    # >=2 = execution error
    if result.returncode >= 2:
        print(result.stderr)
        raise RuntimeError(f"ShellCheck failed with exit code {result.returncode}")

    issues = json.loads(result.stdout or "[]")

    write_summary(issues)

    set_output("issues", str(len(issues)))

    print(f"ShellCheck found {len(issues)} issue(s).")


def write_summary(issues):
    summary_file = os.environ.get("GITHUB_STEP_SUMMARY")

    if not summary_file:
        return

    lines = []

    lines.append("# ShellCheck Report")
    lines.append("")
    lines.append(f"Found **{len(issues)}** issue(s).")
    lines.append("")

    if not issues:
        lines.append("✅ No ShellCheck issues found.")
    else:
        lines.append("| File | Line | Column | Level | Code | Message |")
        lines.append("|---|---:|---:|---|---|---|")

        for issue in issues:
            message = escape_markdown(issue.get("message", ""))

            lines.append(
                f"| {issue.get('file', '')} "
                f"| {issue.get('line', '')} "
                f"| {issue.get('column', '')} "
                f"| {issue.get('level', '')} "
                f"| SC{issue.get('code', '')} "
                f"| {message} |"
            )

    with open(summary_file, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")


def set_output(name, value):
    output_file = os.environ.get("GITHUB_OUTPUT")

    if not output_file:
        return

    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"{name}={value}\n")


def escape_markdown(text):
    return text.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()
