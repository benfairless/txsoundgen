"""Invoke tasks."""
# from txsoundgen.invoke import ns
from invoke import task


@task(
    help={
        "check": "Checks if code is valid and return an exit code. Does not amend code."
    },
)
def fmt(command, check=False):
    """Format Python code using 'black' formatter."""
    cmd = "black"
    if check:
        cmd += " --check"
    command.run(f"{cmd} .")


@task
def lint(command):
    """Run lint tests."""
    command.run("pylint txsoundgen")
    # pylint.run_pylint(argv=["txsoundgen", "tests", "tasks.py"])


@task
def coverage(command):
    """Run code coverage report generation."""
    command.run("coverage report -m")


@task
def unit(command):
    """Run unit tests."""
    command.run(
        "pytest --cov=txsoundgen --cov-branch --cov-report=term --cov-report=html",
        pty=True,
    )


@task
def test(command):
    """Run full test suite."""
    fmt(command)
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
    command.run("rm -f voicepacks/**.wav")


@task
def docs(command):
    """Generate documentation."""
    command.run("pdoc --docformat google txsoundgen")


@task
def docker(command):
    """Generate Docker container."""
    command.run("docker build -t txsoundgen:latest .")


@task
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
    command.run("python -m txsoundgen")
