import boto.ec2
import boto.cloudtrail
import json
import pdb
import time
import os
import sys

access_key = os.environ.get('AWS_ACCESS_KEY_ID')
access_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')

if access_key is None or access_secret is None:
  print "Error, please set AWS_ACCESS_KEY_ID && AWS_SECRET_ACCESS_KEY"
  print os.environ
  sys.exit(-1)

def regions():
  return boto.ec2.regions()

def tag_instances():
  for region in regions():
    region_name = region.name
    if region_name != 'cn-north-1' and region_name != 'us-gov-west-1': # Skip these regions
      print "Region: %s" % (region_name)

      # Connect
      ec2 = boto.ec2.connect_to_region(region_name, aws_access_key_id=access_key, aws_secret_access_key=access_secret)
      cloudtrail = boto.cloudtrail.connect_to_region(region_name, aws_access_key_id=access_key, aws_secret_access_key=access_secret)


      reservations = ec2.get_all_reservations()
      tags = ec2.get_all_tags()
      for reservation in reservations:
        for instance in reservation.instances:
          events_dict = cloudtrail.lookup_events(lookup_attributes=[{'AttributeKey':'ResourceName', 'AttributeValue': instance.id}])

          if len(events_dict['Events']) == 0:
            print("No CloudTrail events for instance: %s - %s" % (instance.id, instance.instance_type))
          else:
            for data in events_dict['Events']:
              json_file = json.loads(data['CloudTrailEvent'])
              # Only interested in RunInstances (e.g. created instances) to find owners
              # There's also StartInstances, but that event is fired if someone else 
              # restarts an instance, which isn't what we're really looking for
              if json_file['eventName'] == 'RunInstances': 
                arn = json_file['userIdentity']['arn']
                username = json_file['userIdentity']['userName']
                user_type = json_file['userIdentity']['type']

                print("Tagging Instance: %s, Username: %s, ARN: %s, Type: %s, eventName: %s" % (
                  instance.id, 
                  username, 
                  arn, 
                  user_type, json_file['eventName'])
                )
                # Tag the instance
                ec2.create_tags([instance.id], {"IAM Username": username, "IAM ARN": arn, "IAM Type": user_type})
          # CloudTrail calls are throttled if there's more than 1 req/s 
          time.sleep(1)

tag_instances()
