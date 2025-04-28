import numpy as np
import os
import logging


class Job(object):
	def __init__(self, name, data=None, **kwargs):
		super(Job, self).__init__()
		self.name = name
		self.data = data		

	def deploy(self, sge_job_id, base_path):
		try:
			path = base_path + f'job_pool/{sge_job_id}.npz'
			np.savez(
				path, 
				matrix_a=self.data['matrix_a'], 
				matrix_b=self.data['matrix_b'],
				name=self.name,
			)
			self.sge_job_id = sge_job_id
			return True
		except Exception as e:
			raise e
	
	def collect(self, base_path):
		try:
			path = base_path + f'result_pool/{self.name}.npz'
			result = np.load(path)
			os.remove(path)
			return True # TODO: This is where you need to do somethign with the result (e.g. pass it to JobPool) or collect files 
		except Exception:
			return False
		

class JobPool(object):
	def __init__(self, to_distribute, **kwargs):
		super(JobPool, self).__init__()
		self.to_distribute = to_distribute 
		self.to_collect = []
		self.base_path = kwargs['base_path']
		self.logger = kwargs['logger']

	def distribute(self, agent):
		if self.to_distribute:
			job = self.to_distribute.pop(0)
			agent.receive(job=job, base_path=self.base_path)
			self.logger.info('Assigned job {} to agent {}.'.format(job.name, agent.sge_job_id))
			self.to_collect.append(job)
		
	def collect(self):
		n = 0
		for job in self.to_collect:
			if job.collect(self.base_path):
				# self.post_processing_task(job) 
				self.logger.info('Collected job result {}.'.format(job.name))
				self.to_collect.remove(job)
				n += 1
		return n

	def is_finished(self):
		if len(self.to_distribute) == 0 and len(self.to_collect) == 0:
			return True
		else:
			return False