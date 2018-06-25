# AutoOrc
Auto start/stop AWS EC2 &amp; RDS Instances

### Usage
Add tags to your EC2 and RDS (non multi-az supported only) Instances that match the scripts variables:

>start = "autoOrc-up"

>stop = "autoOrc-down"

The values for these tags should be the UTC time you want the Instance to start and stop accordingly, e.g. 19:30

Change these variables if you want to use different AWS tags.

By default this auto-stops items every day, and only starts Intances on weekdays. To start instances every day at the tagged time, change:

>weekdays = True

to

>weekdays = False


Permissions required:
*cloudwatch:PutMetricData
*ec2:DescribeInstances
*ec2:DescribeInstanceStatus
*ec2:DescribeTags
*ec2:StartInstances
*ec2:StopInstances
*logs:CreateLogGroup
*logs:CreateLogStream
*logs:DeleteLogGroup
*logs:DeleteLogStream
*logs:DescribeDestinations
*logs:DescribeLogGroups
*logs:DescribeLogStreams
*logs:DescribeMetricFilters
*logs:DescribeResourcePolicies
*logs:FilterLogEvents
*logs:GetLogEvents
*logs:ListTagsLogGroup
*logs:PutLogEvents
*logs:TagLogGroup
*rds:DescribeDBInstances
*rds:ListTagsForResource
*rds:StartDBInstance
*rds:StopDBInstance
*sts:GetCallerIdentity
