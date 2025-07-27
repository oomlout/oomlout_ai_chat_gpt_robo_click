import random
import argparse
import yaml
import robo
import copy
import sys
import os

def main(**kwargs):
    mode = kwargs.get("mode", "")
    filt = kwargs.get("filter", "")
    #if mode isnt a list make it one
    if not isinstance(mode, list):
        mode = [mode]
        kwargs["mode"] = mode
    mode_local = copy.deepcopy(mode)
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
        #remove directory from each entry
        if True:
            directories = [os.path.basename(dir) for dir in directories if os.path.isdir(dir)]
            
        for dir in directories:   
            if filt == "" or filt in dir:
                #make dir absolute
                dir = os.path.join(directory, dir)
                kwargs["directory"] = dir
                directory_absolute = os.path.abspath(dir)
                kwargs["directory_absolute"] = directory_absolute

                if os.path.isdir(dir):
                    file_action = os.path.join(dir, "working.yaml")
                    print(f"running file_action: {file_action}")
                    kwargs["file_action"] = file_action
                    if "oomlout_ai_roboclick" in mode_local:                    
                        mode = "oomlout_ai_roboclick"
                        kwargs["mode"] = mode
                        run_single(**kwargs)
                    if "oomlout_corel_roboclick" in mode_local:
                        mode = "oomlout_corel_roboclick"
                        kwargs["mode"] = mode
                        run_single(**kwargs)
                        for i in range(1, 10):
                            mode = f"oomlout_corel_roboclick_{i}"
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

    file_test = base.get("file_test", "")
    file_test_mode = base.get("file_test_mode", "exists")
    if file_test != "":
        file_test_absolute = os.path.join(kwargs.get("directory_absolute", ""), file_test)
        if file_test_mode == "exists":
            if os.path.exists(file_test_absolute):
                print(f"File test {file_test_absolute} exists, skipping actions.")
                return
        else:
            if not os.path.exists(file_test_absolute):
                print(f"File test {file_test_absolute} does not exist, skipping actions.")
                return

    result = ""
    for action in actions:
        kwargs["action"] = action
        command = action.get("command")
        
        if command == "add_image":
            result = add_image(**kwargs)
        #ai ones
        #ai_mode
        elif command == "ai_set_mode":
            ai_set_mode(**kwargs)
        elif command == "close_tab":
            result = close_tab(**kwargs)
        #corel commands
        #corel_close
        elif command == "corel_close_file":
            corel_close_file(**kwargs)        
        elif command == "corel_import":
            corel_import(**kwargs)
        elif command == "corel_open":        
            corel_open(**kwargs)
        elif command == "corel_save":
            corel_save(**kwargs)
        elif command == "corel_save_as":
            corel_save_as(**kwargs)        
        elif command == "corel_export":
            corel_export(**kwargs)
        elif command == "corel_paste":
            corel_paste(**kwargs)
        elif command == "corel_select_all":
            robo.robo_corel_select_all(**kwargs)
        #corel_set_position
        elif command == "corel_set_size":
            corel_set_size(**kwargs)
        elif command == "corel_set_position":
            corel_set_position(**kwargs)
        elif command == "corel_copy":
            corel_copy(**kwargs)
        elif command == "corel_paste":
            robo.robo_corel_paste(**kwargs)
        #corel trace clipart
        elif command == "corel_trace":
            corel_trace(**kwargs)
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

def close_tab(**kwargs):
    print("close_tab -- closing the current tab")
    #close the current tab
    robo.robo_chrome_close_tab(**kwargs)
    #wait for 5 seconds
    robo.robo_delay(delay=5)  # Wait for the tab to close

##### corel commands
def corel_copy(**kwargs):
    print("corel_copy -- copying selected items in corel")
    #copy selected items in corel
    robo.robo_corel_copy(**kwargs)


def corel_close_file(**kwargs):
    print("corel_close_file -- closing corel")
    #close corel
    robo.robo_corel_close_file(**kwargs)

def corel_export(**kwargs):
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    file_type = action.get("file_type", "pdf")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    kwargs2["file_type"] = file_type
    robo.robo_corel_export_file(**kwargs2)

def corel_import(**kwargs):
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    x = action.get("x", "")
    y = action.get("y", "")
    width = action.get("width", "")
    height = action.get("height", "")
    max_dimension = action.get("max_dimension", "")

    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    if x != "":
        kwargs2["x"] = x
    if y != "":
        kwargs2["y"] = y
    if width != "":
        kwargs2["width"] = width
    if height != "":
        kwargs2["height"] = height
    if max_dimension != "":
        kwargs2["max_dimension"] = max_dimension

    robo.robo_corel_import_file(**kwargs2)

def corel_open(**kwargs):
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    robo.robo_corel_open(**kwargs2)

def corel_paste(**kwargs):
    print("corel_paste -- pasting copied items in corel")
    #paste copied items in corel
    action = kwargs.get("action", {})
    x = action.get("x", "")
    y = action.get("y", "")
    width = action.get("width", "")
    height = action.get("height", "")

    kwargs2 = copy.deepcopy(kwargs)
    if x != "":
        kwargs2["x"] = x
    if y != "":
        kwargs2["y"] = y
    if width != "":
        kwargs2["width"] = width
    if height != "":
        kwargs2["height"] = height
    robo.robo_corel_paste(**kwargs2)

def corel_save(**kwargs):
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    robo.robo_corel_save(**kwargs2)

def corel_save_as(**kwargs):
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    robo.robo_corel_save_as(**kwargs2)

def corel_set_position(**kwargs):
    print("corel_set_position -- setting position")
    action = kwargs.get("action", {})
    x = action.get("x", "")
    y = action.get("y", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["x"] = x
    kwargs2["y"] = y
    robo.robo_corel_set_position(**kwargs2)

def corel_set_size(**kwargs):
    print("corel_set_size -- setting size")
    action = kwargs.get("action", {})
    width = action.get("width", "")
    height = action.get("height", "")
    max_dimension = action.get("max_dimension", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["width"] = width
    kwargs2["height"] = height
    if max_dimension != "":
        kwargs2["max_dimension"] = max_dimension
    robo.robo_corel_set_size(**kwargs2)

def corel_trace(**kwargs):
    print("corel_trace -- tracing")
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    robo.robo_corel_trace(**kwargs2)

##### file commands
def file_copy(**kwargs):
    import shutil
    action = kwargs.get("action", {})
    file_source = action.get("file_source", "")
    file_destination = action.get("file_destination", "")
    directory = kwargs.get("directory", "")
    file_destination = os.path.join(directory, file_destination)
    
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

def ai_set_mode(**kwargs):
    action = kwargs.get("action", {})
    print("ai_set_mode -- setting AI mode")
    mode = action.get("mode", "")
    if mode == "deep_research":
        #press tab twice
        robo.robo_keyboard_press_tab(delay=2, repeat=2)  # Press tab twice to set the mode
        #press_enter
        robo.robo_keyboard_press_enter(delay=2)  # Press enter to confirm the mode
        ##press down 0 #times to select the deep research mode
        #robo.robo_keyboard_press_down(delay=2, repeat=2)  # Press down twice to select the deep research mode
        #press enter
        robo.robo_keyboard_press_enter(delay=2)  # Press enter to confirm the mode
        print("     AI mode set to deep research")

def new_chat(**kwargs):
    action = kwargs.get("action", {})
    description = action.get("description", "")
    log_url = kwargs.get("log_url", True)
    print("new_chat -- opening up a new chat")
    robo.robo_chrome_open_url(url="https://chat.openai.com/chat", delay=15, message="    opening a new chat")    
    #type in start query
    start_query = "Hiya, chadikins the great I have a task for you can you help?" 
    if description != "":
        start_query += f" This chat is about  please chop this up to get a good name for the chat {description} to make it easier to find later."
    robo.robo_keyboard_send(string=start_query, delay=5)
    robo.robo_keyboard_press_enter(delay=20)
    #if log_url is True:
    if log_url:
        #press ctrl l
        robo.robo_keyboard_press_ctrl_generic(string="l", delay=2)
        #copy the url
        url = robo.robo_keyboard_copy(delay=2)
        #print the url
        print(f"    New chat URL: {url}")
        #press esc
        robo.robo_keyboard_press_escape(delay=2, repeat=1)
        #save to url.yaml
        if True:            
            url_file = os.path.join(kwargs.get("directory_absolute", ""), "url.yaml")
            #if url exists load it to add to the list
            if os.path.exists(url_file):
                with open(url_file, 'r') as file:
                    url_data = yaml.safe_load(file)
            else:
                url_data = []
            url_data.append(url)
            with open(url_file, 'w') as file:
                yaml.dump(url_data, file)


def query(**kwargs):
    action = kwargs.get("action", {})
    print("query -- sending a query")
    #get the query from the action
    action = kwargs.get("action", {})
    delay = action.get("delay", 60)
    query_text = action.get("text", "")
    robo.robo_keyboard_send(string=query_text, delay=5)
    print(f"Querying with text: {query_text}")
    robo.robo_keyboard_press_enter(delay=delay)
    
def save_image_generated(**kwargs):
    kwargs["position_click"] = [960, 480]  # Default position for clicking the image    
    robo.robo_delay(delay=300)
    #random extra between 300 and 900 seconds
    
    if True:
        delay = random.randint(300, 900)
        robo.robo_delay(delay=delay)  # Wait for the image to be generated
        #send ctrl rrobo.robo_keyboard_press_ctrl_r(delay=20)
        #click on the image to focus
        robo.robo_keyboard_press_ctrl_generic(string="r", delay=20)
        #click on the image to focus
        robo.robo_mouse_click(position=[330,480], delay=2)  # Click on the white space
        robo.robo_keyboard_press_down(delay=1, repeat=40)  # Press down ten times to select the file input
        save_image(**kwargs)
        file_name = kwargs.get("action", {}).get("file_name", "working.png")
        file_name_absolute = os.path.join(kwargs.get("directory_absolute", ""), file_name)
        if os.path.exists(file_name_absolute):
            print(f"Image saved as {file_name_absolute}")
            saved = True
        else:
            print(f"Image not saved")
            

def save_image_generated_old_try_to_multi_try_doesnt_work(**kwargs):
    kwargs["position_click"] = [960, 400]  # Default position for clicking the image    
    robo.robo_delay(delay=300)
    #random extra between 300 and 900 seconds
    
    saved = False
    y_shift = 0
    attempts = 0
    max_attempts = 4
    while not saved and attempts < max_attempts:
        delay = random.randint(300, 900)
        robo.robo_delay(delay=delay)  # Wait for the image to be generated
        #send ctrl rrobo.robo_keyboard_press_ctrl_r(delay=20)
        #click on the image to focus
        robo.robo_keyboard_press_ctrl_generic(string="r", delay=20)
        #click on the image to focus
        robo.robo_mouse_click(position=[330,480+y_shift], delay=2)  # Click on the white space
        robo.robo_keyboard_press_down(delay=1, repeat=10)  # Press down ten times to select the file input
        save_image(**kwargs)
        file_name = kwargs.get("action", {}).get("file_name", "working.png")
        file_name_absolute = os.path.join(kwargs.get("directory_absolute", ""), file_name)
        if os.path.exists(file_name_absolute):
            print(f"Image saved as {file_name_absolute}")
            saved = True
        else:
            print(f"Image not saved, retrying a little lower")
            y_shift += 100
            attempts += 1


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
    overwrite = action.get("overwrite", True)
    print(f"Saving image as {file_name}")
    if not overwrite and os.path.exists(file_name_absolute):
        print(f"File {file_name_absolute} already exists and overwrite is disabled.")
        return
    else:
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
    files_check = []
    file_name = action.get("file_name", "")
    if file_name != "":
        files_check.append(file_name)
    for i in range(1, 7):
        file_name = action.get(f"file_name_{i}", "")
        if file_name != "":
            files_check.append(file_name)

    directory_absolute = kwargs.get("directory_absolute", "")
    
    return_value = ""
    for file_name in files_check:
        if file_name != "":
            file_name = file_name.strip()  # Remove any leading/trailing whitespace
            if not os.path.isabs(file_name):
                file_name = os.path.join(directory_absolute, file_name)  # Make it absolute
            if os.path.exists(file_name):
                pass
                #print(f"File {file_name} exists.")                
            else:
                return_value = "exit_no_tab"
                break
                #print(f"File {file_name} does not exist.")
    
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