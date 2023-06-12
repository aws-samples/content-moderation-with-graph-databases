from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
    aws_s3 as s3, 
    aws_kinesis as kinesis,
    aws_neptune_alpha as neptune,
    aws_apigateway as apigateway,
    aws_lambda as lm,
    aws_apigatewayv2_alpha as apigwv2,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_s3_notifications,
    aws_sagemaker as sagemaker,
    Stack,
    Fn,
    Tags,
    Aws,
 )
import aws_cdk as cdk 
from aws_cdk.aws_lambda_event_sources import KinesisEventSource

from aws_cdk.aws_apigatewayv2_integrations_alpha import HttpUrlIntegration, HttpLambdaIntegration

from constructs import Construct

class ContentmodStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #### VPC 
        vpc = ec2.Vpc(self, "ContentModVPC",max_azs=2)
        
        sg = ec2.SecurityGroup(self, "ContentModSG",
              vpc=vpc,
              allow_all_outbound=True,
             description='security group for content mod',
            security_group_name='ContentMod'
             )
        sg.add_ingress_rule(peer=sg, connection=ec2.Port.tcp(8182), description='Neptune')
        sg.node.add_dependency(vpc)

        ### Kinesis
        chatKinesisStream=kinesis.Stream(self, "content-mod-chat")
        

        ### Neptune
        neptuneDb = neptune.DatabaseCluster(self, "content-mod-db",
        vpc=vpc,
        instance_type=neptune.InstanceType.T3_MEDIUM,
        security_groups=[sg]
        )
        neptuneDb.connections.allow_default_port_internally()
        self.create_notebook(vpc, neptuneDb)

        #### Lambda - API 

        lambdaLayer=lm.LayerVersion(self, "ContentModLayer", code = lm.AssetCode('assets/ContentModLayer/'), compatible_runtimes=[lm.Runtime.PYTHON_3_9])
       
        lambdaAPI=lm.Function(self, "APIGateway", runtime=lm.Runtime.PYTHON_3_9, handler="lambda_function.lambda_handler", 
        code=lm.Code.from_asset("assets/content-mod-api"), timeout=cdk.Duration.minutes(1), layers=[lambdaLayer], 
        environment={"CLUSTER_ENDPOINT" : neptuneDb.cluster_endpoint.hostname , "CLUSTER_PORT" : str(neptuneDb.cluster_endpoint.port)},
        vpc=vpc,
        security_groups=[sg]
        )
        lambdaAPI_role=lambdaAPI.role
        ManagedPolicy=iam.ManagedPolicy
        lambdaAPI_role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("service-role/AWSLambdaVPCAccessExecutionRole"))
        
        lambdaAPI.node.add_dependency(vpc)
        lambdaAPI.node.add_dependency(sg)
        

        #### API Gateway 
        gateway_integration = HttpLambdaIntegration("lambda-integration", lambdaAPI)
        http_api = apigwv2.HttpApi(self, "Content-Mod-API")

        http_api.add_routes(path="/createGame",methods=[apigwv2.HttpMethod.PUT],integration=gateway_integration)
        http_api.add_routes(path="/createPlayer",methods=[apigwv2.HttpMethod.PUT],integration=gateway_integration)
        http_api.add_routes(path="/playerPlaysGame",methods=[apigwv2.HttpMethod.PUT],integration=gateway_integration)
        http_api.add_routes(path="/playerTransaction",methods=[apigwv2.HttpMethod.PUT],integration=gateway_integration)
        http_api.add_routes(path="/recordAbuse",methods=[apigwv2.HttpMethod.PUT],integration=gateway_integration)
        http_api.add_routes(path="/resetNeptune",methods=[apigwv2.HttpMethod.GET],integration=gateway_integration)
        

        #### Lambda - Chat
        lambdaChat=lm.Function(self, "Chat", runtime=lm.Runtime.PYTHON_3_9, handler="lambda_function.lambda_handler", 
        code=lm.Code.from_asset("assets/content-mod-chat"), timeout=cdk.Duration.minutes(1), layers=[lambdaLayer], 
        environment={"API_ENDPOINT" : http_api.api_endpoint }
        )
        lambdaChat_role=lambdaChat.role
        ManagedPolicy=iam.ManagedPolicy
        lambdaChat_role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("ComprehendFullAccess"))
        
        lambdaChat.add_event_source(KinesisEventSource(chatKinesisStream, batch_size=3,    starting_position=lm.StartingPosition.LATEST))
        lambdaChat.node.add_dependency(chatKinesisStream)
        lambdaChat.node.add_dependency(http_api)
        
        #### Lambda - Audio
        lambdaAudio=lm.Function(self, "Audio", runtime=lm.Runtime.PYTHON_3_9, handler="lambda_function.lambda_handler", 
        code=lm.Code.from_asset("assets/content-mod-audio"), timeout=cdk.Duration.minutes(1), layers=[lambdaLayer], 
        environment={"KINESIS_STREAM" : chatKinesisStream.stream_name }
        )
        lambdaAudio_role=lambdaAudio.role
        lambdaAudio_role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonTranscribeFullAccess"))
        lambdaAudio_role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))
        lambdaAudio_role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonKinesisFullAccess"))
       
        lambdaAudio.node.add_dependency(chatKinesisStream)

        

        #### Lambda - Screenshots 
        lambdaScreenshots=lm.Function(self, "Screenshots", runtime=lm.Runtime.PYTHON_3_9, handler="lambda_function.lambda_handler", 
        code=lm.Code.from_asset("assets/content-mod-screenshots"), timeout=cdk.Duration.minutes(1), layers=[lambdaLayer], 
        environment={"API_ENDPOINT" : http_api.api_endpoint }
        )
        lambdaScreenshots_role=lambdaScreenshots.role
        lambdaScreenshots_role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonRekognitionFullAccess"))
        lambdaScreenshots_role.add_managed_policy(ManagedPolicy.from_aws_managed_policy_name("AmazonS3ReadOnlyAccess"))
        lambdaScreenshots_role.node.add_dependency(http_api)

        #### S3 - Audio
        s3_audio=s3.Bucket(self,"AudioContentMod")
        notifyAudio=aws_s3_notifications.LambdaDestination(lambdaAudio)
        s3_audio.add_object_created_notification(notifyAudio)
        s3_audio.node.add_dependency(lambdaAudio)

        #### S3 - Screenshots 
        s3_screenshot=s3.Bucket(self,"ScreenShotContentMod") 
        notifyScreenshot=aws_s3_notifications.LambdaDestination(lambdaScreenshots)
        s3_screenshot.add_object_created_notification(notifyScreenshot)
        s3_screenshot.node.add_dependency(lambdaScreenshots)
        
        ## s3 - neptune overspill 
        s3_overspill=s3.Bucket(self,"NeptuneOverspill") 

        ## s3- training data bucket
        s3_comprehend=s3.Bucket(self,"ComprehendTraining") 


        #### finally output from CloudFormation the locations we require:
        cdk.CfnOutput(self,"S3ScreenshotsBucket",value=s3_screenshot.bucket_name)
        cdk.CfnOutput(self,"S3AudioBucket",value=s3_audio.bucket_name)
        cdk.CfnOutput(self,"APIEndpoint",value=http_api.api_endpoint)
        cdk.CfnOutput(self,"lambdaAPI",value=lambdaAPI.function_name)
        cdk.CfnOutput(self,"lambdaChat",value=lambdaChat.function_name)
        cdk.CfnOutput(self,"lambdaScreenshots",value=lambdaScreenshots.function_name)
        cdk.CfnOutput(self,"lambdaAudio",value=lambdaAudio.function_name)
        cdk.CfnOutput(self,"KinesisChatStream",value=chatKinesisStream.stream_name)
        cdk.CfnOutput(self,"S3Overspill",value=s3_overspill.bucket_name)
        cdk.CfnOutput(self,"S3TrainingData",value=s3_comprehend.bucket_name)

#### From https://github.com/aws-samples/amazon-neptune-samples/blob/master/neptune-sagemaker/cdk/python/neptune-notebook/neptune_notebook/neptune_notebook_stack.py 
    def create_notebook(self, neptune_vpc: ec2.Vpc, neptune_cluster: neptune.DatabaseCluster):
        """
        Create a Notebook Instance attached to the Neptune Cluster
        """
        # Create an IAM policy for the Notebook
        notebook_role_policy_doc = iam.PolicyDocument()
        notebook_role_policy_doc.add_statements(iam.PolicyStatement(**{
            "effect": iam.Effect.ALLOW,
            "resources": ["arn:aws:s3:::aws-neptune-notebook",
                "arn:aws:s3:::aws-neptune-notebook/*"],
            "actions": ["s3:GetObject",
                "s3:ListBucket"]
            })
        )
        
        # Allow Notebook to access Neptune Cluster
        notebook_role_policy_doc.add_statements(iam.PolicyStatement(**{
        "effect": iam.Effect.ALLOW,
        "resources": ["arn:aws:neptune-db:{region}:{account}:{cluster_id}/*".format(
            region=Aws.REGION, account=Aws.ACCOUNT_ID, cluster_id=neptune_cluster.cluster_resource_identifier)],
        "actions": ["neptune-db:connect"]
            })
        )

        # Create a role and add the policy to it
        notebook_role = iam.Role(self, 'Neptune-CDK-Notebook-Role',
            role_name='AWSNeptuneNotebookRole-CDK',
            assumed_by=iam.ServicePrincipal('sagemaker.amazonaws.com'),
            inline_policies={
                'AWSNeptuneNotebook-CDK': notebook_role_policy_doc
            }
        )

        notebook_lifecycle_script = f'''#!/bin/bash
sudo -u ec2-user -i <<'EOF'
echo "export GRAPH_NOTEBOOK_AUTH_MODE=DEFAULT" >> ~/.bashrc
echo "export GRAPH_NOTEBOOK_HOST={neptune_cluster.cluster_endpoint.hostname}" >> ~/.bashrc
echo "export GRAPH_NOTEBOOK_PORT=8182" >> ~/.bashrc
echo "export NEPTUNE_LOAD_FROM_S3_ROLE_ARN=" >> ~/.bashrc
echo "export AWS_REGION={Aws.REGION}" >> ~/.bashrc
aws s3 cp s3://aws-neptune-notebook/graph_notebook.tar.gz /tmp/graph_notebook.tar.gz
rm -rf /tmp/graph_notebook
tar -zxvf /tmp/graph_notebook.tar.gz -C /tmp
/tmp/graph_notebook/install.sh
EOF
'''
        notebook_lifecycle_config = sagemaker.CfnNotebookInstanceLifecycleConfig(self, 'NpetuneWorkbenchLifeCycleConfig',
            notebook_instance_lifecycle_config_name='aws-neptune-cdk-example-LC',
            on_start=[sagemaker.CfnNotebookInstanceLifecycleConfig.NotebookInstanceLifecycleHookProperty(
            content=Fn.base64(notebook_lifecycle_script)
            )]
        )

        neptune_security_group = neptune_cluster.connections.security_groups[0]
        neptune_security_group_id = neptune_security_group.security_group_id
        neptune_subnet = neptune_vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_NAT).subnets[0]
        neptune_subnet_id = neptune_subnet.subnet_id

        notebook = sagemaker.CfnNotebookInstance(self, 'CDKNeptuneWorkbench',
            instance_type='ml.t3.medium',
            role_arn=notebook_role.role_arn,
            lifecycle_config_name=notebook_lifecycle_config.notebook_instance_lifecycle_config_name,
            notebook_instance_name='cdk-neptune-workbench',
            root_access='Disabled',
            security_group_ids=[neptune_security_group_id],
            subnet_id=neptune_subnet_id,
            direct_internet_access='Enabled',
        )
        Tags.of(notebook).add('aws-neptune-cluster-id', neptune_cluster.cluster_identifier)
        Tags.of(notebook).add('aws-neptune-resource-id', neptune_cluster.cluster_resource_identifier)

        notebook.node.add_dependency(neptune_cluster)
        notebook.node.add_dependency(neptune_security_group)
        notebook.node.add_dependency(neptune_subnet)        
