#!/ur/bin/python

from errbot import BotPlugin, botcmd
import boto3


class AWS(BotPlugin):
    """
    Very simple AWS plugin
    """
    permitted_instances = []

    def __init__(self, *args, **kwargs):
        super(AWS, self).__init__(*args, **kwargs)
        self.ec2 = boto3.resource("ec2", region_name="us-west-2")

    @botcmd(admin_only = True)
    def aws_addpermission(self, msg, args):
        """
        Includes instance id in permitted list.
        """
        id = args
        self.permitted_instances.append(id)
        return "Instance {} added to permitted list".format(id)

    @botcmd(admin_only = True)
    def aws_removepermission(self, msg, args):
        """
        Removes instance id from permitted list.
        """
        id = args
        self.permitted_instances.remove(id)
        return "Instance {} removed from permitted list".format(id)

    def _get_instance_name(self, instance):
        for tag in instance.tags:
            if tag['Key'] == 'Name':
                return tag['Value'] 

    def _is_instance_permitted(self, id):
        """ 
        Verifies if instance is in permitted instances list.
        """
        response = id in self.permitted_instances
        return response

    @botcmd
    def aws_instances(self, msg, args):
        """
        List all AWS instances.
        """
        instances = self.ec2.instances.all()
        yield  """**Permitted**	|**Name**	|**IP**	|**State**	|**ID**	|**Instance Type**"""
        for i in instances:
            is_permitted = self._is_instance_permitted(i.id)
            name = self._get_instance_name(i)
            yield "{permitted} | {name} | {ip} | {state} | {id} | {type}".format(
                permitted=is_permitted,
                name=name,
                ip=i.public_ip_address,
                state=i.state['Name'],
                id=i.id,
                type=i.instance_type)

    @botcmd
    def aws_stop(self, msg, args):
        """
        Stop instance by id.
        """
        id = args
        response = ""
        if self.is_instance_permitted(id):
            i = self.ec2.instances.filter(InstanceIds=[id]).stop()
            reponse = "Instance {} stopped".format(self._get_instance_name(id))
        else:
            response = "Instance not in permitted list. Use `aws addpermission ID` command."
        return reponse

    @botcmd
    def aws_start(self, msg, args):
        """
        Start instance by id.
        """
        id = args
        response = ""
        if self.is_instance_permitted(id);
            i = self.ec2.instances.filter(InstanceIds=[id]).start()
            response = "Instance {} started".format(self._get_instance_name(id))
        else:
            response = "Instance not in permitted list. Use `aws addpermission ID` command."
        return response

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

