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
    filt_all = kwargs.get("filter_all", None)
    filt_or = kwargs.get("filter_or", None)
    
    #if filter isn't "" and filt_all or filt_or have something make an errror about too many filters
    if filt != "" and (filt_all is not None or filt_or is not None):
        print("Error: Too many filters specified. Please use only one of 'filter', 'filter_all', or 'filter_or'.")
        return
    
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
            run = False
            if filt_all is not None and filt_all != []:
                #check if all filt_all are in dir
                run = all(f in dir for f in filt_all)
            elif filt_or is not None and filt_or != []:
                #check if any filt_or are in dir
                run = any(f in dir for f in filt_or)
            else:
                run = filt in dir or filt == "" 
            #if filt == "" or filt in dir:
            if run:
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
                        for i in range(1, 10):
                            mode = f"oomlout_ai_roboclick_{i}"
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
        print(f"file test mode {file_test_mode} on {file_test_absolute}")
        if file_test_mode == "exists":
            if os.path.exists(file_test_absolute):
                print(f"File test {file_test_absolute} exists, skipping actions.")
                return
        elif len(file_test_absolute) > 20:
            length = len(file_test_mode)
            print(f"File test is {length} lone to {file_test_mode} is too long, skipping actions.")
            return
        else:
            if not os.path.exists(file_test_absolute):
                print(f"File test {file_test_absolute} does not exist, skipping actions.")
                return

    result = ""
    
    kwargs = copy.deepcopy(kwargs)
    kwargs["actions"] = actions 


    for action in actions:
        kwargs["action"] = action
        result = run_action(**kwargs)
        if result == "exit" or result == "exit_no_tab":
            print("Exiting due to 'exit' command.")
            break

    
    
def run_action(**kwargs):    
    result = ""
    action = kwargs.get("action", {})
    command = action.get("command")
    
    if command == "add_image":
        result = add_image(**kwargs)
    #ai ones
    #ai save_text
    elif command == "ai_save_text":
        ai_save_text(**kwargs)
    #ai_mode
    elif command == "ai_set_mode":
        ai_set_mode(**kwargs)
    elif command == "close_tab":
        result = close_tab(**kwargs)
    #corel commands
    #corel_close
    #corel add text
    elif command == "corel_add_text":
        corel_add_text(**kwargs)
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
    elif command == "corel_object_order":
        corel_object_order(**kwargs)
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
    elif command == "corel_trace_full":
        corel_trace_full(**kwargs)
    ###### file commands
    elif command == "file_copy":
        result = file_copy(**kwargs)
    #image commands
    #image_upscale
    elif command == "image_upscale":
        image_upscale(**kwargs)
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
    
    #if result is "exit_no_tab", dont close the tab
    return result
#actions


def add_image(**kwargs):
    return_value = ""
    print("add_image -- adding an image")
    #kwargs["position_click"] = [750,995]

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
    #tab once
    robo.robo_keyboard_press_tab(delay=2, repeat=1)  # Press tab once to focus on the add image button
    #down zero times
    #robo.robo_keyboard_press_down(delay=1, repeat=1)  # Press down zero times to select the file input
    #enter once
    robo.robo_keyboard_press_enter(delay=5)  # Press enter to open the file dialog
    #robo.robo_keyboard_press_down(delay=1, repeat=2)  # Press down twice to select the file input
    robo.robo_keyboard_send(string=file_name_absolute, delay=5)  # Type the file name
    robo.robo_keyboard_press_enter(delay=5)  # Press enter to confirm
    robo.robo_delay(delay=15)  # Wait for the image to be added
    #preess escape 5 times in case of any dialog boxes
    robo.robo_keyboard_press_escape(delay=5, repeat=5)  # Escape to close any dialogs
    return return_value

def add_image_old_1(**kwargs):
    return_value = ""
    print("add_image -- adding an image")
    #kwargs["position_click"] = [750,995]

    position_click = kwargs.get("position_click", [738, 982])
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
    #robo.robo_keyboard_press_down(delay=1, repeat=2)  # Press down twice to select the file input
    robo.robo_keyboard_press_down(delay=1, repeat=1)  # Press down twice to select the file input
    robo.robo_keyboard_press_enter(delay=5)
    robo.robo_keyboard_send(string=file_name_absolute, delay=5)  # Type the file name
    robo.robo_keyboard_press_enter(delay=5)  # Press enter to confirm
    robo.robo_delay(delay=15)  # Wait for the image to be added
    #preess escape 5 times in case of any dialog boxes
    robo.robo_keyboard_press_escape(delay=5, repeat=5)  # Escape to close any dialogs
    return return_value


def ai_save_text(**kwargs):
    action = kwargs.get("action", {})
    file_name_full = action.get("file_name_full", "text.txt")
    file_name_clip = action.get("file_name_clip", "clip.txt")
    clip = action.get("clip", " ")
    directory = kwargs.get("directory", "")

    robo.robo_mouse_click(position=[300, 300], delay=2, button="left")  # Click to focus
    text = robo.robo_keyboard_copy(delay=2)  # Copy the selected text
    if file_name_full != "":
        file_name_full_full = os.path.join(directory, file_name_full)
        with open(file_name_full_full, 'w', encoding='utf-8') as f:
            f.write(text)
            print(f"Text saved to {file_name_full_full}")
    if file_name_clip != "":
        file_name_clip_full = os.path.join(directory, file_name_clip)
        with open(file_name_clip_full, 'w', encoding='utf-8') as f:
            #text between two clip tages
            clipping = text.split(clip)
            if len(clipping) > 1:
                clipping = clipping[len(clipping)-2]
            else:
                clipping = text
            f.write(clipping)
            print(f"Clip text saved to {file_name_clip_full}")

def close_tab(**kwargs):
    print("close_tab -- closing the current tab")
    #close the current tab
    robo.robo_chrome_close_tab(**kwargs)
    #wait for 5 seconds
    robo.robo_delay(delay=5)  # Wait for the tab to close

##### corel commands

def corel_add_text(**kwargs):
    print("corel_add_text -- adding text in corel")
    action = kwargs.get("action", {})
    text = action.get("text", "Hello World")
    x = action.get("x", 100)
    y = action.get("y", 100)
    font = action.get("font", "Arial")
    font_size = action.get("font_size", 12)
    bold = action.get("bold", False)
    italic = action.get("italic", False)
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["text"] = text
    kwargs2["x"] = x
    kwargs2["y"] = y
    kwargs2["font"] = font
    kwargs2["font_size"] = font_size
    kwargs2["bold"] = bold
    kwargs2["italic"] = italic
    robo.robo_corel_add_text(**kwargs2)
    #wait for 2 seconds
    robo.robo_delay(delay=2)  # Wait for the text to be added

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

def corel_object_order(**kwargs):
    print("corel_object_order -- changing object order in corel")
    action = kwargs.get("action", {})
    order = action.get("order", "to_front")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["order"] = order
    robo.robo_corel_object_order(**kwargs2)

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

def corel_trace_full(**kwargs):
    action = kwargs.get("action", {})
    file_source = action.get("file_source", "")
    file_source_just_file_and_extension = os.path.basename(file_source)
    file_source_trace = action.get("file_source_trace", "")
    file_source_trace_just_file_and_extension = os.path.basename(file_source_trace)
    file_source_trace_just_file_and_extension_upscaled = file_source_trace_just_file_and_extension.replace(".png", "_upscaled.png").replace(".jpg", "_upscaled.jpg").replace(".jpeg", "_upscaled.jpeg")
    file_destination = action.get("file_destination", "")
    file_destination_just_file_and_extension = os.path.basename(file_destination)
    file_destination_just_file_and_extension_pdf = file_destination_just_file_and_extension.replace(".cdr", ".pdf").replace(".png", ".pdf").replace(".jpg", ".pdf").replace(".jpeg", ".pdf")
    file_destination_just_file_and_extension_png = file_destination_just_file_and_extension.replace(".cdr", ".png").replace(".pdf", ".png").replace(".jpg", ".png").replace(".jpeg", ".png")
    
    max_dimension = action.get("max_dimension", 100)
    xx = action.get("x", 100)
    yy = action.get("y", 100)

    actions = []

    #file_copy
    action = {} 
    action["command"] = "file_copy"
    action["file_source"] = f"{file_source}"
    action["file_destination"] = f"{file_destination_just_file_and_extension}"
    actions.append(copy.deepcopy(action))

    #corel_open
    action = {}
    action["command"] = "corel_open"
    action["file_name"] = f"{file_destination_just_file_and_extension}"
    actions.append(copy.deepcopy(action))

    #image_upscale
    action = {}
    action["command"] = "image_upscale"
    action["file_input"] = f"{file_source_trace_just_file_and_extension}"
    action["scale"] = 4
    actions.append(copy.deepcopy(action))

    #corel_import
    action = {}
    action["command"] = "corel_import"
    action["x"] = xx
    action["y"] = yy
    action["width"] = max_dimension
    action["file_name"] = f"{file_source_trace_just_file_and_extension_upscaled}"
    actions.append(copy.deepcopy(action))

    #corel_save
    action = {}
    action["command"] = "corel_save"
    actions.append(copy.deepcopy(action))

    #corel_save_as
    action = {}
    action["command"] = "corel_save_as"
    action["file_name"] = f"{file_destination_just_file_and_extension}"
    actions.append(copy.deepcopy(action))

    #trace_clipart
    action = {}
    action["command"] = "corel_trace"
    actions.append(copy.deepcopy(action))

    #corel_set_size
    action = {}
    action["command"] = "corel_set_size"
    action["max_dimension"] = {max_dimension}
    actions.append(copy.deepcopy(action))

    #corel_set_position
    action = {}
    action["command"] = "corel_set_position"
    action["x"] = xx
    action["y"] = yy
    actions.append(copy.deepcopy(action))

    #corel_save
    action = {}
    action["command"] = "corel_save"
    actions.append(copy.deepcopy(action))

    #export as pdf
    action = {}
    action["command"] = "corel_export"                
    action["file_name"] = f"{file_destination_just_file_and_extension_pdf}"
    action["file_type"] = "pdf"
    actions.append(copy.deepcopy(action))

    #export png
    action = {}
    action["command"] = "corel_export"
    action["file_name"] = f"{file_destination_just_file_and_extension_png}"
    action["file_type"] = "png"
    actions.append(copy.deepcopy(action))

    #corel close
    action = {}
    action["command"] = "corel_close_file"
    actions.append(copy.deepcopy(action))

    for action in actions:
        kwargs["action"] = action
        run_action(**kwargs)

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
    if mode == "deep_research" or mode == "deep_research_off":
        #press tab twice
        robo.robo_keyboard_press_tab(delay=2, repeat=1)  # Press tab twice to set the mode        
        #press_enter
        robo.robo_keyboard_press_enter(delay=2)  # Press enter to confirm the mode
        #press down once
        robo.robo_keyboard_press_down(delay=2, repeat=1)
        ##press down 0 #times to select the deep research mode
        #robo.robo_keyboard_press_down(delay=2, repeat=2)  # Press down twice to select the deep research mode
        #press enter
        robo.robo_keyboard_press_enter(delay=2)  # Press enter to confirm the mode
        print("     AI mode set to deep research")

#image commands
def image_upscale(**kwargs):
    action = kwargs.get("action", {})
    directory = kwargs.get("directory", "")
    file_input = action.get("file_input", "")
    file_input = os.path.join(directory, file_input)
    file_input_full = os.path.abspath(file_input)
    #png or jpeg or jpg
    file_output_default = file_input.replace(".png", "_upscaled.png").replace(".jpg", "_upscaled.jpg").replace(".jpeg", "_upscaled.jpeg")
    file_output = action.get("file_output", file_output_default)
    if directory not in file_output:
        file_output = os.path.join(directory, file_output)
    upscale_factor = action.get("upscale_factor", 2)
    #if file_input is a file
    if os.path.isfile(file_input):
        #use pil; LANCZOS to upscale the image
        from PIL import Image
        try:
            #if outpurt file exists, delete
            if os.path.exists(file_output):
                os.remove(file_output)
                print(f"Removed existing output file {file_output}")
            with Image.open(file_input_full) as img:
                # Calculate new size
                new_size = (int(img.width * upscale_factor), int(img.height * upscale_factor))
                # Resize the image
                #img = img.resize(new_size, Image.LANCZOS)
                #use nearest
                img = img.resize(new_size, Image.NEAREST)
                # Save the upscaled image
                img.save(file_output)
                print(f"Image upscaled and saved to {file_output}")
        except Exception as e:
            print(f"Error upscaling image {file_input_full}: {e}")
            return
    else:
        print(f"file_input {file_input} does not exist, skipping image upscale")
        return

def new_chat(**kwargs):
    action = kwargs.get("action", {})
    description = action.get("description", "")
    log_url = kwargs.get("log_url", True)
    print("new_chat -- opening up a new chat")
    robo.robo_chrome_open_url(url="https://chat.openai.com/chat", delay=15, message="    opening a new chat")    
    #type in start query
    start_query = ""
    if description != "":        
        start_query += f" Hi, CHadikins I hope your day is going well! lets get to this!."
    start_query += " Chadikins the best let do this!"
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
        robo.robo_keyboard_press_escape(delay=2, repeat=5)
        #save to url.yaml
        if True:            
            url_file = os.path.join(kwargs.get("directory_absolute", ""), "url.yaml")
            #if url exists load it to add to the list
            if os.path.exists(url_file):
                with open(url_file, 'r') as file:
                    url_data = yaml.safe_load(file)
            else:
                url_data = []
            if url_data == None:
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
    #split with _ if it exists
    if "_" in index:
        index = index.split("_")[0]
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
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    print(f"wait_for_file -- skip if a necessary file doesnt exist {file_name}")
    
    files_check = []
    
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
                print(f"file exists.")                
            else:
                return_value = "exit_no_tab"
                print(f"file does not exist.")
                break
                

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