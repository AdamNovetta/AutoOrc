# AutoOrc
Auto start/stop AWS EC2 &amp; RDS Instances

### Usage
Add tags to your EC2 and RDS (non multi-az supported only) Instances that match the scripts:

>start = "autoOrc-up"

>stop = "autoOrc-down"

The values for these tags should be the UTC time you want the Instance to start and stop accordingly, e.g. 19:30

Change these variables if you want to use different AWS tags.

