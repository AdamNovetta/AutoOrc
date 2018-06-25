# AutoOrc V1.0- AWS Lambda Instance Auto-Orchestration
Auto start/stop AWS EC2 &amp; RDS Instances

## Usage
### Copy the lambda_function.py contents to a new blank Lambda.
(This script works regionally, you'll have to create a separate Lambda in every AWS region you want to control your instances)
#### Settings:
* Runtime : Python 3.6
* Handler : lambda_function.lambda_handler
* Memory : 128 MB
* Timeout : 30 sec

#### Setup


Add tags to your EC2 and RDS (non multi-az supported only) Instances that match the scripts variables:
```python
start = "autoOrc-up"
stop = "autoOrc-down"
```
The values for these tags should be the **UTC time** you want the Instance to start and stop accordingly, e.g. 19:30

Change these variables if you want to use different AWS tags.

By default this auto-stops items every day, and only starts Instances on weekdays. To start instances every day at the tagged time, change:
```python
weekdays = True
```
to
```python
weekdays = False
```

#### Trigger
Create a CloudWatch rule, that runs on a schedule of fixed rate every 1 minute, and target it to the AutoOrc Lambda

#### Permissions required for Lambda Role:
* cloudwatch:PutMetricData
* ec2:DescribeInstances
* ec2:DescribeInstanceStatus
* ec2:DescribeTags
* ec2:StartInstances
* ec2:StopInstances
* logs:CreateLogGroup
* logs:CreateLogStream
* logs:DeleteLogGroup
* logs:DeleteLogStream
* logs:DescribeDestinations
* logs:DescribeLogGroups
* logs:DescribeLogStreams
* logs:DescribeMetricFilters
* logs:DescribeResourcePolicies
* logs:FilterLogEvents
* logs:GetLogEvents
* logs:ListTagsLogGroup
* logs:PutLogEvents
* logs:TagLogGroup
* rds:DescribeDBInstances
* rds:ListTagsForResource
* rds:StartDBInstance
* rds:StopDBInstance
* sts:GetCallerIdentity

