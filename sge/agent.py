import os


class Agent(object):
	def __init__(self, **kwargs):
		super(Agent, self).__init__()
		self.kwargs = kwargs
		self.sge_job_id = self.kwargs['sge_job_id']
		self.shared_data_path = self.kwargs["shared_data_path"]
		self.base_path = self.kwargs["base_path"]

	def receive(self, job, base_path):
		job.deploy(self.sge_job_id, self.base_path)

		with open(self.base_path + 'agent_pool/{}.POOL'.format(self.sge_job_id), 'a') as f:
			# TODO: Need shared data path to populate agents
			f.write(self.shared_data_path)

	def is_available(self):
		if os.stat(self.base_path + f'agent_pool/{self.kwargs["sge_job_id"]}.POOL').st_size == 0:
			return True
		else:
			return False


