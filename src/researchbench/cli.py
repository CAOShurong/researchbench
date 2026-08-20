"""ResearchBench CLI - run, list, and explore the benchmark."""
import click
import json
from researchbench import Benchmark
from researchbench.tasks import PaperComprehension, IdeaGeneration, LiteratureSynthesis, ExperimentalDesign, PeerReview, Reproduction, OpenQuestionId

TASK_INFO = {
    "paper_comprehension": {"class": PaperComprehension, "desc": "Test deep understanding of research papers, methodology critique, and limitation identification."},
    "idea_generation": {"class": IdeaGeneration, "desc": "Test ability to generate novel research hypotheses from gap analysis."},
    "literature_synthesis": {"class": LiteratureSynthesis, "desc": "Test ability to synthesize multiple papers and identify trends."},
    "experimental_design": {"class": ExperimentalDesign, "desc": "Test ability to design valid experiments with controls and statistics."},
    "peer_review": {"class": PeerReview, "desc": "Test ability to provide constructive, technically sound peer review."},
    "reproduction": {"class": Reproduction, "desc": "Test ability to diagnose and fix reproduction failures."},
    "open_question_id": {"class": OpenQuestionId, "desc": "Test ability to identify important open research questions."},
}

@click.group()
def main():
    pass

@main.command()
def list():
    """List all available tasks."""
    click.echo("ResearchBench Tasks:")
    click.echo("=" * 60)
    for name, info in TASK_INFO.items():
        click.echo(f"  {name:25s} {info['desc']}")

@main.command()
@click.option("--tasks", default="all", help="Comma-separated task names or 'all'")
@click.option("--model", default="gpt-4o", help="Model to evaluate")
@click.option("--output", default=None, help="Output JSON file path")
def run(tasks, model, output):
    """Run the benchmark."""
    if tasks == "all":
        task_list = list(TASK_INFO.keys())
    else:
        task_list = [t.strip() for t in tasks.split(",")]
    bench = Benchmark(tasks=task_list)
    result = bench.run(model=model)
    click.echo(result.summary())
    if output:
        with open(output, "w") as f:
            f.write(result.to_json())
        click.echo(f"Results saved to {output}")

@main.command()
@click.argument("task_name")
def show(task_name):
    """Show task description and sample."""
    if task_name not in TASK_INFO:
        click.echo(f"Unknown task: {task_name}")
        click.echo("Available: " + ", ".join(TASK_INFO.keys()))
        return
    info = TASK_INFO[task_name]
    click.echo(f"Task: {task_name}")
    click.echo(f"Description: {info['desc']}")
    from researchbench.tasks.paper_comprehension import PAPERS
    if hasattr(PAPERS, '__len__') and len(PAPERS) > 0:
        click.echo(f"\nSample data: {len(PAPERS)} papers loaded")

if __name__ == "__main__":
    main()