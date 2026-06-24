# Stack responsável pelo AWS Glue Crawler do pipeline ClimaBR
from aws_cdk import Stack
from aws_cdk import aws_glue as glue
from aws_cdk import aws_iam as iam
from constructs import Construct


class GlueCrawlerStack(Stack):
    """
    Provisiona:
    - IAM Role para o Glue com permissões de leitura no S3
    - Glue Crawler configurado para a camada raw/clima
    """
   
    def __init__(self, scope: Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        data_bucket_name = self.node.try_get_context("data_bucket_name")
        crawler_name = self.node.try_get_context("crawler_name")
        glue_database_name = self.node.try_get_context("glue_database_name")
        
        # IAM Role que o Glue vai usar para acessar o S3
        glue_role = iam.Role(
            self,
            "GlueServiceRole",
            role_name="AWSGlueServiceRole-clima-dbt",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )

        # Permissão de leitura no bucket raw
        glue_role.add_to_policy(
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:ListBucket"],
                resources=[
                    f"arn:aws:s3:::{data_bucket_name}",
                    f"arn:aws:s3:::{data_bucket_name}/*",
                ],
            )
        )

        # Glue Crawler com as mesmas configurações do ambiente atual
        crawler = glue.CfnCrawler(
            self,
            "CrawlerDbtClima",
            name=crawler_name,
            role=glue_role.role_arn,
            database_name=glue_database_name,
            targets=glue.CfnCrawler.TargetsProperty(
                s3_targets=[
                    glue.CfnCrawler.S3TargetProperty(
                        path="s3://{data_bucket_name}/raw/clima/"
                    )
                ]
            ),
            recrawl_policy=glue.CfnCrawler.RecrawlPolicyProperty(
                recrawl_behavior="CRAWL_NEW_FOLDERS_ONLY"
            ),
            schema_change_policy=glue.CfnCrawler.SchemaChangePolicyProperty(
                delete_behavior="LOG",
                update_behavior="LOG",
            ),
            configuration='{"Version":1.0,"CreatePartitionIndex":true}',
        )

        # Exporta o nome do crawler para a StepFunctionsStack
        self.crawler_name = crawler.name