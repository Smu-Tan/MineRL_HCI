import json
import random


class HCI_controller:
 """
 Goal: HCI_controller Class provides subtask, special action, as well as basic action(if include_basic_actions = True)
 recommendation to human player.

 """

 def __init__(self):
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
  self.init_stage = True

 @staticmethod
 def load_chain():
  """
  goal: load chain.
  """
  chain_path = './HCI/ironpickaxe_chain.json'
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
    if self.init_stage:
      self.init_stage=False
      # provide subtask and special action
      subtask_sp_action_recommendation = self.generate_utterance(suggest_subtask, suggest_sp_action, init_subtask=True)
      return subtask_sp_action_recommendation
    # if now is not initial substask
    else:
     subtask_sp_action_recommendation = self.generate_utterance(suggest_subtask, suggest_sp_action, init_subtask=False)
     recommendations = subtask_sp_action_recommendation
     return recommendations

  # finished the game
  else:
   return 'Congrats! You have finished the process!'

 @staticmethod
 def generate_utterance(suggest_subtask, suggest_sp_action=None, init_subtask=False):
  """
  goal: generate utterance template.
  """
  subtask_template = [
   'Next, you need to get {} {} item(s).',
   'Good job, now perhaps try to get {} {}.',
   'Collect {} {} item from now on!',
   'Next, I suggest you to find {} {} item(s).',
   'Now you can collect {} {}, trust yourself!',
   'Now you need to obtain {} {} item(s).',
   'Try to collect {} {} from now on.']

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