import random
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
                print(f"Configuration loaded from {config_file}: {len(config)} items found")
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
                mode = "oomlout_ai_roboclick"
                kwargs["mode"] = mode
                run_single(**kwargs)
                mode = "oomlout_corel_roboclick"
                kwargs["mode"] = mode
                run_single(**kwargs)
            else:
                print(f"Skipping non-directory: {dir}")
    else:
        print(f"No directory specified, running in current directory: {os.getcwd()}")
        mode = "oomlout_ai_roboclick"
        kwargs["mode"] = mode
        run_single(**kwargs)
        mode = "oomlout_corel_roboclick"
        kwargs["mode"] = mode
        run_single(**kwargs)
            
        
def run_single(**kwargs):
    file_action = kwargs.get("file_action", "configuration\\working.yaml")
    configuration = kwargs.get("configuration", {})
    mode = kwargs.get("mode", "")
    # Load actions from YAML file
    if True:
        print(f"loading configuration from {file_action}")
        try:
            with open(file_action, 'r') as file:
                workings = yaml.safe_load(file)
                print(f"Configuration loaded from {file_action}: {len(workings)}")
        except FileNotFoundError:
            print(f"Configuration file {file_action} not found.")
            return
        except yaml.YAMLError as e:
            print(f"Error parsing YAML file {file_action}: {e}")
            return
        
        base = workings.get(mode, [])
        if base != []:
            actions = base.get("actions", {})
        else:
            print(f"No actions found for mode {mode} in {file_action}")
            return

    

    print(f"Running with actions: {len(actions)}")

    file_test = workings.get("file_test", "")
    if file_test != "":
        file_test_absolute = os.path.join(kwargs.get("directory_absolute", ""), file_test)
        if os.path.exists(file_test_absolute):
            print(f"File test {file_test_absolute} exists, skipping actions.")
            return

    result = ""
    for action in actions:
        kwargs["action"] = action
        command = action.get("command")
        
        if command == "add_image":
            result = add_image(**kwargs)
        ###### file commands
        elif command == "file_copy":
            result = file_copy(**kwargs)
        elif command == "new_chat":
            kwargs
            new_chat(**kwargs)
        elif command == "query":
            query(**kwargs)
        elif command == "save_image_generated":
            save_image_generated(**kwargs)
        elif command == "save_image_search_result":
            save_image_search_result(**kwargs)
        elif command == "wait_for_file":
            result = wait_for_file(**kwargs)
        #if result is "exit", break the loop
        if result == "exit" or result == "exit_no_tab":
            print("Exiting due to 'exit' command.")
            break   
    if result != "exit_no_tab":
        robo.robo_chrome_close_tab(**kwargs)  # Close the tab after all actions are done

#actions


def add_image(**kwargs):
    return_value = ""
    print("add_image -- adding an image")
    kwargs["position_click"] = [750,995]
    position_click = kwargs.get("position_click", [960, 500])
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "working.png")
    directory_absolute = kwargs.get("directory_absolute", "")
    file_name_absolute = os.path.join(directory_absolute, file_name)
    file_name_abs = os.path.abspath(file_name) 
    print(f"Adding image {file_name} at position {position_click}")
    #test if filename exists
    if not os.path.exists(file_name_absolute):
        print(f"File {file_name_absolute} does not exist, skipping action.")
        return_value = "exit"
        return return_value
    #click on the position
    robo.robo_mouse_click(position=position_click, delay=2, button="left")  # Click on the image to focus
    robo.robo_keyboard_press_down(delay=1, repeat=2)  # Press down twice to select the file input
    robo.robo_keyboard_press_enter(delay=5)
    robo.robo_keyboard_send(string=file_name_absolute, delay=5)  # Type the file name
    robo.robo_keyboard_press_enter(delay=5)  # Press enter to confirm
    robo.robo_delay(delay=15)  # Wait for the image to be added
    #preess escape 5 times in case of any dialog boxes
    robo.robo_keyboard_press_escape(delay=5, repeat=5)  # Escape to close any dialogs
    return return_value

##### corel commands

##### file commands
def file_copy(**kwargs):
    import shutil
    file_source = kwargs.get("file_source", "")
    file_destination = kwargs.get("file_destination", "")
    
    return_value = ""

    if file_source == "" or file_destination == "":
        print("file_source or file_destination not set, skipping file copy")
        return
    
    #check if the file exists
    if os.path.isfile(file_source):
        print(f"copying {file_source} to {file_destination}")
        #use shutil to copy the file
        import shutil
        shutil.copy(file_source, file_destination)
    else:
        print(f"file {file_source} does not exist")
        return_value = "exit_no_tab"

    return return_value

def new_chat(**kwargs):
    print("new_chat -- opening up a new chat")
    robo.robo_chrome_open_url(url="https://chat.openai.com/chat", delay=15, message="    opening a new chat")    
    #type in start query
    start_query = "Hiya, chadikins the great I have a task for you can you help?" 
    robo.robo_keyboard_send(string=start_query, delay=5)
    robo.robo_keyboard_press_enter(delay=20)

def query(**kwargs):
    action = kwargs.get("action", {})
    print("query -- sending a query")
    #get the query from the action
    action = kwargs.get("action", {})
    query_text = action.get("text", "")
    robo.robo_keyboard_send(string=query_text, delay=5)
    print(f"Querying with text: {query_text}")
    robo.robo_keyboard_press_enter(delay=60)
    
def save_image_generated(**kwargs):
    kwargs["position_click"] = [960, 500]  # Default position for clicking the image    
    robo.robo_delay(delay=300)
    #random extra between 300 and 900 seconds
    delay = random.randint(300, 900)
    robo.robo_delay(delay=delay)  # Wait for the image to be generated
    robo.robo_mouse_click(position=[330,480], delay=2)  # Click on the image to focus
    robo.robo_keyboard_press_down(delay=1, repeat=10)  # Press down twice to select the file input
    save_image(**kwargs)

def save_image_search_result(**kwargs):
    kwargs["position_click"] = [813, 259]  # Default position for clicking the image
    position_click = kwargs.get("position_click")
    
    action = kwargs.get("action", {})
    index = action.get("index", 1)
    position_click[0] += (int(index)-1) * 200  # Adjust the x-coordinate based on the index
    file_name = action.get("file_name", "working.png")   
    directory_absolute = kwargs.get("directory_absolute", "")
    file_name_absolute = os.path.join(directory_absolute, file_name)
    file_name_abs = os.path.abspath(file_name) 
    print(f"Saving image as {file_name}")
    #save the image
    robo.robo_mouse_click(position=position_click, delay=2, button="left")  # Click on the image to focus
    robo.robo_mouse_click(position=position_click, delay=2, button="right")  # Click on the image to focus
    #press down twice
    robo.robo_keyboard_press_down(delay=1, repeat=2)
    robo.robo_keyboard_press_enter(delay=5)
    robo.robo_keyboard_send(string=file_name_absolute, delay=5)
    robo.robo_keyboard_press_enter(delay=5)
    robo.robo_keyboard_send(string="y", delay=5)
    robo.robo_keyboard_press_escape(delay=5, repeat=5)  # Escape to close any dialogs

    print(f"Image saved as {file_name}")

def save_image(**kwargs):
    position_click = kwargs.get("position_click", [960, 500])
    
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "working.png")   
    directory_absolute = kwargs.get("directory_absolute", "")
    file_name_absolute = os.path.join(directory_absolute, file_name)
    file_name_abs = os.path.abspath(file_name) 
    print(f"Saving image as {file_name}")
    #save the image
    robo.robo_mouse_click(position=position_click, delay=2, button="right")  # Click on the image to focus
    #press down twice
    robo.robo_keyboard_press_down(delay=1, repeat=2)
    robo.robo_keyboard_press_enter(delay=5)
    robo.robo_keyboard_send(string=file_name_absolute, delay=5)
    robo.robo_keyboard_press_enter(delay=5)
    robo.robo_keyboard_send(string="y", delay=5)
    robo.robo_keyboard_press_escape(delay=5, repeat=5)  # Escape to close any dialogs
    print(f"Image saved as {file_name}")

def wait_for_file(**kwargs):
    print("wait_for_file -- skip if a necessary file doesnt exist")
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "working.png")
    directory_absolute = kwargs.get("directory_absolute", "")
    file_name_absolute = os.path.join(directory_absolute, file_name)
    file_name_abs = os.path.abspath(file_name) 
    
    
    return_value = ""

    # Wait for the file to be created
    if not os.path.exists(file_name_absolute):
        # If the file does not exist, wait and check again
        return_value = "exit_no_tab"        
        print(f"File {file_name_absolute} not found.")
    return return_value

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