
import argparse
import yaml
import robo
import copy
import sys
import os

def main(**kwargs):
    
    #load confuiguration
    if True:
        config_file = "configuration\\oomlout_ai_chat_gpt_robo_click_configuration.yaml"
        try:
            with open(config_file, 'r') as file:
                config = yaml.safe_load(file)
                print(f"Configuration loaded from {config_file}: {config}")
        except FileNotFoundError:
            #try in the current file directory to use the default one
            config_file = os.path.join(os.path.dirname(__file__), "configuration", "oomlout_ai_chat_gpt_robo_click_configuration.yaml")
            try:
                with open(config_file, 'r') as file:
                    config = yaml.safe_load(file)
                    print(f"Configuration loaded from {config_file}: {config}")
            except FileNotFoundError:
                print(f"Configuration file {config_file} not found.")
                return
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {config_file}: {e}")
            return
        kwargs["configuration"] = config
        coordinates = config.get("coordinates", [])
        kwargs["coordinates"] = coordinates

    #deciding how to run
    file_action = kwargs.get("file_action", "configuration\\working.yaml")
    #make it absolute
    file_action = os.path.abspath(file_action)

    #directory
    directory = kwargs.get("directory", "")

    if directory != "":
        pass
        import glob
        directories = glob.glob(os.path.join(directory, "*"))
        for dir in directories:         
            kwargs["directory"] = dir   
            directory_absolute = os.path.abspath(dir)
            kwargs["directory_absolute"] = directory_absolute

            if os.path.isdir(dir):
                file_action = os.path.join(dir, "working.yaml")
                print(f"running file_action: {file_action}")
                kwargs["file_action"] = file_action
                run_single(**kwargs)
            else:
                print(f"Skipping non-directory: {dir}")
    else:
        print(f"No directory specified, running in current directory: {os.getcwd()}")
        run_single(**kwargs)
            
        
def run_single(**kwargs):
    file_action = kwargs.get("file_action", "configuration\\working.yaml")
    configuration = kwargs.get("configuration", {})
    # Load actions from YAML file
    if True:
        print(f"loading configuration from {file_action}")
        try:
            with open(file_action, 'r') as file:
                actions = yaml.safe_load(file)
                print(f"Configuration loaded from {file_action}: {actions}")
        except FileNotFoundError:
            print(f"Configuration file {file_action} not found.")
            return
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {file_action}: {e}")
            return
        
        actions = actions.get("actions", [])
        kwargs["actions"] = actions

    

    print(f"Running with actions: {actions}")

    for action in actions:
        kwargs["action"] = action
        command = action.get("command")
        if command == "new_chat":
            kwargs
            new_chat(**kwargs)
        elif command == "query":
            query(**kwargs)
        elif command == "save_image":
            save_image(**kwargs)

#actions

def new_chat(**kwargs):
    print("new_chat -- opening up a new chat")
    robo.robo_chrome_open_url(url="https://chat.openai.com/chat", delay=15, message="    opening a new chat")    
    #type in start query
    start_query = "Hiya, chadikins the great I have a task for you can you help?" 
    robo.robo_keyboard_send(string=start_query, delay=5)
    robo.robo_keyboard_press_enter(delay=10)

def query(**kwargs):
    action = kwargs.get("action", {})
    print("query -- sending a query")
    #get the query from the action
    action = kwargs.get("action", {})
    query_text = action.get("text", "")
    robo.robo_keyboard_send(string=query_text, delay=5)
    print(f"Querying with text: {query_text}")
    robo.robo_keyboard_press_enter(delay=30)
    
def save_image(**kwargs):
    robo.robo_delay(delay=300)
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "working.png")   
    directory_absolute = kwargs.get("directory_absolute", "")
    file_name_absolute = os.path.abspath(file_name)
    file_name_abs = os.path.abspath(file_name) 
    print(f"Saving image as {file_name}")
    #save the image
    robo.robo_mouse_click(position=[960, 500], delay=2, button="right")  # Click on the image to focus
    #press down twice
    robo.robo_keyboard_press_down(delay=1, repeat=2)
    robo.robo_keyboard_press_enter(delay=5)
    robo.robo_keyboard_send(string=file_name_absolute, delay=5)
    robo.robo_keyboard_press_enter(delay=5)
    print(f"Image saved as {file_name}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='My CLI tool')
    parser.add_argument('--file_action', '-fa', help='Enable verbose output', default="not_set")
    parser.add_argument('--count', type=int, default=1, help='Number of iterations')
    args = parser.parse_args()
    
    kwargs = copy.deepcopy(vars(args))

    if kwargs["file_action"] == "not_set":
        kwargs["file_action"] = "configuration/working.yaml"
    
    #print out kwargs
    print(f"Running with arguments:")
    for key, value in kwargs.items():
        print(f"    {key}: {value}")
    
    main(**kwargs)