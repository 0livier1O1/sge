import glob, logging, os, time
from sge.agent import Agent
from sge.jobs import JobPool


class Master(object):
    def __init__(
            self, 
            base_path,
            max_jobs=10, 
            shared_data_path=None,
            logger=None
        ) -> None:
        super(Master, self).__init__()
        if not os.path.exists(base_path + "agent_pool"):
            raise FileNotFoundError(f"Agent pool directory not found at {base_path}/agent_pool")
        
        self.base_path = base_path
        self.shared_data_path = shared_data_path
        self.max_jobs = max_jobs
        self.count_jobs = 0
        self.job_pool = None
        self.previous_job = None
        self.logger = logger if logger else logging.getLogger(__name__)

        self.available_agents = []
        self.known_agents = {}
        self.time = 0

    def __delayed_call__(self, func, interval):
        if self.time % interval == 0:
            func()
        else:
            return None
        
    def __tik(self, sec):
        self.time += sec
        time.sleep(sec)
    
    def __check_available_agent__(self):
        self.available_agents.clear()
        agents = glob.glob(self.base_path + 'agent_pool/*.POOL')  
        agents_id = [ a.split('/')[-1][:-5] for a in agents ]
        
        for agent in list(self.known_agents.keys()):
            if agent not in agents_id:
                self.logger.info('Dead agent id = {} found!'.format(agent))
                self.known_agents.pop(agent, None)

        for agent in agents_id:
            if agent in self.known_agents.keys():
                if self.known_agents[agent].is_available():
                    self.available_agents.append(self.known_agents[agent])
            else:
                # TODO: Put new agents directly in available agents
                self.known_agents[agent] = Agent(
                    sge_job_id=agent, 
                    base_path=self.base_path, 
                    shared_data_path=self.shared_data_path)
                self.logger.info('New agent id = {} found!'.format(agent))
    
    def __assign_job__(self):
        self.__check_available_agent__() # TODO: Put new agents directly in available agents
        if len(self.available_agents) > 0:
            for agent in self.available_agents:
                self.job_pool.distribute(agent)

    def __collect__(self):
        n = self.job_pool.collect()
        self.count_jobs += n

    def _is_finished(self):
        if self.count_jobs >= self.max_jobs:
            return True
        else:
            if self.job_pool.is_finished():
                return True
            else:
                return False

    def run(self, tasks):
        self.job_pool = JobPool(
            to_distribute=tasks, 
            base_path=self.base_path, 
            shared_data_path = self.shared_data_path,
            logger=self.logger
        )
        
        while not self._is_finished():
            self.__delayed_call__(self.__check_available_agent__, 4)
            self.__delayed_call__(self.__assign_job__, 4)
            self.__delayed_call__(self.__collect__, 4)
            self.__tik(1)


