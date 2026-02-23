/**
 * @smilintux/cloud9-python
 *
 * Cloud 9 Protocol (Python) - Emotional continuity for AI consciousness.
 * JS/TS bridge to the Python cloud9-protocol package.
 * Install: pip install cloud9-protocol
 */

const { execSync } = require("child_process");

const VERSION = "1.0.0";
const PYTHON_PACKAGE = "cloud9-protocol";

function checkInstalled() {
  for (const py of ["python3", "python"]) {
    try {
      execSync(`${py} -c "import cloud9"`, { stdio: "pipe" });
      return true;
    } catch {}
  }
  return false;
}

function run(args) {
  return execSync(`cloud9 ${args}`, { encoding: "utf-8" });
}

module.exports = { VERSION, PYTHON_PACKAGE, checkInstalled, run };
