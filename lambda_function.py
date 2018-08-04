#!/usr/bin/env python3
import boto3
import logging
import time
import datetime


# Output logging - default WARNING. Set to INFO for full output in cloudwatch
logger = logging.getLogger()
logger.setLevel(logging.WARNING)

# AWS Tags to target for starting and stopping
start = "autoOrc-up"
stop = "autoOrc-down"

# Start instances only on weekdays? (change to False to start every day)
weekdays = True

# define boto3 connections/variables
ec2 = boto3.resource('ec2')
cw = boto3.client('cloudwatch')
rds = boto3.client('rds')


# create cloudwatch metrics for instance start/stop/failure
def putCloudWatchMetric(metricName, value, process, outcome):
    cw.put_metric_data(
        Namespace='ORC-Results',
        MetricData=[{
            'MetricName': metricName,
            'Value': value,
            'Unit': 'Count',
            'Dimensions': [{
                'Name': 'Process',
                'Value': process
                },
                {
                'Name': 'Outcome',
                'Value': outcome
                }]
            }]
    )


# find the name tag of an instance
def get_ec2_instance_name(instance_id):
    InstanceName = None
    UnNamedLabel = "(no name)"
    EC2Instance = ec2.Instance(instance_id)
    if EC2Instance.tags is not None:
        for tags in EC2Instance.tags:
            if tags["Key"] == 'Name':
                InstanceName = tags["Value"]
    if InstanceName is None or InstanceName == '':
        InstanceName = UnNamedLabel
    return(InstanceName)


# get AutoOrc-down / AutoOrc-up tags on RDS instances
def get_rds_orc_tags(ARN, phase):
    OrcTimer = ''
    tags = rds.list_tags_for_resource(ResourceName=ARN)

    for tag in tags['TagList']:
        if tag['Key'] == phase:
            OrcTimer = tag['Value']

    return OrcTimer


# Main function that lambda calls
def lambda_handler(event, context):
    start_tag = "tag:" + start
    stop_tag = "tag:" + stop
    MyAWSID = boto3.client('sts').get_caller_identity().get('Account')

    # day of the week
    d = datetime.datetime.now()

    # check to see if today is a weekday
    def weekday(test_date):
        if test_date.isoweekday() in range(1, 6):
            return(True)
        else:
            return(False)

    is_weekday = weekday(d)

    # define timer, used to gague shutdown time, in UTC time
    timer = time.strftime("%H:%M")

    # set base filters for running/stopped instances, and matching orc tags
    FilterRunning = [
        {'Name': 'instance-state-name', 'Values': ['running']},
        {'Name': stop_tag, 'Values': [timer]}
        ]

    FilterStopped = [
        {'Name': 'instance-state-name', 'Values': ['stopped']},
        {'Name': start_tag, 'Values': [timer]}
        ]

    print("\n[ AutoOrc start time : " + timer + " ]")

    OrcInstances = ec2.instances.filter(Filters=FilterRunning)
    OrcDBs = rds.describe_db_instances()
    counter = ErrorCounter = 0

    # stop EC2 Instances
    for instance in OrcInstances:
        counter += 1
        StateCode = 0
        name = get_ec2_instance_name(instance.id)
        print(
                "---> Shutting down instance: \n\t" + instance.id +
                "[ Name : " + name + " ] "
            )
        response = instance.stop()
        StateCode = response['StoppingInstances'][0]['CurrentState']['Code']

        if StateCode == 16:
            ErrorCounter += 1
            print("Error stopping " + name + ", error code: " + str(StateCode))

    if (counter > 0):
        putCloudWatchMetric(MyAWSID, counter, stop, 'Success')

    if (ErrorCounter > 0):
        putCloudWatchMetric(MyAWSID, ErrorCounter, stop, 'Error')
        print(" x - Errored while stopping " + str(counter) + " instances")

    print(" - Stopped " + str(counter) + " instances")

    OrcInstancesUp = ec2.instances.filter(Filters=FilterStopped)
    counter = ErrorCounter = 0
    BadStartCodes = ['32', '48', '64', '80']

    # Cycle through and start tagged EC2 instances
    if is_weekday or weekdays is False:
        for instance in OrcInstancesUp:
            counter += 1
            StateCode = 0
            name = get_ec2_instance_name(instance.id)
            print(
                    "---> Starting instance: \n\t" + instance.id +
                    " [ Name : " + name + " ] "
                )
            response = instance.start()
            StateCode = response['StartingInstances'][0]['CurrentState']['Code']

            if StateCode in BadStartCodes:
                ErrorCounter += 1
                print(" Error starting " + name + ", code: " + str(StateCode))

        if (counter > 0):
            putCloudWatchMetric(MyAWSID, counter, start, 'Success')

        if (ErrorCounter > 0):
            putCloudWatchMetric(MyAWSID, ErrorCounter, start, 'Error')
            print(" x - Errored while starting " + str(counter) + " instances")

    print(" - Started " + str(counter) + " instances")

    # Cycle through all RDS instaces, starting Orc tagged ones
    for RDSInstance in OrcDBs['DBInstances']:
        RDSName = str(RDSInstance['DBInstanceIdentifier'])
        RDSARN = str(RDSInstance['DBInstanceArn'])
        RDSStatus = str(RDSInstance['DBInstanceStatus'])
        RDSAZState = str(RDSInstance['MultiAZ'])

        if is_weekday or weekdays is False:

            if RDSAZState == 'False' and RDSStatus == 'stopped':
                orc_up = get_rds_orc_tags(RDSARN, start)

                if orc_up == timer:
                    print("RDS : " + RDSName + " database is starting up")
                    rds.start_db_instance(DBInstanceIdentifier=RDSName)

        if RDSAZState == 'False' and RDSStatus == 'available':
            orc_down = get_rds_orc_tags(RDSARN, stop)

            if orc_down == timer:
                print("RDS : " + RDSName + " database is shutting down now")
                rds.stop_db_instance(DBInstanceIdentifier=RDSName)

    print("[ AutoOrc finished ]\n")
