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


## **Instruction of the program**
1. Before you run the program, make sure you intsall python packages in the 'dependencies.txt'.
2. You will find the instruction notebook in the 'HCI/HCI_module_notebook.ipynb'.

