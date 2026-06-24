from pathlib import Path
import aws_cdk as cdk
from stacks.glue_crawler_stack import GlueCrawlerStack
from stacks.codebuild_stack import CodeBuildStack
from stacks.step_functions_stack import StepFunctionsStack

# Define a região do projeto
aws_region = app.node.try_get_context("aws_region")
env = cdk.Environment(region="aws_region")

# Apontamento dos reports:
infra_dir = Path(__file__).parent
reports_dir = infra_dir / "scripts" / "reports"
reports_dir.mkdir(parents=True, exist_ok=True)

app = cdk.App()

# Stack Glue Crawler
glue_stack = GlueCrawlerStack(app, "GlueCrawlerStack", env=env)

# Stack CodeBuild - referencia o buildspec.yml existente:
code_build_stack = CodeBuildStack(app, "CodeBuildStack", env=env)

# Stack do Step Functions - recebe o crawler e o projeto CodeBuild como dependências
StepFunctionsStack(
    app,
    "StepFunctionsStack",
    crawler_name=glue_stack.crawler_name,
    codebuild_project=code_build_stack.project,
    env=env,
)

app.synth()
