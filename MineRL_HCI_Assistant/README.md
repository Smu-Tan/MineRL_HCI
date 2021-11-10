#  **MineRL HCI assistant**
![image](https://user-images.githubusercontent.com/79228128/140317038-be80fe22-aa5b-47c5-8b64-ea035c2cea71.png)
#### 1. Subtask recommendation
     a. Assigning subtask for human-player.
     b. Subtask could be the chain in HDQfD or Markov-controller or hand-crafted chain.
     c. Potential research: Comparing Human-player performance between different provided chains.
#### 2. Action recommendation
     a. Assigning action in the subtask for human-player.
     b. For action, things might be a bit complex.
     c. 10 basic actions: 
        Move -- [forward, back, left, right]  
        Camera -- [up, down, left, right] 
        Combo -- [forward+jump] 
        Attack 
     d. Special actions:
        Craft -- [Planke, stick, crafting_table, wooden_pickaxe, etc]: converting raw material
        Place -- [item]: placing item(s)
        NearbyCraft -- [item]: Craft item(s) when something nearby
        Equip -- [item]


# **Instruction of the program**
1. Before you run the program, make sure you intsall python packages in the 'dependencies.txt'.
2. You will find the instruction notebook in the 'HCI/HCI_module_notebook.ipynb'.

# **Documentation**

## **HCI_basic_agents**
> **HCI_basic_agents Class provides basic action recommendation to human players.**

|Function|Input|Output|Description
|----|-------|-------|---------------------|
|init|None|A instance|Initialization of the class will do certain things once you create a new instance: <br>1. set hyper-perameters for agents, e.g: *replay buffer, obs_space, act_space*.<br> 2. load MineRL AI agents (forger) from the `./MineRL_HCI_Assistant/saved_agents/` folder.<br>|
|load_config|None|MineRL agent config|Function to load agent configuration`(minerl_config.yaml file)`.|
|load_agents|None|None|Function to load MineRL log and cobblestone agents under the `./saved_agents` folder.|
|agent_infer_action|1.agent (*log or cobb agent*),<br>2.obs (*image of the current state*)|agent int action recommendation|Function to make corresponding MineRL agent to provide basic action recommendation. Notes: This function will call `ForgER.agent` to provide action, which based on tensorflow.|
|action_to_recommendation|int_action|text action recommendation|Because the action that minerl agents infered is int data structure, we need to convert it to the corresponding text action recommendation. It will refer `self.key_to_dict` to convert the int action to the string action first, e.g: 0 -> 'forward'.<br> Notes: The function will call `self.template` to generate the text recommendation, therefore, if you want to modify the template, please modify `self.template` in the init part.|
|recommend_action|None|MineRL agent config|Function to provide basic action to human player given obs (image) and task (log or cobblestone). The function will first infer int action considering what kind of task is given, then convert int action recommendation to readable text.|
-----
<br/>

## **HCI_controller**
> **HCI_controller Class provides subtask, special action, as well as basic action(if include_basic_actions = True) text  recommendation sentence(s) to human players.**


|Function|Input|Output|Description
|----|-------|-------|---------------------|
|init|include_basic_actions, basic_action_delay|A instance|Initialization of the class will do certain things once you create a new instance: <br>1. Load the chain, and initialze the subtask_nodes and special_actions lists according to the chain.<br> 2. set stage to 0 (stage will determine which stage we are on, and the HCI_controller will provide recommendation according to the `self.stage`)<br>3. if `include_basic_actions = True`, create an `HCI_basic_agents` instance and set delay ect.|
|load_chain|None|Loaded chain|Function to load MineRL chain under the `./HCI/`.|
|create_nodes|chain|subtasks, special_actions|method to initialize the class: output subtasks,special_actions given a chain|
|str_to_action_dict|str_action|python dict|convert string action to python dictionary.|
|is_subtask|str|boolean value|classify special actions and subtasks.|
|list2dict|list|python dict|Split the subtask_node to name of the subtask and its requirement of number.|
|split_subtask_NumItem|subtask_node|subtask_name, subtask_num|convert list to python dictionary.|
|get_crafting_actions_from_chain|chain, node_name|list of special actions|getting special actions from chain for subtask item.|
|check_stage|state|stage|Function to check which stage we are in according to the state.|
|finish_requirement|state, cur_subtask|boolean value|Function to check whether human player obtained sufficient item of current subtask given state and  current subtask|
|provide_basic_action|obs(image of current state)|text action recommendation|Function to provide basic action text recommendation given obs(image).<br> Notes: 1. This function will only be called if `include_basic_actions = True`.<br> 2. It will call `recommend_action` funtion in **HCI_basic_agents** class to provide basic actions given the subtask is one of the ['log', 'cobblestone'].|
|generate_utterance|suggest_subtask, suggest_sp_action, init_subtask(boolean)|recommendation template.|Function to generate recommendation template given suggest_subtask, suggest_sp_action and init_subtask(boolean).|
|give_suggestion|inventory, obs (image of current state)|text recommendation sentence|Function to assign suggestion to human player given inventory infomation.<br>Notes: In this function, we will <br>1. first check whether the game has been finished yet: `Obtained the IronPickaxe`.<br>2. determine if the current subtask has finished: obtained certain number of item in a subtask.<br>3. provide subtask and special action(s) according to the `self.stage`.<br>4. If `include_basic_actions = True`, call `provide_basic_action` funtion to capture the text action recommendation that MineRL agent gave.|
-----

## **Data structure of the input to the give_suggestion function**
|Name|<div style="width:500px">Data structure</div>|Description
|----|-------|-----|
|Inventory_data|Inventory_data: Python Dictionary<br><br><pre>Inventory_data = { “equipped_items.mainhand.type”: str,<br>                   “inventory”: <br>                          { “coal”: int,<br>                            “cobblestone”: int,<br>                            “crafting_table”: int,<br>                            “dirt”: int,<br>                            “furnace”: int,<br>                            “iron_axe”: int,<br>                            “iron_ingot”: int,<br>                            “iron_ore”: int,<br>                            “iron_pickaxe”: int,<br>                            “log”: int,<br>                            “planks”: int,<br>                            “stick”: int,<br>                            “stone”: int,<br>                            “stone_axe”: int,<br>                            “stone_pickaxe”: int,<br>                            “torch”: int,<br>                            “wooden_axe”: int,<br>                            “wooden_pickaxe”: int }<br>                  }|In general, Inventory_data contains the human player’s current inventory information and the mainhand equipped item type. <br><br>For example, the mainhand equipped item type could be any items in the inventory list(keys of inventory), such as coal, cobblestone, etc. To keep consistency, Items not in the inventory list can be considered as ‘others’. And no item in the mainhand will be ‘none’.<br><br>On the other hand, the inventory in the inventory_data is a python sub-dictionary containing 18 different item keys, and their values is python int.
|Image_data|Image_data: Python Numpy array with shape: (64,64,3), dtype: uint8. e.g:<br><br><pre>img = array( [[[[[143, 181, 253],<br>                 [143, 181, 253],<br>                 [143, 181, 255],<br>                 ...,<br>                 [149, 182, 253],<br>                 [150, 183, 247],<br>                 [150, 183, 247]],<br>              ...<br>                 [ 70,  49,  34],<br>                 [ 76,  51,  32],<br>                 [108,  83,  64]]]]], dtype=uint8)|Image_data is the current POV image data of human players. It must be a numpy array, with shape: (64,64,3), dtype: unit8.<br><br>In order to test whether the image converted to the right numpy array: verify the shape of the image is (64,64,3) <br><br>you could use the code below to visualize the image, then see whether the original image is the visualized array.<br><br>**import matplotlib.pyplot as plt**<br><br>**plt.imshow(img, interpolation='nearest')**
-----

