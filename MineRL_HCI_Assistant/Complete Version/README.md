#  **Can intelligent agents play Minecraft? Developing a hierarchical reinforcement learning agent to play Minecraft.**
 
**Note:**

This study is a collaborative project between **Max Planck Institute (Germany)** and **Dr. Shihan Wang (Utrecht University)**. and it is under supervision of **Dr. Shihan Wang**.


## **Weekly meeting report:**
**The Weekly meeting report file includes all weekly meeting report.**. 


## **Instruction of Forger baseline code**
1. Preparations:
    1. Request for resources: Open Jupyter Hub, request for short mode (at least 8 core CPU, 1 GPU, 16 memory, 1/2 hours)<br>
    2. Load environment:<br>
        open Terminal and run code:
        `module load python/3.8`, `module load conda`, `conda activate MineRL` <br>
    3. Prepare code: Upload forger-baseline.zip, then open the “Unzip.ipynb” notebook, run the code to unzip the file.
    4. Install packages:<br>
        open Terminal and run code:
        `cd forger/forger-baseline/`, `pip install -r requirements.txt`<br><br>
2. Run simple_set experiment:
    1. In terminal run code: `python3 train_simple_set.py --config simple_set_config.yaml`
    2. Hyper-parameter can be set in *config simple_set_config.yaml*



