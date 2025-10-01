"""Invoke tasks using the Invoke library.

This module defines a set of tasks for managing the development workflow of the project,
including formatting, linting, testing, documentation generation, building, and
publishing.

Each task is decorated with `@task` from the Invoke library, allowing for easy execution
from the command line. Tasks can be run individually or as part of a sequence, and
they support various options to customize their behavior.

Usage:
    - To run a specific task, use the command:
        inv <task_name> [options]
    - To see a list of available tasks, use:
        inv --list
    - To get help on a specific task, use:
        inv <task_name> --help
"""

from invoke import task


@task(
    aliases=(["format"]),
    help={"fix": "Automatically fix formatting issues."},
)
def fmt(command, fix=True):
    """Format code."""
    cmd = "ruff format"
    if not fix:
        cmd += " --diff"
    command.run(f"{cmd}", pty=True)


@task(help={"fix": "Automatically fix linting issues."})
def lint(command, fix=True):
    """Run lint tests."""
    cmd = "ruff check"
    if fix:
        cmd += " --fix"
    command.run(cmd, pty=True)


@task(aliases=(["coverage"]))
def cov(command):
    """Run code coverage report generation."""
    command.run("coverage report -m")


@task(
    help={
        "all": "Run full test suite, including slow tests.",
        "benchmark": "Run benchmarks for the test suite.",
    }
)
def unit(command, all=False, benchmark=False):
    """Run unit tests."""
    cmd = "pytest"
    if not all:
        cmd += " -m 'not slow'"
    if benchmark:
        cmd += " --durations=5 --durations-min=1.0"
    command.run(cmd, pty=True)


@task(
    help={
        "all": "Run full test suite, including slow tests.",
        "fix": "After checking formatting and linting, make the necessary changes.",
    },
)
def test(command, all=False, fix=True):
    """Run full test suite."""
    fmt(command, fix=fix)
    lint(command, fix=fix)
    unit(command, all=all)
    cov(command)


@task
def dependencies(command):
    """Install dependencies."""
    command.run("poetry install")


@task
def update(command):
    """Update dependencies."""
    command.run("poetry update")


@task
def clean(command):
    """Clean development environment, removing temporary files."""
    command.run("rm -rf dist/ build/ **/__pycache__ .pytest_cache/")
    # These will probably go away
    command.run("rm -rf htmlcov/")
    command.run("rm -rf resources/")


@task(
    help={"serve": "Serve documentation on HTTP server."},
)
def docs(command, serve=False):
    """Generate documentation."""
    args = [] if serve else ["-o", "docs"]
    args.extend(["--mermaid", "--docformat", "google", "txsoundgen"])
    command.run("pdoc " + " ".join(args), pty=True)
    if not serve:
        command.run("rm -f docs/index.html")
        command.run("mv docs/txsoundgen.html docs/index.html")


@task
def docker(command):
    """Generate Docker container."""
    command.run("docker build -t txsoundgen:latest .")


@task(clean)
def build(command):
    """Build distributable."""
    command.run("poetry build")


@task
def version(command):
    """Display package version."""
    command.run("poetry version")
    # https://python-poetry.org/docs/cli/#version


@task
def publish(command):
    """Publish package to remote repository."""
    command.run("poetry publish")


@task
def deploy(command):
    """Full clean build and publish"""
    clean(command)
    build(command)
    publish(command)


@task(default=True)
def run(command):
    """Run the module's main object."""
    command.run("python -m txsoundgen", pty=True)


if __name__ == "__main__":
    run(None)
