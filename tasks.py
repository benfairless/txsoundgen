"""Invoke tasks."""

from invoke import task


@task(
    aliases=(["fmt"]),
    help={"change": "After checking formatting, make the necessary changes."},
)
def format(command, change=False):
    """Check formatting of Python code using 'black' formatter."""
    cmd = "black"
    if not change:
        cmd += " --check"
    command.run(f"{cmd} .", pty=True)


@task
def lint(command):
    """Run lint tests."""
    command.run("pylint txsoundgen -r y --exit-zero")
    # pylint.run_pylint(argv=["txsoundgen", "tests", "tasks.py"])


@task
def coverage(command):
    """Run code coverage report generation."""
    command.run("coverage report -m")


@task
def unit(command):
    """Run unit tests."""
    command.run(
        "pytest tests --cov=txsoundgen --cov-context=test --cov-report=term --cov-report=html",
        pty=True,
    )


@task
def test(command):
    """Run full test suite."""
    format(command)
    lint(command)
    unit(command)


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
    help={
        "serve": "Serve documentation on HTTP server, rather than generate static content."
    },
)
def docs(command, serve=False):
    """Generate documentation."""
    args = [] if serve else ["-o", "docs"]
    args.extend(["--mermaid", "--docformat", "google", "txsoundgen"])
    # command.run("pdoc --docformat google txsoundgen --logo https://placedog.net/300?random", pty=True)
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
    """Runs the module's main object."""
    command.run("python -m txsoundgen", pty=True)


if __name__ == "__main__":
    run(None)
