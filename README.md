# Tag Instances

Small tool for tagging AWS EC2 instances with appropriate IAM Users, to polyfill a gap in AWS 
where it's not particularly obvious who has created an EC2 instance, even when using IAM roles.

To do this, the script:

- Goes through each Region, looking for EC2 instances
- Asks the CloudTrail API for events relating to each instance
- Looks for `RunInstances` events, and tags these EC2 instances with:
  * IAM Username
  * IAM ARN
  * IAM User Type

One limitation is that the CloudTrail API only lists audit events for the past 7 days, so existing 
created instances may not fall into this window. You'll want to run this on a scheduled basis, at 
least once every 7 days

## Installation

To install, you'll need a working Python environment with `boto` installed. Install this via `pip`:

    $ [sudo] pip install boto

Alternatively, you can run this tool in a container:

    $ docker run -it -e AWS_ACCESS_KEY_ID=***** -e AWS_SECRET_ACCESS_KEY=***** fheng/tag_instances

## Running - Environment Variables

To run (either in a container or standalone), you'll need to export two environment variables:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
```

#### Building & Releasing for Docker

To build:

```
$ docker build -t feedhenry/tag_instances .
```

Get your Image ID via:

```
$ docker images | grep tag_instances
feedhenry/tag_instances          latest              0618027d8d57        8 minutes ago       749 MB
```

Push your images (you may need to login):

```
$ docker push feedhenry/tag_instances
```