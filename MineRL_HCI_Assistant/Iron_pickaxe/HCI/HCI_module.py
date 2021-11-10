import json
import yaml
import numpy as np
import gym

from ForgER.agent import Agent
from ForgER.replay_buff import AggregatedBuff
from ForgER.model import get_network_builder

class HCI_basic_agents:
 """
 Goal: HCI_basic_agents Class provides basic action recommendation to human player.

 """

 def __init__(self):
  """
  The class will be initialzed by steps below.
  1.Load the agent config
  2.Set agent directory.
  3.Set replay buffer, obs_space, act_space
  4.load log and cobblestone agents
  """
  self.agent_config = self.load_config()

  self.agents_dir = 'saved_agents/'

  self.env_dict = {'action': {'shape': 1, 'dtype': 'int32'}, 'reward': {'dtype': 'float32'}, 'done': {'dtype': 'bool'},
                   'n_reward': {'dtype': 'float32'}, 'n_done': {'dtype': 'bool'}, 'actual_n': {'dtype': 'float32'},
                   'demo': {'dtype': 'float32'}, 'state': {'shape': (64, 64, 6), 'dtype': np.dtype('uint8')},
                   'next_state': {'shape': (64, 64, 6), 'dtype': np.dtype('uint8')},
                   'n_state': {'shape': (64, 64, 6), 'dtype': np.dtype('uint8')}}

  self.dtype_dict = {'action': 'int32', 'reward': 'float32', 'done': 'bool', 'n_reward': 'float32', 'n_done': 'bool',
                     'actual_n': 'float32', 'demo': 'float32', 'state': np.dtype('uint8'),
                     'next_state': np.dtype('uint8'),
                     'n_state': np.dtype('uint8'), 'weights': 'float32', 'indexes': 'int32'}

  self.key_to_dict = {
   # forward
   0: 'forward',
   # camera [0,5]
   1: 'turn camera right',
   # attack
   2: 'attack',
   # camera [5,0]
   3: 'turn camera down',
   # camera [-5,0]
   4: 'turn camera up',
   # camera [0,-5]
   5: 'turn camera left',
   # forward + jump
   6: 'forward and jump',
   # left
   7: 'left',
   # right
   8: 'right',
   # back
   9: 'back'}

  self.template = ' I recommend you to {}.'

  self.obs_space = gym.spaces.box.Box(0, 255, (64, 64, 6), np.uint8)
  self.act_space = gym.spaces.discrete.Discrete(10)

  self.replay_buff = AggregatedBuff(32, env_dict=self.env_dict)

  # self, config, replay_buffer, build_model, obs_space, act_space, dtype_dict=None, log_freq=100
  self.log_agent = Agent(config=self.agent_config, replay_buffer=self.replay_buff,
                         build_model=get_network_builder('minerl_dqfd'), obs_space=self.obs_space,
                         act_space=self.act_space)
  self.cobb_agent = Agent(config=self.agent_config, replay_buffer=self.replay_buff,
                          build_model=get_network_builder('minerl_dqfd'), obs_space=self.obs_space,
                          act_space=self.act_space)

 def load_config(self):
  """
  goal: load minerl agent config.
  """
  config = './ForgER/minerl_config.yaml'
  with open(config, "r") as config_file:
   config = yaml.load(config_file, Loader=yaml.FullLoader)
   agent_config = config['agent']
  return agent_config

 def load_agents(self):
  """
  goal: load minerl log and cobblestone agent.
  """
  print('loading agents now...')
  if os.path.exists(self.agents_dir):
   self.log_agent.load(self.agents_dir + '/log/model.ckpt')
   self.cobb_agent.load(self.agents_dir + 'cobblestone/model.ckpt')
   print('agents loaded...')

 def recommend_action(self, obs, task):
  """
  goal: provide basic action to human player given obs(image) and task(log or cobblestone)
  """
  if task == 'log':
   action = self.agent_infer_action(self.log_agent, obs)
   suggestion = self.action_to_recommendation(action)
   return suggestion
  if task == 'cobblestone':
   action = self.agent_infer_action(self.cobb_agent, obs)
   suggestion = self.action_to_recommendation(action)
   return suggestion
  else:
   raise Exception('task is error! task should be one of [\'log\', \'cobblestone\']')

 def action_to_recommendation(self, int_action):
  """
  goal: Because the action that minerl agents infered is int data structure, we need to convert int action to text action recommendation.
  """
  # convert the int action to the corresponding string
  str_action = self.key_to_dict[int_action]
  return self.template.format(str_action)

 def agent_infer_action(self, agent, obs):
  """
  goal: input obs(image) to log or cobblestone agents, then return the int action recommendation.
  """
  # call agent(log or cobblestone) to give action, it will return a int, we will convert the int action to the string
  return agent.give_basic_action_recommendation(obs)


class HCI_controller:
 """
 Goal: HCI_controller Class provides subtask, special action, as well as basic action(if include_basic_actions = True)
 recommendation to human player.

 """

 def __init__(self, include_basic_actions=False, basic_action_delay=0):
  """
  The class will be initialzed by steps below.
  1.Load the chain
  2.initialze the subtask_nodes and special_actions lists according to the chain.
  3.set stage to 0 (stage will determine which stage we are on, and the HCI_controller will provide recommendation according to the )
  4.if include_basic_actions = True, create an HCI_basic_agents instance and set delay ect.
  """
  self.chain = self.load_chain()
  self.subtask_nodes, self.special_actions = self.create_nodes(self.chain)
  self.stage = 0
  self.include_basic_actions = include_basic_actions
  # create a HCI_basic_agents instantce to provide basic actions
  if self.include_basic_actions:
   self.basic_agents = HCI_basic_agents()
   # provide basic action every "basic_action_delay" step, e.g: basic_action_delay = 10, basic actions will
   # be provided in the last time when you call the "give_suggestion" 10 times!
   self.basic_action_delay = basic_action_delay
   self.basic_action_count = 0

 @staticmethod
 def load_chain():
  """
  goal: load chain.
  """
  chain_path = './HCI/chain.json'
  with open(chain_path, "r") as f:
   chain = json.load(f)
  return chain

 @staticmethod
 def str_to_action_dict(action_):
  """
  goal: convert string action to dict.
  str -> dict
  :param action_:
  :return:
  """
  a_, _, value = action_.split(":")
  return {a_: value}

 @classmethod
 def get_crafting_actions_from_chain(cls, chain_, node_name_):
  """
  goal: getting crafting actions from chain for subtask item.
  """
  previous_actions = []
  for vertex in chain_:
   if vertex == node_name_:
    break
   if not cls.is_subtask(vertex):
    previous_actions.append(vertex)
   else:
    previous_actions = []
  return [cls.str_to_action_dict(action_) for action_ in previous_actions]

 @staticmethod
 def is_subtask(name):
  """
  goal: classify special actions and subtasks
  """
  return len(name.split(":")) == 2

 @staticmethod
 def list2dict(a):
  it = iter(a)
  res_dct = dict(zip(it, it))
  return res_dct

 @staticmethod
 def split_subtask_NumItem(subtask_node):
  """
  goal: Split the subtask_node to name of the subtask and its requirement of number.
  """
  subtask_name, subtask_num = subtask_node.split(":")
  return subtask_name, int(subtask_num)

 def check_stage(self, state):
  """
  goal: Check which stage we are in according to the state.
  """
  cur_subtask = self.subtask_nodes[self.stage]
  if self.finish_requirement(state, cur_subtask):
   self.stage += 1
   return self.check_stage(state)
  else:
   return (self.stage)

 @classmethod
 def finish_requirement(cls, state, cur_subtask):
  """
  Check whether human player obtained sufficient item of current subtask.
  """
  cur_subtask_name, cur_subtask_num = cls.split_subtask_NumItem(cur_subtask)
  if state['inventory'][cur_subtask_name] >= cur_subtask_num:
   return True
  else:
   return False

 @classmethod
 def create_nodes(cls, chain):
  """
  goal: method to initialize the class: output subtasks,special_actions given a chain
  """
  subtasks = [item for item in chain if cls.is_subtask(item)]

  special_actions = []
  for subtask in subtasks:
   special_actions.append(cls.get_crafting_actions_from_chain(chain, subtask))

  return subtasks, special_actions

 def give_suggestion(self, inventory, obs=None):
  """
  goal: Assign suggestion to human player given inventory infomation.

  """

  # determine whether finished the game.
  if self.stage < len(self.subtask_nodes):
   suggest_subtask = self.subtask_nodes[self.stage]
   suggest_sp_action = self.special_actions[self.stage]
   # determine if the current subtask has finished.
   if self.finish_requirement(inventory, suggest_subtask):
    # enter to next stage
    self.stage += 1
    return self.give_suggestion(inventory, obs)
   # the current subtask has not finished.
   else:
    # determine if now is the initial substask
    if self.stage == 0:
     # if provide basic actions
     if self.include_basic_actions:
      basic_action_recommendation = self.provide_basic_action(obs)
     else:
      basic_action_recommendation = ''
     # provide subtask and special action
     subtask_sp_action_recommendation = self.generate_utterance(suggest_subtask, suggest_sp_action, init_subtask=True)
     recommendations = subtask_sp_action_recommendation + basic_action_recommendation
     return recommendations
    # if now is not initial substask
    else:
     if self.include_basic_actions:
      basic_action_recommendation = self.provide_basic_action(obs)
     else:
      basic_action_recommendation = ''
     subtask_sp_action_recommendation = self.generate_utterance(suggest_subtask, suggest_sp_action, init_subtask=False)
     recommendations = subtask_sp_action_recommendation + basic_action_recommendation
     return recommendations

  # finished the game
  else:
   return 'Congrats! You have finished the process!'

 def provide_basic_action(self, obs):
  """
  goal: provide basic action given obs(image).
  """
  # count how many times this function has been called
  self.basic_action_count += 1
  if self.basic_action_delay == 0:
   reach_delay = 0
  else:
   reach_delay = self.basic_action_count % self.basic_action_delay

  # if provide basic action, and reached the delay setting
  if self.include_basic_actions == True and reach_delay == 0:
   if self.stage < len(self.subtask_nodes):
    suggest_subtask = self.subtask_nodes[self.stage]
   else:
    suggest_subtask = 'None'

   if 'log' in str(suggest_subtask):
    return self.basic_agents.recommend_action(obs, 'log')
   elif 'cobblestone' in str(suggest_subtask):
    return self.basic_agents.recommend_action(obs, 'cobblestone')
   # if not log or cobblestone, return an empty string
   else:
    return ''
  else:
   return ''

 @staticmethod
 def generate_utterance(suggest_subtask, suggest_sp_action=None, init_subtask=False):
  """
  goal: generate utterance template.
  """
  subtask_template = [
   'Next, you need to get {} {} item(s).',
   'Good job, now perhaps try to get {} {}.',
   'Sick! Collect {} {} item from now on!',
   'Yooo, nice move! Next, I suggest you to find {} {} item(s).',
   'Previous one was hard, right? Now you can collect {} {}, trust yourself!',
   'Noooo way! Thats dope! Now you need to obtain {} {} item(s).',
   'Come on! This game might be too easy for you! Try to collect {} {} from now on.']

  sp_action_template_two = [
   'In order to do that, you have to do action \"{} {}\", then \"{} {}\".',
   'In an attempt to do that, you have to do action \"{} {}\", then \"{} {}\".',
   'How to do that? you have to do action \"{} {}\", then \"{} {}\", easy peasy! ',
   'The magic behind that is to do action \"{} {}\", then \"{} {}\"']

  sp_action_template_four = [
   'In order to do that, you have to do action \"{} {}\".',
   'In an attempt to do that, you have to do action \"{} {}\".',
   'How to do that? you have to do action \"{} {}\", easy peasy! ',
   'The magic behind that is to do action \"{} {}\", try it now?']

  subtask_name, subtask_num = suggest_subtask.split(':')

  # fixed template for initial subtask
  if init_subtask == True:
   template = 'Welcome to the game! I\'m your personal AI assistant, I will give you suggestions to help you play this wonderful game! Now try to collect {} {}.'.format(
    subtask_num, subtask_name)
  else:
   template = random.choice(subtask_template).format(subtask_num, subtask_name)

  # if it has special action
  if suggest_sp_action:
   # if it is four special actions
   if len(suggest_sp_action) > 1:
    sp_action, sp_item = list(suggest_sp_action[0].items())[0]
    sp_action_s, sp_item_s = list(suggest_sp_action[1].items())[0]
    sp_action_recommend = random.choice(sp_action_template_four)
    template = template + " In order to do that, you have to do action \"{} {}\", then \"{} {}\".".format(sp_action,
                                                                                                          sp_item,
                                                                                                          sp_action_s,
                                                                                                          sp_item_s)
   # if it is two special actions
   else:
    sp_action, sp_item = list(suggest_sp_action[0].items())[0]
    sp_action_recommend = random.choice(sp_action_template_two)
    template = template + " In order to do that, you have to do action \"{} {}\".".format(sp_action, sp_item)

  return template