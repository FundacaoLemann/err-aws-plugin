#!/ur/bin/python

from errbot import BotPlugin, botcmd
import boto3


class AWS(BotPlugin):
    """
    Very simple AWS plugin
    """
    def __init__(self, *args, **kwargs):
        super(AWS, self).__init__(*args, **kwargs)
        self.ec2 = boto3.resource("ec2", region_name="us-west-2")

    def _get_instance_name(self, instance):
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                return tag['Value'] 

    @botcmd
    def aws_instances(self, msg, args):
        """
        List all AWS instances.
        """
        instances = self.ec2.instances.all()
        for i in instances:
            name = self._get_instance_name(i)
            yield "**Name:** {name} | **IP:** {ip} | **State:** {state} | **ID:** {id} | **Instance Type:** {type}".format(
                name=name,
                ip=i.public_ip_address,
                state=i.state['Name'],
                id=i.id,
                type=i.instance_type)

    def list_instances_by_status(self, status):
        """
        Lists instances by status.

        Args:
            status (str): aws status such as 'running', 'stopped'
        """
        instances = self.ec2.instances.filter(Filters=[
            {"Name": "instance-state-name",
             "Values": [status]}
            ])
        for i in instances:
            print (i.id, i.instance_type)

    def create_instance(self):
        new = self.ec2.create_instances(
            ImageId='ami-7a3dd76c',
            MinCount=1,
            MaxCount=1)
        return new

    def aws_terminate(self, id):
        i = self.ec2.instances.filter(InstanceIds=[id]).terminate()

    def stop_instance(self, id):
        i = self.ec2.instances.filter(InstanceIds=[id]).stop()

    def start_instance(self, id):
        i = self.ec2.instances.filter(InstanceIds=[id]).start()
        return i
