# Stack responsável pelo AWS Step Functions do pipeline ClimaBR
from aws_cdk import Stack, Duration
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_codebuild as codebuild
from constructs import Construct


class StepFunctionsStack(Stack):
    """
    Provisiona a State Machine do pipeline ClimaBR com o fluxo:
    1. Invoke Lambda (getAPI-clima)        — ingesta dados
    2. Glue StartCrawler                   — inicia o crawler
    3. Glue GetCrawlers                    — verifica estado
    4. Choice: RUNNING → Wait 5s → volta para GetCrawlers
               Default → CodeBuild StartBuild
    5. End
    """

    def __init__(
        self,
        scope: Construct,
        id: str,
        crawler_name: str,
        codebuild_project: codebuild.Project,
        
        **kwargs,
    ):
        super().__init__(scope, id, **kwargs)
        lambda_name = self.node.try_get_context("lambda_name")
        state_machine_name = self.node.try_get_context("state_machine_name")

        # IAM Role para a State Machine
        sfn_role = iam.Role(
            self,
            "StepFunctionsRole",
            role_name="StepFunctionsRole-climabr",
            assumed_by=iam.ServicePrincipal("states.amazonaws.com"),
        )

        # Permissão para invocar a Lambda
        sfn_role.add_to_policy(
            iam.PolicyStatement(
                actions=["lambda:InvokeFunction"],
                resources=[
                    f"arn:aws:lambda:{self.region}:{self.account}:function:{lambda_name}"
                ],
            )
        )

        # Permissão para operar o Glue Crawler
        sfn_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "glue:StartCrawler",
                    "glue:GetCrawlers",
                ],
                resources=["*"],
            )
        )

        # Permissão para iniciar o CodeBuild
        sfn_role.add_to_policy(
            iam.PolicyStatement(
                actions=["codebuild:StartBuild"],
                resources=[codebuild_project.project_arn],
            )
        )

        # Permissão para logs do Step Functions
        sfn_role.add_to_policy(
            iam.PolicyStatement(
                actions=[
                    "logs:CreateLogDelivery",
                    "logs:GetLogDelivery",
                    "logs:UpdateLogDelivery",
                    "logs:DeleteLogDelivery",
                    "logs:ListLogDeliveries",
                    "logs:PutLogEvents",
                    "logs:PutResourcePolicy",
                    "logs:DescribeResourcePolicies",
                    "logs:DescribeLogGroups",
                ],
                resources=["*"],
            )
        )

        # Referencia a Lambda existente (criada fora do CDK)
        ingestion_lambda = lambda_.Function.from_function_name(
            self, "IngestionLambda", lambda_name
        )

        # ── STATES ──────────────────────────────────────────────────────────

        # 1. Invoke Lambda — ingesta dados via API
        invoke_lambda = tasks.LambdaInvoke(
            self,
            "Ingestion - Lambda - API",
            lambda_function=ingestion_lambda,
            output_path="$.Payload",
        )

        # 2. Glue StartCrawler — inicia o crawler
        start_crawler = tasks.CallAwsService(
            self,
            "StartCrawler - Atualização Metadados",
            service="glue",
            action="startCrawler",
            parameters={"Name": crawler_name},
            iam_resources=["*"],
        )

        # 3. Glue GetCrawlers — verifica estado
        get_crawler = tasks.CallAwsService(
            self,
            "GetCrawler - Verificação de estado",
            service="glue",
            action="getCrawlers",
            parameters={"CrawlerNameList": [crawler_name]},
            iam_resources=["*"],
            result_path="$",
        )

        # 4a. Wait 5s — aguarda antes de verificar novamente
        wait_state = sfn.Wait(
            self,
            "Espera",
            time=sfn.WaitTime.duration(Duration.seconds(5)),
        )

        # 4b. CodeBuild StartBuild — dispara o build do dbt
        start_build = tasks.CodeBuildStartBuild(
            self,
            "CodeBuild StartBuild",
            project=codebuild_project,
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        # 4c. Choice — verifica se o crawler ainda está RUNNING
        choice = sfn.Choice(self, "Escolha")
        choice.when(
            sfn.Condition.string_equals("$.Crawlers[0].State", "RUNNING"),
            wait_state.next(get_crawler),
        )
        choice.otherwise(start_build)

        # ── ENCADEAMENTO ────────────────────────────────────────────────────
        definition = (
            invoke_lambda
            .next(start_crawler)
            .next(get_crawler)
            .next(choice)
        )

        # State Machine
        sfn.StateMachine(
            self,
            "PipelineClimaBR",
            state_machine_name=state_machine_name,
            definition_body=sfn.DefinitionBody.from_chainable(definition),
            role=sfn_role,
        )