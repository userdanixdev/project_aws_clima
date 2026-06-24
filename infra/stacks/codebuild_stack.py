# Stack responsável pelo AWS CodeBuild do pipeline ClimaBR
from aws_cdk import Stack
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_iam as iam
from constructs import Construct



class CodeBuildStack(Stack):
    """
    Provisiona:
    - IAM Role para o CodeBuild com permissões de S3, Athena e Glue
    - Projeto CodeBuild conectado ao GitHub (userdanixdev/project_aws_clima)
      usando o buildspec.yml existente no repositório
    """

    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        data_bucket_name = self.node.try_get_context("data_bucket_name")
        site_bucket_name = self.node.try_get_context("site_bucket_name")
        github_owner = self.node.try_get_context("github_owner")
        github_repo = self.node.try_get_context("github_repo")
        github_branch = self.node.try_get_context("github_branch")
        codebuild_project_name = self.node.try_get_context("codebuild_project_name")

        # IAM Role que o CodeBuild vai usar
        codebuild_role = iam.Role(
            self,
            "CodeBuildServiceRole",
            role_name="CodeBuildServiceRole-climabr",
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSCodeBuildDeveloperAccess"
                ),
            ],
        )

        # S3: leitura/escrita nos buckets de dados e staging
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                ],
                resources=[
                    "arn:aws:s3:::{data_bucket_name}",
                    "arn:aws:s3:::{data_bucket_name}/*",
                ],
            )
        )

        # S3: escrita no bucket do site (docs dbt)
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject",
                    "s3:ListBucket",
                ],
                resources=[
                    "arn:aws:s3:::{site_bucket_name}",
                    "arn:aws:s3:::{site_bucket_name}/*",
                ],
            )
        )

        # Athena: execução de queries
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "athena:StartQueryExecution",
                    "athena:GetQueryExecution",
                    "athena:GetQueryResults",
                    "athena:StopQueryExecution",
                    "athena:GetWorkGroup",
                ],
                resources=["*"],
            )
        )

        # Glue: acesso ao catálogo de dados
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "glue:GetDatabase",
                    "glue:GetDatabases",
                    "glue:GetTable",
                    "glue:GetTables",
                    "glue:GetPartition",
                    "glue:GetPartitions",
                    "glue:CreateTable",
                    "glue:UpdateTable",
                    "glue:BatchCreatePartition",
                    "glue:BatchGetPartition",
                ],
                resources=["*"],
            )
        )

        # Logs: permissão para gravar no CloudWatch Logs
        codebuild_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                ],
                resources=["*"],
            )
        )

        # Projeto CodeBuild
        project = codebuild.Project(
            self,
            "ClimaBRProject",
            project_name=codebuild_project_name,
            role=codebuild_role,
            # Source: GitHub com buildspec.yml do próprio repositório
            source=codebuild.Source.git_hub(
                owner=github_owner,
                repo=github_repo,
                branch_or_ref=github_branch,
                # Não configura webhook — o trigger vem do Step Functions
                webhook=False,
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
            ),
            # Usa o buildspec.yml existente no repositório
            build_spec=codebuild.BuildSpec.from_source_filename("buildspec.yml"),
        )

        # Exporta o projeto para a StepFunctionsStack
        self.project = project