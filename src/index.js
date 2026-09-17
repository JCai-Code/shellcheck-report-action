import * as core from "@actions/core";
import * as exec from "@actions/exec";
import * as glob from "@actions/glob";

async function run() {
  try {
    const pattern = core.getInput("path");
    const severity = core.getInput("severity");

    const globber = await glob.create(pattern);
    const files = await globber.glob();

    if (files.length === 0) {
      core.warning(`No files matched: ${pattern}`);
      core.setOutput("issues", 0);
      return;
    }

    core.info(`Matched ${files.length} file(s):`);

    for (const file of files) {
      core.info(`- ${file}`);
    }

    let output = "";

    const exitCode = await exec.exec(
      "shellcheck",
      [
        "--format=json",
        `--severity=${severity}`,
        ...files
      ],
      {
        listeners: {
          stdout: (data) => {
            output += data.toString();
          }
        },
        ignoreReturnCode: true
      }
    );

    const issues = JSON.parse(output || "[]");

    const table = [
      [
        { data: "File", header: true },
        { data: "Line", header: true },
        { data: "Level", header: true },
        { data: "Code", header: true },
        { data: "Message", header: true }
      ]
    ];

    for (const issue of issues) {
      table.push([
        issue.file,
        String(issue.line),
        issue.level,
        `SC${issue.code}`,
        issue.message
      ]);
    }

    await core.summary
      .addHeading("ShellCheck Report")
      .addRaw(`Found ${issues.length} issue(s).\n`)
      .addTable(table)
      .write();

    core.setOutput("issues", issues.length);

    core.info(`ShellCheck exit code: ${exitCode}`);
  } catch (error) {
    core.setFailed(
      error instanceof Error ? error.message : String(error)
    );
  }
}

run();