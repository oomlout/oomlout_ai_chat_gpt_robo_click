import random
import argparse
from statistics import mode
import yaml
import robo
import copy
import sys
import os
import pyautogui
import inspect

# Action registry - automatically populated by decorators or manual registration
ACTION_REGISTRY = {}

# Import manual action registration
try:
    from action_registry_manual import ACTIONS_METADATA
    MANUAL_REGISTRY_AVAILABLE = True
except ImportError:
    MANUAL_REGISTRY_AVAILABLE = False
    print("Warning: action_registry_manual.py not found, using fallback registration")

def action(command_name, variables=None):
    """
    Decorator to register an action function and document it.
    
    Usage:
        @action("command_name", ["var1", "var2"])
        def my_action(**kwargs):
            '''Description of what this action does'''
            # implementation
    """
    def decorator(func):
        # Get description from docstring
        description = func.__doc__.strip() if func.__doc__ else "No description"
        
        # Auto-detect category based on command name
        if command_name.startswith("ai_") or command_name in ["add_file", "add_image", "save_image_generated"]:
            category = "AI"
        elif command_name.startswith("browser_"):
            category = "Browser"
        elif command_name.startswith("corel_"):
            category = "Corel"
        elif command_name.startswith("image_"):
            category = "Image"
        elif command_name.startswith("file_") or command_name == "convert_svg_to_pdf":
            category = "File"
        elif "chat" in command_name or command_name in ["query", "save_image_search_result"]:
            category = "Chat"
        elif command_name.startswith("google_"):
            category = "Google Doc"
        elif command_name.startswith("openscad_"):
            category = "OpenSCAD"
        else:
            category = "Other"
        
        # Register the action
        ACTION_REGISTRY[command_name] = {
            'function': func,
            'description': description,
            'variables': variables or [],
            'category': category
        }
        return func
    return decorator

def get_all_actions_documentation():
    """
    Returns documentation for all registered actions.
    """
    actions = []
    for command, info in sorted(ACTION_REGISTRY.items()):
        actions.append({
            'command': command,
            'description': info['description'],
            'variables': info['variables'],
            'category': info.get('category', 'Other')
        })
    return actions

def register_all_actions_from_manual():
    """
    Register all actions using the manual metadata and finding functions in globals.
    This should be called after all action functions are defined.
    """
    if not MANUAL_REGISTRY_AVAILABLE:
        print("Manual registry not available")
        return 0
    
    registered_count = 0
    for command_name, metadata in ACTIONS_METADATA.items():
        # Look for the function in globals
        if command_name in globals():
            func = globals()[command_name]
            ACTION_REGISTRY[command_name] = {
                'function': func,
                'description': metadata['description'],
                'variables': metadata['variables']
            }
            registered_count += 1
    
    print(f"Registered {registered_count} actions from manual registry")
    return registered_count

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

    for i in range(len(mode_local)):
        m = mode_local[i]   
        if m == "all" or m == "" :
            mode_local[i] = "oomlout_ai_roboclick"
            mode_local.append("oomlout_corel_roboclick")
        elif m == "ai":
            mode_local[i] = ["oomlout_ai_roboclick"]
        elif m == "corel":
            mode_local[i] = ["oomlout_corel_roboclick"]
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
                    #load workings into kwargs
                    kwargs["workings"] = {}
                    try:
                        with open(file_action, 'r') as file:
                            kwargs["workings"] = yaml.safe_load(file)
                            print(f"Workings loaded from {file_action}: {len(kwargs['workings'])} items found")
                    except FileNotFoundError:
                        print(f"Workings file {file_action} not found.")
                    except yaml.YAMLError as e:
                        print(f"Error parsing YAML file {file_action}: {e}")
                    except Exception as e:
                        print(f"Error loading workings from {file_action}: {e}")

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
        #load_workings from file
        if False:
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
        if True:
            workings = kwargs.get("workings", {})


        base = workings.get(mode, [])
        if base != []:
            actions = base.get("actions", {})
        else:
            #print(f"No actions found for mode {mode} in {file_action}")
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
        #if result is a dict
        elif isinstance(result, dict):
            print ("Updating workings with result dict")
            for key, value in result.items():
                workings[key] = value
                print(f"    Updated workings key: {key} with value: {value}")
            #write kwargs to file_action
            try:
                with open(file_action, 'w') as file:
                    yaml.dump(workings, file)
                    print(f"Updated workings saved to {file_action}")
            except Exception as e:
                print(f"Error saving workings to {file_action}: {e}")
                import time
                time.sleep(5)
            
    
    
def run_action(**kwargs):    
    """
    Execute an action based on the command in kwargs.
    Now uses the ACTION_REGISTRY for automatic dispatch.
    """
    result = ""
    action = kwargs.get("action", {})
    command = action.get("command")
    
    # Use the registry to find and execute the action
    if command in ACTION_REGISTRY:
        action_info = ACTION_REGISTRY[command]
        result = action_info['function'](**kwargs)
    else:
        print(f"Warning: Unknown command '{command}'")
    
    return result

#==============================================================================
# ACTION FUNCTIONS







###ai ones
@action("ai_add_image", ["file_name", "position_click"])
def ai_add_image(**kwargs):
    """Add a file (alias for add_image)"""
    """Add an image file to the current context"""
    return_value = ""
    print("add_image -- adding an image")
    #kwargs["position_click"] = [750,995]

    action = kwargs.get("action", {})
    file_name = action.get("file_name", "working.png")
    directory_absolute = kwargs.get("directory_absolute", "")
    file_name_absolute = os.path.join(directory_absolute, file_name)
    file_name_abs = os.path.abspath(file_name) 
    #print(f"Adding image {file_name} at position {position_click}")
    #test if filename exists
    if not os.path.exists(file_name_absolute):
        print(f"File {file_name_absolute} does not exist, skipping action.")
        return_value = "exit"
        return return_value
    #send "  "
    robo.robo_keyboard_send(string="  ", delay=2)  # Send two spaces to open the add image dialog
    #tab once
    robo.robo_keyboard_press_tab(delay=5, repeat=1)  # Press tab once to focus on the add image button
    #down zero times
    #robo.robo_keyboard_press_down(delay=1, repeat=1)  # Press down zero times to select the file input
    #enter once
    robo.robo_keyboard_press_enter(delay=5)  # Press enter to open the file dialog
    #new needs two enters maybe
    if True:
        robo.robo_keyboard_press_enter(delay=5)  # Press enter to open the file dialog
    #robo.robo_keyboard_press_down(delay=1, repeat=2)  # Press down twice to select the file input
    robo.robo_keyboard_send(string=file_name_absolute, delay=5)  # Type the file name
    robo.robo_keyboard_press_enter(delay=5)  # Press enter to confirm
    robo.robo_delay(delay=15)  # Wait for the image to be added
    #preess escape 5 times in case of any dialog boxes
    robo.robo_keyboard_press_escape(delay=5, repeat=5)  # Escape to close any dialogs
    return return_value


@action("ai_add_file", ["file_name"])
def ai_add_file(**kwargs):
    """Add a file (alias for add_image)"""
    return ai_add_image(**kwargs)    


@action("ai_fix_yaml_copy_paste", ["file_input", "file_output", "remove_top_level", "new_item_name", "search_and_replace"])
def ai_fix_yaml_copy_paste(**kwargs):
    """Fix YAML formatting from copy-pasted content"""
    action = kwargs.get("action", {})
    file_input = action.get("file_input", "working.yaml")
    file_output = action.get("file_output", "working_fixed.yaml")
    directory = kwargs.get("directory", "")
    remove_top_level = action.get("remove_top_level", [])
    new_item_name = action.get("new_item_name", "")
    search_and_replace = action.get("search_and_replace", [])
    #load input file
    with open(os.path.join(directory, file_input), 'r', encoding='utf-8') as f:
        text = f.read()
    #replace all double line breaks with singles
    if True:
        text = text.replace("\n\n", "\n")
    #remvoe_top_level
    if True:
        #if remove_top_level is a string make it an array
        if isinstance(remove_top_level, str):
            remove_top_level = [remove_top_level]
        for tag in remove_top_level:
            lines = text.split("\n")
            new_lines = []
            skip = False
            for line in lines:
                if line.strip().startswith(f"{tag}:"):
                    skip = True
                    continue
                if skip:
                    if line.startswith(" "):
                        continue
                    else:
                        skip = False
                new_lines.append(line)
            text = "\n".join(new_lines)
    #new_item_name
    if True:
        #if the line starts new_item name : then add "- "
        #if it has text add two spaces
        if new_item_name != "":
            lines = text.split("\n")
            new_lines = []
            for line in lines:
                if line.strip().startswith(f"{new_item_name}:"):
                    new_lines.append(f"- {line}")
                    continue
                else:
                    new_lines.append(f"  {line}")
            text = "\n".join(new_lines)
    #remove any lines that are all whitespace
    if True:
        lines = text.split("\n")
        new_lines = []
        for line in lines:
            if line.strip() == "":
                continue
            new_lines.append(line)
        text = "\n".join(new_lines)
    #search_and_replace
    if search_and_replace != []:
        for item in search_and_replace:
            search = item[0]
            replace = item[1]
            if search != "":
                text = text.replace(search, replace)
    
    
    #save output file
    with open(os.path.join(directory, file_output), 'w', encoding='utf-8') as f:
        f.write(text)
    pass


@action("ai_save_text", ["file_name_full", "file_name_clip", "clip"])
def ai_save_text(**kwargs):
    """Save text content from AI"""
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


@action("ai_set_mode", ["mode"])
def ai_set_mode(**kwargs):
    """Set AI mode (e.g., deep_research)"""
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


# browser

@action("browser_close_tab", [])
def browser_close_tab(**kwargs):
    """Close the current browser tab"""
    print("browser_close_tab -- closing the current tab")
    #close the current tab
    robo.robo_chrome_close_tab(**kwargs)
    #wait for 5 seconds
    robo.robo_delay(delay=5)  # Wait for the tab to close

@action("browser_open_url", ["url"])
def browser_open_url(**kwargs):
    """Open a URL in the browser"""
    action = kwargs.get("action", {})
    url = action.get("url", "")
    print(f"browser_open_url -- opening URL: {url}")
    robo.robo_chrome_open_url(url=url, delay=15, message="    opening URL in browser")

@action("browser_save_url", ["url", "url_directory"])
def browser_save_url(**kwargs):
    """Save the current URL in the browser"""
    action = kwargs.get("action", {})
    url = action.get("url", "")
    url_directory = action.get("url_directory", "web_page")
    print(f"browser_save_url -- saving URL: {url} to directory: {url_directory}")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["url"] = url
    kwargs2["url_directory"] = url_directory
    kwargs2["delay"] = 15
    robo.robo_chrome_save_url(**kwargs2)

##### convert commands

@action("continue_chat", ["url_chat", "log_url"])
def continue_chat(**kwargs):
    """Continue existing chat session"""
    action = kwargs.get("action", {})    
    log_url = kwargs.get("log_url", True)
    url_chat = action.get("url_chat", "")
    print("continue_chat -- continuing an existing chat")
    robo.robo_chrome_open_url(url=url_chat, delay=15, message="    opening a new chat")    
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
            return url


@action("convert_svg_to_pdf", ["file_input", "file_output"])
def convert_svg_to_pdf(**kwargs):
    """Convert SVG file to PDF format"""
    directory = kwargs.get("directory", "")
    action = kwargs.get("action", {})
    file_input = action.get("file_input", "")
    kwargs["file_input"] = f"{directory}\\{file_input}"
    file_output = action.get("file_output", "")
    if file_output == "":
        file_output = file_input.replace(".svg", ".pdf")
    kwargs["file_output"] = f"{directory}\\{file_output}"
    robo.robo_convert_svg_to_pdf(**kwargs)

##### corel commands


@action("corel_add_text", ["text", "x", "y", "font", "font_size", "bold", "italic"])
def corel_add_text(**kwargs):
    """Add text in CorelDRAW"""
    print("corel_add_text -- adding text in corel")
    action = kwargs.get("action", {})
    text = action.get("text", "Hello World")
    x = action.get("x", 100)
    y = action.get("y", 100)
    font = action.get("font", "")
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


@action("corel_add_text_box", ["text", "x", "y", "width", "height", "font", "font_size", "bold", "italic"])
def corel_add_text_box(**kwargs):
    """Add text box in CorelDRAW"""
    print("corel_add_text -- adding text in corel")
    action = kwargs.get("action", {})
    text = action.get("text", "Hello World")
    x = action.get("x", 100)
    y = action.get("y", 100)
    width = action.get("width", 200)
    height = action.get("height", 100)
    font = action.get("font", "")
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
    kwargs2["width"] = width
    kwargs2["height"] = height
    robo.robo_corel_add_text_box(**kwargs2)
    #wait for 2 seconds
    robo.robo_delay(delay=2)  # Wait for the text to be added


@action("corel_close_file", [])
def corel_close_file(**kwargs):
    """Close current file in CorelDRAW"""
    print("corel_close_file -- closing corel")
    #close corel
    robo.robo_corel_close_file(**kwargs)


@action("corel_convert_to_curves", ["ungroup", "delay"])
def corel_convert_to_curves(**kwargs):
    """Convert selected items to curves in CorelDRAW"""
    print("corel_convert_to_curves -- converting selected items to curves in corel")
    
    action = kwargs.get("action", {})
    ungroup = action.get("ungroup", False)
    delay_convert = action.get("delay", 5)
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["delay"] = delay_convert
    if ungroup:
        kwargs2["ungroup"] = ungroup
    robo.robo_corel_convert_to_curves(**kwargs2)


@action("corel_copy", [])
def corel_copy(**kwargs):
    """Copy selected items in CorelDRAW"""
    print("corel_copy -- copying selected items in corel")
    #copy selected items in corel
    robo.robo_corel_copy(**kwargs)



@action("corel_export", ["file_name", "file_destination", "file_type", "delay"])
def corel_export(**kwargs):
    """Export file from CorelDRAW"""
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    delay_export = action.get("delay", 10)
    action.pop("delay", None)   
    if file_name == "":
        file_name = action.get("file_destination", "")
    file_type = action.get("file_type", "pdf")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    kwargs2["file_type"] = file_type
    kwargs2["delay"] = delay_export
    robo.robo_corel_export_file(**kwargs2)


@action("corel_group", [])
def corel_group(**kwargs):
    """Group selected items in CorelDRAW"""
    print("corel_group -- grouping selected items in corel")
    #group selected items in corel
    robo.robo_corel_group(**kwargs)


@action("corel_import", ["file_name", "file_source", "x", "y", "width", "height", "max_dimension", "angle", "special"])
def corel_import(**kwargs):
    """Import file into CorelDRAW"""
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    if file_name == "":
        file_name = action.get("file_source", "")
    x = action.get("x", "")
    y = action.get("y", "")
    width = action.get("width", "")
    height = action.get("height", "")
    max_dimension = action.get("max_dimension", "")
    angle = action.get("angle", 0)
    special = action.get("special", "")
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
    if angle != 0:
        kwargs2["angle"] = angle
    if special != "":
        kwargs2["special"] = special

    robo.robo_corel_import_file(**kwargs2)


@action("corel_object_order", ["order"])
def corel_object_order(**kwargs):
    """Change object stacking order in CorelDRAW"""
    print("corel_object_order -- changing object order in corel")
    action = kwargs.get("action", {})
    order = action.get("order", "to_front")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["order"] = order
    robo.robo_corel_object_order(**kwargs2)


@action("corel_open", ["file_name", "file_source"])
def corel_open(**kwargs):
    """Open file in CorelDRAW"""
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    #if file_name is "" try file_source
    if file_name == "":
        file_name = action.get("file_source", "")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    robo.robo_corel_open(**kwargs2)


@action("corel_page_goto", ["page_number"])
def corel_page_goto(**kwargs):
    """Navigate to specific page in CorelDRAW"""
    print("corel_page_goto -- going to page in corel")
    action = kwargs.get("action", {})
    page_number = action.get("page_number", 1)
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["page_number"] = page_number
    robo.robo_corel_page_goto(**kwargs2)


@action("corel_paste", ["x", "y", "width", "height"])
def corel_paste(**kwargs):
    """Paste copied items in CorelDRAW"""
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


@action("corel_save", ["file_name"])
def corel_save(**kwargs):
    """Save current file in CorelDRAW"""
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    robo.robo_corel_save(**kwargs2)


@action("corel_save_as", ["file_name", "file_destination"])
def corel_save_as(**kwargs):
    """Save file with new name in CorelDRAW"""
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "")
    if file_name == "":
        file_name = action.get("file_destination", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_name"] = file_name
    robo.robo_corel_save_as(**kwargs2)


@action("corel_set_position", ["x", "y"])
def corel_set_position(**kwargs):
    """Set position of selected items in CorelDRAW"""
    print("corel_set_position -- setting position")
    action = kwargs.get("action", {})
    x = action.get("x", "")
    y = action.get("y", "")
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["x"] = x
    kwargs2["y"] = y
    robo.robo_corel_set_position(**kwargs2)

#corel set rotation

@action("corel_set_rotation", ["angle"])
def corel_set_rotation(**kwargs):
    """Set rotation angle of selected items in CorelDRAW"""
    print("corel_set_rotation -- setting rotation")
    action = kwargs.get("action", {})
    angle = action.get("angle", 0)
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["angle"] = angle
    robo.robo_corel_set_rotation(**kwargs2)


@action("corel_set_size", ["width", "height", "max_dimension", "select_all"])
def corel_set_size(**kwargs):
    """Set size of selected items in CorelDRAW"""
    print("corel_set_size -- setting size")
    action = kwargs.get("action", {})
    width = action.get("width", "")
    height = action.get("height", "")
    max_dimension = action.get("max_dimension", "")
    select_all = action.get("select_all", False)
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["width"] = width
    kwargs2["height"] = height
    kwargs2["select_all"] = select_all
    if max_dimension != "":
        kwargs2["max_dimension"] = max_dimension
    robo.robo_corel_set_size(**kwargs2)


@action("corel_trace", ["file_name", "remove_background_color_from_entire_image", "delay_trace", "number_of_colors", "detail_minus", "smoothing", "corner_smoothness"])
def corel_trace(**kwargs):
    """Trace bitmap image in CorelDRAW"""
    print("corel_trace -- tracing")
    action = kwargs.get("action", {})
    kwargs2 = copy.deepcopy(kwargs)    
    file_name = action.get("file_name", "")
    kwargs2["file_name"] = file_name
    remove_background_color_from_entire_image = action.get("remove_background_color_from_entire_image", False)
    kwargs2["remove_background_color_from_entire_image"] = remove_background_color_from_entire_image    
    
    delay_trace = action.get("delay_trace", None)
    number_of_colors = action.get("number_of_colors", None)
    if number_of_colors is not None:
        kwargs2["number_of_colors"] = number_of_colors
    detail_minus = action.get("detail_minus", None)
    if detail_minus is not None:
        kwargs2["detail_minus"] = detail_minus
    smoothing = action.get("smoothing", None)
    if smoothing is not None:
        kwargs2["smoothing"] = smoothing
    corner_smoothness = action.get("corner_smoothness", None)
    if corner_smoothness is not None:
        kwargs2["corner_smoothness"] = corner_smoothness
    
    
    delay_trace = action.get("delay_trace", 30)
    kwargs2["delay_trace"] = delay_trace

    robo.robo_corel_trace(**kwargs2)
    pass
            

##### file commands

@action("corel_trace_full", ["file_source", "file_source_trace", "file_destination", "delay_trace", "delay_png", "max_dimension", "detail_minus", "x", "y", "number_of_colors", "remove_background_color_from_entire_image", "smoothing", "corner_smoothness"])
def corel_trace_full(**kwargs):
    """Complete trace workflow in CorelDRAW"""
    action = kwargs.get("action", {})
    action_main = copy.deepcopy(action)
    file_source = action.get("file_source", "")
    file_source_just_file_and_extension = os.path.basename(file_source)
    file_source_trace = action.get("file_source_trace", "")
    file_source_trace_just_file_and_extension = os.path.basename(file_source_trace)
    file_source_trace_just_file_and_extension_upscaled = file_source_trace_just_file_and_extension.replace(".png", "_upscaled.png").replace(".jpg", "_upscaled.jpg").replace(".jpeg", "_upscaled.jpeg")
    file_destination = action.get("file_destination", "")
    file_destination_just_file_and_extension = os.path.basename(file_destination)
    file_destination_just_file_and_extension_pdf = file_destination_just_file_and_extension.replace(".cdr", ".pdf").replace(".png", ".pdf").replace(".jpg", ".pdf").replace(".jpeg", ".pdf")
    file_destination_just_file_and_extension_png = file_destination_just_file_and_extension.replace(".cdr", ".png").replace(".pdf", ".png").replace(".jpg", ".png").replace(".jpeg", ".png")
    delay_trace = action.get("delay_trace", 30)
    delay_png = action.get("delay_png", 10)
    max_dimension = action.get("max_dimension", 100)
    detail_minus = action.get("detail_minus", 0)
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
    if "number_of_colors" in action_main:
        action["number_of_colors"] = action_main["number_of_colors"]
    if "remove_background_color_from_entire_image" in action_main:
        action["remove_background_color_from_entire_image"] = action_main["remove_background_color_from_entire_image"]
    if detail_minus != 0:
        action["detail_minus"] = detail_minus
    if "delay_trace" in action_main:
        action["delay_trace"] = delay_trace
    if "smoothing" in action_main:
        action["smoothing"] = action_main["smoothing"]
    if "corner_smoothness" in action_main:
        action["corner_smoothness"] = action_main["corner_smoothness"]
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
    action["delay"] = delay_png
    actions.append(copy.deepcopy(action))

    #export png
    action = {}
    action["command"] = "corel_export"
    action["file_name"] = f"{file_destination_just_file_and_extension_png}"
    action["file_type"] = "png"
    action["delay"] = delay_png
    actions.append(copy.deepcopy(action))

    #corel close
    action = {}
    action["command"] = "corel_close_file"
    actions.append(copy.deepcopy(action))

    for action in actions:
        kwargs["action"] = action
        run_action(**kwargs)

## file commands

@action("file_copy", ["file_source", "file_destination"])
def file_copy(**kwargs):
    """Copy file from source to destination"""
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

@action("file_create_text_file", ["file_name", "content"])
def file_create_text_file(**kwargs):
    directory = kwargs.get("directory", "")
    action = kwargs.get("action", {})
    file_name = action.get("file_name", "textfile.txt")    
    file_name_full = os.path.join(directory, file_name)
    content = action.get("content", "")
    delay = action.get("delay", 1)
    """Create a text file with specified content"""
    try:
        with open(file_name_full, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Text file created at {file_name_full}")
    except Exception as e:
        print(f"Error creating text file at {file_name_full }: {e}")
    robo.robo_delay(delay=delay)  # Wait for the file to be created
##google commands

@action("google_doc_new", ["template", "title", "folder"])
def google_doc_new(**kwargs):
    """Create a new Google Doc and return its URL"""
    action = kwargs.get("action", {})
    template = action.get("template", "")
    title = action.get("title", "")
    folder = action.get("folder", "")
    print("google_doc_new -- creating a new Google Doc")
    
    kwargs2 = copy.deepcopy(kwargs)
    if template != "":
        kwargs2["template"] = template
    if title != "":
        kwargs2["title"] = title
    if folder != "":
        kwargs2["folder"] = folder
    
    result = robo.robo_google_doc_new(**kwargs2)
    
    return result


@action("image_crop", ["file_input", "file_output", "crop"])
def image_crop(**kwargs):
    """Crop image to specified format"""
    action = kwargs.get("action", {})
    directory = kwargs.get("directory", "")
    file_input = action.get("file_input", "")
    file_input = os.path.join(directory, file_input)
    file_input_full = os.path.abspath(file_input)
    file_output_default = file_input_full
    file_output = action.get("file_output", file_output_default)
    if directory not in file_output:
        file_output = os.path.join(directory, file_output)
    crop = action.get("crop", "a4_portrait")  #left, upper, right, lower
    #if file_input is a file
    print(f"Cropping image {file_input} to {crop} and saving to {file_output}")
    if os.path.isfile(file_input):
        #use pil to crop the image
        from PIL import Image
        try:
            with Image.open(file_input_full) as img:
                # Crop the image
                crop_box = [0,0,100,100]
                if crop == "a4_landscape":
                    img_width, img_height = img.size
                    aspect_ratio = 297 / 210  
                    # create_coordinates to take from the middle of the image check if source is wider or taller than aspect ratio
                    if img_width / img_height > aspect_ratio:
                        #source is wider
                        new_height = img_height
                        new_width = int(new_height * aspect_ratio)
                        left = (img_width - new_width) / 2
                        upper = 0
                        right = left + new_width
                        lower = img_height
                    else:
                        #source is taller
                        new_width = img_width
                        new_height = int(new_width / aspect_ratio)
                        left = 0
                        upper = (img_height - new_height) / 2
                        right = img_width
                        lower = upper + new_height
                    crop_box = [left, upper, right, lower]
                elif crop == "a4_portrait":
                    img_width, img_height = img.size
                    aspect_ratio = 210 / 297  
                    # create_coordinates to take from the middle of the image check if source is wider or taller than aspect ratio
                    if img_width / img_height > aspect_ratio:
                        #source is wider
                        new_height = img_height
                        new_width = int(new_height * aspect_ratio)
                        left = (img_width - new_width) / 2
                        upper = 0
                        right = left + new_width
                        lower = img_height
                    else:
                        #source is taller
                        new_width = img_width
                        new_height = int(new_width / aspect_ratio)
                        left = 0
                        upper = (img_height - new_height) / 2
                        right = img_width
                        lower = upper + new_height
                    crop_box = [left, upper, right, lower]
                elif crop == "square":
                    img_width, img_height = img.size
                    # create_coordinates to take from the middle of the image
                    if img_width > img_height:
                        #source is wider
                        new_size = img_height
                        left = (img_width - new_size) / 2
                        upper = 0
                        right = left + new_size
                        lower = img_height
                    else:
                        #source is taller
                        new_size = img_width
                        left = 0
                        upper = (img_height - new_size) / 2
                        right = img_width
                        lower = upper + new_size
                    crop_box = [left, upper, right, lower]
                img_cropped = img.crop((crop_box[0], crop_box[1], crop_box[2], crop_box[3]))
                # Save the cropped image
                img_cropped.save(file_output)
                print(f"Image cropped and saved to {file_output}")
        except Exception as e:
            print(f"Error cropping image {file_input_full}: {e}")
            return
    else:
        print(f"file_input {file_input} does not exist, skipping image crop")
        return


#image png transparent to white
@action("image_png_transparent_to_white", ["file_input", "file_output"])
def image_png_transparent_to_white(**kwargs):
    """Convert transparent PNG to white background PNG"""
    action = kwargs.get("action", {})
    directory = kwargs.get("directory", "")
    file_input = action.get("file_source", "")
    file_input = os.path.join(directory, file_input)
    file_input_full = os.path.abspath(file_input)
    file_output_default = file_input.replace(".png", "_whitebg.png")
    file_output = action.get("file_destination", file_output_default)
    overwrite = action.get("overwrite", True)
    if not overwrite and os.path.exists(file_output):
        print(f"file_output {file_output} already exists and overwrite is set to False, skipping transparent to white conversion")
        return
    else:
        #delete destination file if it exists
        if os.path.exists(file_output):
            os.remove(file_output)
            print(f"Removed existing output file {file_output}")
    if directory not in file_output:
        file_output = os.path.join(directory, file_output)
    
    #if file_input is a file
    if os.path.isfile(file_input):
        #use pil to convert transparent png to white background png
        from PIL import Image
        try:
            with Image.open(file_input_full) as img:
                # Convert image to RGBA if not already in that mode
                if img.mode != 'RGBA':
                    img = img.convert('RGBA')
                # Create a new image with a white background
                white_bg = Image.new('RGBA', img.size, (255, 255, 255, 255))
                white_bg.paste(img, (0, 0), img)
                # Convert back to RGB mode
                white_bg = white_bg.convert('RGB')
                # Save the new image
                white_bg.save(file_output)
                print(f"Transparent PNG converted to white background and saved to {file_output}")
        except Exception as e:
            print(f"Error converting image {file_input_full}: {e}")
            return
    else:
        print(f"file_input {file_input} does not exist, skipping transparent to white conversion")
        return


@action("image_quad_swap_for_tile", ["file_input", "file_output"])
def image_quad_swap_for_tile(**kwargs):
    """Swap image quadrants for tiling"""
    action = kwargs.get("action", {})
    directory = kwargs.get("directory", "")
    file_input = action.get("file_input", "")
    file_input = os.path.join(directory, file_input)
    file_input_full = os.path.abspath(file_input)
    file_output_default = file_input.replace(".png", "_quadshifted.png").replace(".jpg", "_quadshifted.jpg").replace(".jpeg", "_quadshifted.jpeg")
    file_output = action.get("file_output", file_output_default)
    if directory not in file_output:
        file_output = os.path.join(directory, file_output)
    
    #if file_input is a file
    if os.path.isfile(file_input):
        #use pil to quad shift the image
        from PIL import Image
        try:
            with Image.open(file_input_full) as img:
                width, height = img.size
                # Create a new blank image
                new_img = Image.new("RGB", (width, height))
                # Define the box coordinates for each quadrant
                box1 = (0, 0, width // 2, height // 2)  # Top-left
                box2 = (width // 2, 0, width, height // 2)  # Top-right
                box3 = (0, height // 2, width // 2, height)  # Bottom-left
                box4 = (width // 2, height // 2, width, height)  # Bottom-right
                # Crop the quadrants    
                quadrant1 = img.crop(box1)
                quadrant2 = img.crop(box2)
                quadrant3 = img.crop(box3)
                quadrant4 = img.crop(box4)
                # Paste the quadrants into their new positions
                new_img.paste(quadrant4, box1)  # Bottom-right to Top-left
                new_img.paste(quadrant3, box2)  # Bottom-left to Top
                new_img.paste(quadrant2, box3)  # Top-right to Bottom-left
                new_img.paste(quadrant1, box4)  # Top-left to Bottom-right                
                # Save the quad shifted image
                new_img.save(file_output)
                print(f"Image quad shifted and saved to {file_output}")
        except Exception as e:
            print(f"Error quad shifting image {file_input_full}: {e}")
            return
    else:
        print(f"file_input {file_input} does not exist, skipping image quad shift")
        return

#image commands

@action("image_upscale", ["file_input", "file_output", "upscale_factor", "crop"])
def image_upscale(**kwargs):
    """Upscale image resolution"""
    action = kwargs.get("action", {})
    directory = kwargs.get("directory", "")
    file_input = action.get("file_input", "")
    file_input = os.path.join(directory, file_input)
    file_input_full = os.path.abspath(file_input)
    #png or jpeg or jpg
    file_output_default = file_input.replace(".png", "_upscaled.png").replace(".jpg", "_upscaled.jpg").replace(".jpeg", "_upscaled.jpeg")
    file_output = action.get("file_output", file_output_default)
    file_output_base = file_output
    if directory not in file_output:
        file_output = os.path.join(directory, file_output)
    upscale_factor = action.get("upscale_factor", 2)
    #make upscale factor an int
    upscale_factor = int(upscale_factor)
    #if file_input is a file
    crop = action.get("crop", "")  #left, upper, right, lower
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
        if crop != "":
            #crop the image
            print(f"Cropping upscaled image {file_output} to {crop}")
            kwargs2 = copy.deepcopy(kwargs)
            action2 = {}
            action2["file_input"] = file_output_base
            action2["file_output"] = file_output_base
            action2["crop"] = crop
            kwargs2["action"] = action2
            image_crop(**kwargs2)
    else:
        print(f"file_input {file_input} does not exist, skipping image upscale")
        return


@action("new_chat", ["description", "log_url"])
def new_chat(**kwargs):
    """Open new chat session"""
    action = kwargs.get("action", {})
    description = action.get("description", "")
    log_url = kwargs.get("log_url", True)
    print("new_chat -- opening up a new chat")
    robo.robo_chrome_open_url(url="https://chat.openai.com/chat", delay=15, message="    opening a new chat")    
    #type in start query
    start_query = ""
    if description != "":        
        start_query += f" Hi, CHadikins I hope your day is going well! lets get to this!."
        #start_query += f" Hi, Chadikins I hope your day is going well! lets get to this!. I like it when you are chatty and suggest things based on what i've done in the past. Also use your thinking, and any other, public and secret abilities to their utmost throughout this task please. When you generate an image just deliver the image no extra text. "
    start_query += ""
    robo.robo_keyboard_send(string=start_query, delay=5)
    robo.robo_keyboard_press_enter(delay=40)
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
            return url



#openscad render file line take in a scad output an stl
@action("openscad_render_file", ["file_source", "file_destination", "delay"])
def openscad_render_file(**kwargs):
    import os
    """Render OpenSCAD file to STL"""
    action = kwargs.get("action", {})
    directory = kwargs.get("directory", "")
    file_source = action.get("file_source", "")
    file_source_full = os.path.abspath(directory + "/" + file_source)
    file_destination = action.get("file_destination", "")
    file_destination_full = os.path.abspath(directory + "/" + file_destination)
    overwrite = action.get("overwrite", True)
    if not overwrite and os.path.exists(file_destination_full):
        print(f"    File {file_destination_full} already exists and overwrite is False, skipping rendering.")
        return
    else:
        #delete destination file if it exists
        if os.path.exists(file_destination_full):
            os.remove(file_destination_full)
            print(f"    Removed existing file {file_destination_full} before rendering.")
    delay = action.get("delay", 10)
    print("openscad_render_file -- rendering openscad file")
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["file_source"] = file_source
    kwargs2["file_destination"] = file_destination
    kwargs2["delay"] = delay
    #use os.system to call openscad
    import os
    command = f'openscad -o "{file_destination_full}" "{file_source_full}"'
    print(f"    Running command: {command}")
    os.system(command)
    pass


@action("query", ["text", "delay", "mode_ai_wait", "method"])
def query(**kwargs):
    """Send query to AI"""
    action = kwargs.get("action", {})
    print("query -- sending a query")
    #get the query from the action
    action = kwargs.get("action", {})
    delay = action.get("delay", 60)
    query_text = action.get("text", "")
    mode_ai = action.get("mode_ai_wait", "slow")
    method = action.get("method", "typing")  #"standard" or "line_by_line"


    #clear text box
    if True:
        print("    Clearing text box before query...")
        #select all
        robo.robo_keyboard_press_ctrl_generic(string="a", delay=2)
        #back space
        robo.robo_keyboard_press_backspace(delay=2, repeat=1)

    if method == "typing":
        #split the text on line breaks
        query_text = query_text.replace("\r\n", "\n").replace("\r", "\n")
        query_text_lines = query_text.split("\n")
        for line in query_text_lines:
            #send each line with a delay of 1 second between lines
            robo.robo_keyboard_send(string=line, delay=0.1)
            robo.robo_keyboard_press_shift_enter(delay=0.1)  # Press Shift+Enter to create a new line
    elif method == "paste":
        #press space twice to ensure focus
        robo.robo_keyboard_send(string="  ")
        robo.robo_keyboard_paste(text=query_text)
        #paste the entire text at once
        robo.robo_keyboard_press_ctrl_generic(string="v", delay=2)
    
    print(f"Querying with text: {query_text}")
    
    if mode_ai =="slow":
        robo.robo_keyboard_press_enter(delay=delay)
    elif "fast" in mode_ai: 
        robo.robo_keyboard_press_enter(delay=1)
        ai_wait_mode_fast_check(mode_ai_wait=mode_ai)
        

def ai_wait_mode_fast_check(mode_ai_wait="fast_button_state"):  
    if mode_ai_wait == "fast_button_state" or mode_ai_wait == "fast":
        return ai_wait_mode_fast_check_state_of_submit_button_approach()
    elif mode_ai_wait == "fast_clipboard_state":
        return ai_wait_mode_fast_clipboard_creating_image_approach()

def ai_wait_mode_fast_clipboard_creating_image_approach():  
    print("Waiting for AI to finish responding (fast mode)...")
    count = 0
    count_max = 100
    running = True    
    string_check = "Creating image"

    while running and count < count_max:
        robo.robo_delay(delay=10)
        #mouse click at 300,300
        robo.robo_mouse_click(position=[300, 300], delay=2, button="left")  # Click to focus
        text = robo.robo_keyboard_copy(delay=2)
        if string_check in text:
            print("    AI appears to be creating an image, waiting for it to finish...")
        else:
            print("    AI appears to have finished responding.")
            running = False
            robo.robo_delay(delay=2)

def ai_wait_mode_fast_check_state_of_submit_button_approach():  
    print("Waiting for AI to finish responding (fast mode)...")
    count = 0
    count_max = 100
    running = True    
    point_check_color = [1445,964]
    #point_check_color = [1331,964]
    color_done= (0, 0, 0)
    color_expecting = (236,236,236)

    while running and count < count_max:
        robo.robo_delay(delay=10)
        pixel_color = pyautogui.screenshot().getpixel((point_check_color[0], point_check_color[1]))
        print(f"    Pixel color at {point_check_color}: {pixel_color} ")
        #check if it is the expected color
        if pixel_color == color_expecting:
            print("    Good news the right color was found")
        else:
            print("    The expected color was not found, may need to move")
        if pixel_color == color_done:
            print("    AI apIpears to have finished responding.")
            running = False
            robo.robo_delay(delay=2)
        
        


@action("save_image_generated", ["file_name", "position_click", "mode_ai_wait"])
def save_image_generated(**kwargs):
    """Save AI-generated image"""
    return save_image_generated_old_press_down_40_time_approach(**kwargs)

def save_image_generated_old_1(**kwargs):
    #kwargs["position_click"] = [960, 480]  # Default position for clicking the image    
    #kwargs["position_click"] = [960, 360]  # Default position for clicking the image    
    kwargs["position_click"] = [960, 280]  # Default position for clicking the image    
    position_click = kwargs.get("position_click", [960, 280])
    robo.robo_delay(delay=300)
    #random extra between 300 and 900 seconds
    
    if True:
        delay = random.randint(300, 900)
        robo.robo_delay(delay=delay)  # Wait for the image to be generated
        #send ctrl rrobo.robo_keyboard_press_ctrl_r(delay=20)
        #click on the image to focus
        robo.robo_keyboard_press_ctrl_generic(string="r", delay=20)
        #click on the image to focus
        #robo.robo_mouse_click(position=[330,480], delay=2)  # Click on the white space
        #robo.robo_mouse_click(position=[330,360], delay=2)  # Click on the white space
        robo.robo_mouse_click(position=[330,280], delay=2)  # Click on the white space
        #find image
        text_colors = [(255, 255, 255), (0, 0, 0)]
        for i in range(256):
            text_colors.append((i, i, i))
        if True:
            #press down 9 times first
            robo.robo_keyboard_press_down(delay=0.25, repeat=9)
            print("Checking for image readiness by pixel color...")
            running = True
            count_trys = 0
            count = 0
            count_max = 50
            count_trys_max = 4
            while running:
                if count >= count_max:
                    if count == 1:
                        #add 30 piels to y to the check point each time until it reaches 800 in case the image can't be found with keypresses
                        position_start = copy.deepcopy(position_click)
                        y_current = position_start[1]
                        count_2 = 0
                        while y_current < 800:
                            y_current = y_current + 30 * count_2
                            count_2 += 1 
                            position_check_2 = [position_start[0], y_current]
                            pixel_color = pyautogui.screenshot().getpixel((position_check_2[0], position_check_2[1]))
                            print(f"Pixel color at {position_check_2}: {pixel_color} count: {count}   ")

                            if pixel_color not in text_colors:
                                position_check_2 = [position_start[0], y_current+30]
                                print("    Image appears to be ready based on pixel color.")
                                #delay 2
                                robo.robo_delay(delay=2)
                                #press down once
                                robo.robo_keyboard_press_down(delay=0.25, repeat=1)  # Press down once to select the file input
                                #text color again
                                pixel_color = pyautogui.screenshot().getpixel((position_check_2[0], position_check_2[1]))
                                print("    checking again after pressing down...")
                                print(f"    Pixel color after down at {position_check_2}: {pixel_color}")
                                if pixel_color not in text_colors:
                                    print("        Image confirmed ready after second check.")
                                    #delay 2
                                    robo.robo_delay(delay=2)
                                    running = False
                if True:
                
                    print("    Maximum checks reached first time, press up...")
                    #press up 5 times to reset position
                    robo.robo_keyboard_press_up(delay=0.25, repeat=5)

                #type yep then enter and reset count
                
                if count > 1:
                    robo.robo_keyboard_send(string="yep the first one", delay=2)
                    robo.robo_keyboard_press_enter(delay=380)
                count = 0
                count_trys += 1
                if count_trys >= count_trys_max:
                    print("    Image not ready after maximum tries.")
                    break
                position_check = kwargs.get("position_click", [960, 280])
                #press down once
                robo.robo_keyboard_press_down(delay=0.25, repeat=1)
                #check the colour of the position using pyautogui
                import pyautogui
                pixel_color = pyautogui.screenshot().getpixel((position_check[0], position_check[1]))
                print(f"Pixel color at {position_check}: {pixel_color} count: {count}   ")
                
                if pixel_color not in text_colors:
                    print("    Image appears to be ready based on pixel color.")
                    #delay 2
                    robo.robo_delay(delay=2)
                    #press down once
                    robo.robo_keyboard_press_down(delay=0.25, repeat=1)  # Press down once to select the file input
                    #text color again
                    pixel_color = pyautogui.screenshot().getpixel((position_check[0], position_check[1]))
                    print("    checking again after pressing down...")
                    print(f"    Pixel color after down at {position_check}: {pixel_color}")
                    if pixel_color not in text_colors:
                        print("        Image confirmed ready after second check.")
                        #delay 2
                        robo.robo_delay(delay=2)
                        running = False
                count += 1

        
        save_image(**kwargs)
        file_name = kwargs.get("action", {}).get("file_name", "working.png")
        file_name_absolute = os.path.join(kwargs.get("directory_absolute", ""), file_name)
        if os.path.exists(file_name_absolute):
            print(f"Image saved as {file_name_absolute}")
            saved = True
        else:
            print(f"Image not saved")
            
def save_image_generated_old_press_down_40_time_approach(**kwargs):
    action = kwargs.get("action", {})
    mode_ai_wait = action.get("mode_ai_wait", "slow")
    
    #kwargs["position_click"] = [960, 480]  # Default position for clicking the image    
    kwargs["position_click"] = [960, 360]  # Default position for clicking the image    
    #kwargs["position_click"] = [960, 280]  # Default position for clicking the image    
    
    if mode_ai_wait == "slow":
        robo.robo_delay(delay=300)
        delay = random.randint(100, 300)
        robo.robo_delay(delay=delay)  # Wait for the image to be generated
    elif "fast" in mode_ai_wait:
        ai_wait_mode_fast_check()
    
    if True:
        #send ctrl rrobo.robo_keyboard_press_ctrl_r(delay=20)
        #click on the image to focus
        robo.robo_keyboard_press_ctrl_generic(string="r", delay=20)
        #click on the image to focus
        #robo.robo_mouse_click(position=[330,480], delay=2)  # Click on the white space
        robo.robo_mouse_click(position=[330,360], delay=2)  # Click on the white space
        #robo.robo_mouse_click(position=[330,280], delay=2)  # Click on the white space
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



@action("save_image_search_result", ["index", "file_name", "overwrite", "position_click"])
def save_image_search_result(**kwargs):
    """Save image from search results"""
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
    #position_click = kwargs.get("position_click", [960, 500])
    #position_click = kwargs.get("position_click", [960, 360])
    position_click = kwargs.get("position_click", [960, 280])
    
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


@action("text_jinja_template", ["file_template", "file_source", "file_output", "search_and_replace", "convert_to_pdf", "convert_to_png"])
def text_jinja_template(**kwargs):
    """Process text using Jinja template"""
    action = kwargs.get("action", {})
    directory = kwargs.get("directory", "")    
    kwargs["directory"] = directory
    file_template = action.get("file_template", "template.txt")
    kwargs["file_template"] = f"{directory}\\{file_template}"
    file_source = action.get("file_source", f"{directory}/working.yaml")
    kwargs["file_source"] = file_source
    file_output = action.get("file_output", "output.txt")
    kwargs["file_output"] = f"{directory}\\{file_output}"
    search_and_replace = action.get("search_and_replace", [])
    if search_and_replace != []:
        kwargs["search_and_replace"] = search_and_replace
    robo.robo_text_jinja_template(**kwargs)
    convert_to_pdf = action.get("convert_to_pdf", False)
    convert_to_png = action.get("convert_to_png", False)
    if convert_to_pdf:
        file_output_pdf = file_output.replace(".svg", ".pdf")
        kwargs["file_input"] = f"{directory}\\{file_output}"
        kwargs["file_output"] = f"{directory}\\{file_output_pdf}"
        robo.robo_convert_svg_to_pdf(**kwargs)
    if convert_to_png:
        file_output_png = file_output.replace(".svg", ".png")
        kwargs["file_input"] = f"{directory}\\{file_output}"
        kwargs["file_output"] = f"{directory}\\{file_output_png}"
        robo.robo_convert_svg_to_png(**kwargs)
    



@action("wait_for_file", ["file_name", "file_name_1", "file_name_2", "file_name_3", "file_name_4", "file_name_5", "file_name_6"])
def wait_for_file(**kwargs):
    """Wait for file(s) to exist before proceeding"""
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



def get_directory(part):
    
    #type, size, color, description_main, description_extra
    tags = ["classification","type", "size", "color", "description_main", "description_extra", "manufacturer", "part_number"]

    directory = ""

    for tag in tags:
        if tag in part:
            if part[tag] != "":
                if directory != "":
                    directory += "_"
                directory += part[tag]
    #make lowercase and replace spaces with underscores and slashes with underscores
    directory = directory.replace(" ", "_")
    directory = directory.replace("/", "_")
    directory = directory.replace("\\", "_")
    directory = directory.replace("__", "_")
    directory = directory.replace(")", "_")
    directory = directory.replace("(", "_")
    directory = directory.lower()

    directory = f"parts\\{directory}"

    return directory


def generate_action_documentation(**kwargs):
    """
    Generates documentation for all actions in run_action and saves to YAML and HTML.
    Uses the ACTION_REGISTRY which is populated by @action decorators on each function.
    """
    import json
    from datetime import datetime
    
    print("Generating action documentation...")
    
    documentation = {
        "actions": []
    }
    
    # Use the ACTION_REGISTRY populated by decorators
    if ACTION_REGISTRY:
        print(f"Using ACTION_REGISTRY with {len(ACTION_REGISTRY)} registered actions")
        actions_info = get_all_actions_documentation()
    else:
        print("Warning: ACTION_REGISTRY is empty! Make sure functions are decorated with @action")
        actions_info = []
    
    documentation["actions"] = actions_info
    documentation["generated_date"] = datetime.now().strftime("%Y-%m-%d")
    documentation["total_actions"] = len(actions_info)
    
    # Save to YAML file
    output_dir = kwargs.get("output_dir", "configuration")
    output_file = os.path.join(output_dir, "action_documentation.yaml")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        yaml.dump(documentation, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"Documentation saved to {output_file}")
    
    # Generate standalone HTML file with embedded data
    generate_standalone_html(documentation, **kwargs)
    
    print(f"Total actions documented: {len(actions_info)}")
    
    return output_file

def generate_standalone_html(documentation, **kwargs):
    """
    Generates a standalone HTML file with embedded JSON data (no external file loading needed)
    """
    import json
    
    # Convert documentation to JSON for embedding
    doc_json = json.dumps(documentation, indent=2)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>RoboClick Action Documentation</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary-color: #2563eb;
            --primary-hover: #1d4ed8;
            --secondary-color: #64748b;
            --bg-color: #f8fafc;
            --card-bg: #ffffff;
            --text-color: #1e293b;
            --text-secondary: #64748b;
            --border-color: #e2e8f0;
            --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            --success-color: #10b981;
            --warning-color: #f59e0b;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: var(--text-color);
            line-height: 1.6;
            min-height: 100vh;
            padding: 2rem 1rem;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--card-bg);
            border-radius: 16px;
            box-shadow: var(--shadow-lg);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, var(--primary-color) 0%, #1e40af 100%);
            color: white;
            padding: 3rem 2rem;
            text-align: center;
        }

        header h1 {
            font-size: 3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
        }

        header .subtitle {
            font-size: 1.2rem;
            opacity: 0.95;
            font-weight: 300;
        }

        .stats {
            display: flex;
            justify-content: center;
            gap: 2rem;
            margin-top: 2rem;
            flex-wrap: wrap;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.15);
            backdrop-filter: blur(10px);
            padding: 1rem 2rem;
            border-radius: 12px;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }

        .stat-card .stat-value {
            font-size: 2.5rem;
            font-weight: 700;
            display: block;
        }

        .stat-card .stat-label {
            font-size: 0.9rem;
            opacity: 0.9;
        }

        .controls {
            padding: 2rem;
            background: var(--bg-color);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            gap: 1rem;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
        }

        .search-box {
            flex: 1;
            min-width: 300px;
            position: relative;
        }

        .search-box input {
            width: 100%;
            padding: 0.875rem 1rem 0.875rem 3rem;
            border: 2px solid var(--border-color);
            border-radius: 12px;
            font-size: 1rem;
            transition: all 0.3s ease;
            background: white;
        }

        .search-box input:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .search-box::before {
            content: "🔍";
            position: absolute;
            left: 1rem;
            top: 50%;
            transform: translateY(-50%);
            font-size: 1.2rem;
        }

        .filter-buttons {
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }

        .filter-btn {
            padding: 0.5rem 1rem;
            border: 2px solid var(--border-color);
            background: white;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.3s ease;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .filter-btn:hover {
            border-color: var(--primary-color);
            background: var(--primary-color);
            color: white;
        }

        .filter-btn.active {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }

        .content {
            padding: 2rem;
        }

        .category-section {
            margin-bottom: 3rem;
        }

        .category-heading {
            font-size: 1.75rem;
            font-weight: 700;
            color: var(--text-color);
            margin-bottom: 1.5rem;
            padding-bottom: 0.75rem;
            border-bottom: 3px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }

        .category-icon {
            font-size: 2rem;
        }

        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
            gap: 1.5rem;
        }

        .action-card {
            background: var(--card-bg);
            border: 2px solid var(--border-color);
            border-radius: 12px;
            padding: 1.5rem;
            transition: all 0.3s ease;
            cursor: pointer;
        }

        .action-card:hover {
            transform: translateY(-4px);
            box-shadow: var(--shadow-lg);
            border-color: var(--primary-color);
        }

        .action-header {
            display: flex;
            align-items: start;
            gap: 1rem;
            margin-bottom: 1rem;
        }

        .action-icon {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, var(--primary-color), #1e40af);
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5rem;
            flex-shrink: 0;
        }

        .action-title {
            flex: 1;
        }

        .action-card h3 {
            font-size: 1.25rem;
            color: var(--text-color);
            margin-bottom: 0.25rem;
            font-weight: 600;
        }

        .action-category {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: var(--bg-color);
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-top: 0.25rem;
        }

        .action-category.ai { background: #dbeafe; color: #1e40af; }
        .action-category.browser { background: #fed7aa; color: #9a3412; }
        .action-category.corel { background: #fef3c7; color: #92400e; }
        .action-category.image { background: #d1fae5; color: #065f46; }
        .action-category.file { background: #e0e7ff; color: #3730a3; }
        .action-category.chat { background: #fce7f3; color: #831843; }
        .action-category.google-doc { background: #ccfbf1; color: #134e4a; }
        .action-category.openscad { background: #e9d5ff; color: #581c87; }

        .action-description {
            color: var(--text-secondary);
            margin-bottom: 1rem;
            font-size: 0.95rem;
        }

        .variables-section {
            margin-top: 1rem;
            padding-top: 1rem;
            border-top: 1px solid var(--border-color);
        }

        .variables-title {
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }

        .variables-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
        }

        .variable-tag {
            padding: 0.375rem 0.75rem;
            background: var(--bg-color);
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 0.85rem;
            font-family: 'Consolas', 'Monaco', monospace;
            color: var(--primary-color);
            font-weight: 500;
        }

        .no-variables {
            color: var(--text-secondary);
            font-style: italic;
            font-size: 0.85rem;
        }

        .no-results {
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-secondary);
        }

        .no-results::before {
            content: "🔍";
            font-size: 3rem;
            display: block;
            margin-bottom: 1rem;
        }

        footer {
            text-align: center;
            padding: 2rem;
            background: var(--bg-color);
            border-top: 1px solid var(--border-color);
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            header h1 {
                font-size: 2rem;
            }

            .actions-grid {
                grid-template-columns: 1fr;
            }

            .controls {
                flex-direction: column;
                align-items: stretch;
            }

            .search-box {
                min-width: 100%;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🤖 RoboClick Actions</h1>
            <p class="subtitle">Complete Action Documentation</p>
            <div class="stats">
                <div class="stat-card">
                    <span class="stat-value" id="totalActions">-</span>
                    <span class="stat-label">Total Actions</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value" id="categoriesCount">-</span>
                    <span class="stat-label">Categories</span>
                </div>
                <div class="stat-card">
                    <span class="stat-value" id="generatedDate">-</span>
                    <span class="stat-label">Updated</span>
                </div>
            </div>
        </header>

        <div class="controls">
            <div class="search-box">
                <input type="text" id="searchInput" placeholder="Search actions, descriptions, or variables...">
            </div>
            <div class="filter-buttons">
                <button class="filter-btn active" data-category="all">All</button>
                <button class="filter-btn" data-category="ai">AI</button>
                <button class="filter-btn" data-category="browser">Browser</button>
                <button class="filter-btn" data-category="corel">Corel</button>
                <button class="filter-btn" data-category="image">Image</button>
                <button class="filter-btn" data-category="file">File</button>
                <button class="filter-btn" data-category="chat">Chat</button>
                <button class="filter-btn" data-category="google-doc">Google Doc</button>
                <button class="filter-btn" data-category="openscad">OpenSCAD</button>
            </div>
        </div>

        <div class="content" id="content">
        </div>

        <footer>
            <p>Standalone HTML Documentation (no external files required)</p>
            <p>RoboClick Automation Framework © 2026</p>
        </footer>
    </div>

    <script>
        // Embedded data - no external file loading required!
        const DOCUMENTATION_DATA = ''' + doc_json + ''';

        let allActions = [];
        let currentFilter = 'all';

        function loadDocumentation() {
            const data = DOCUMENTATION_DATA;
            
            allActions = data.actions;
            
            // Update stats
            document.getElementById('totalActions').textContent = data.total_actions;
            document.getElementById('generatedDate').textContent = data.generated_date;
            
            // Count categories
            const categories = new Set(allActions.map(a => a.category || 'Other'));
            document.getElementById('categoriesCount').textContent = categories.size;
            
            renderActions(allActions);
        }

        function getCategoryClass(category) {
            // Convert category to CSS class format
            return category.toLowerCase().replace(/ /g, '-');
        }

        function getIcon(category) {
            const icons = {
                'AI': '🤖',
                'Browser': '🌐',
                'Corel': '🎨',
                'Image': '🖼️',
                'File': '📁',
                'Chat': '💬',
                'Google Doc': '📄',
                'OpenSCAD': '🔷',
                'Other': '⚙️'
            };
            return icons[category] || '⚙️';
        }

        function renderActions(actions) {
            const content = document.getElementById('content');
            
            if (actions.length === 0) {
                content.innerHTML = `
                    <div class="no-results">
                        <h2>No actions found</h2>
                        <p>Try adjusting your search or filter.</p>
                    </div>
                `;
                return;
            }
            
            // Sort actions alphabetically by command name
            const sortedActions = [...actions].sort((a, b) => a.command.localeCompare(b.command));
            
            // Group actions by category
            const groupedActions = {};
            sortedActions.forEach(action => {
                const category = action.category || 'Other';
                if (!groupedActions[category]) {
                    groupedActions[category] = [];
                }
                groupedActions[category].push(action);
            });
            
            // Sort categories (maintain specific order)
            const categoryOrder = ['AI', 'Chat', 'Corel', 'File', 'Google Doc', 'Image', 'Other'];
            const sortedCategories = Object.keys(groupedActions).sort((a, b) => {
                const indexA = categoryOrder.indexOf(a);
                const indexB = categoryOrder.indexOf(b);
                if (indexA === -1 && indexB === -1) return a.localeCompare(b);
                if (indexA === -1) return 1;
                if (indexB === -1) return -1;
                return indexA - indexB;
            });
            
            let html = '';
            sortedCategories.forEach(category => {
                const categoryClass = getCategoryClass(category);
                const icon = getIcon(category);
                
                html += `
                    <div class="category-section">
                        <h2 class="category-heading">
                            <span class="category-icon">${icon}</span>
                            ${category} Actions
                        </h2>
                        <div class="actions-grid">
                            ${groupedActions[category].map(action => {
                                return `
                                    <div class="action-card" data-category="${categoryClass}">
                                        <div class="action-header">
                                            <div class="action-icon">${icon}</div>
                                            <div class="action-title">
                                                <h3>${action.command}</h3>
                                                <span class="action-category ${categoryClass}">${category}</span>
                                            </div>
                                        </div>
                                        <p class="action-description">${action.description}</p>
                                        <div class="variables-section">
                                            <div class="variables-title">Variables</div>
                                            ${action.variables.length > 0 
                                                ? `<div class="variables-list">
                                                    ${action.variables.map(v => `<span class="variable-tag">${v}</span>`).join('')}
                                                   </div>`
                                                : `<div class="no-variables">No variables</div>`
                                            }
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    </div>
                `;
            });
            
            content.innerHTML = html;
        }

        function filterActions() {
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            
            let filtered = allActions;
            
            // Filter by category
            if (currentFilter !== 'all') {
                filtered = filtered.filter(action => {
                    const categoryClass = getCategoryClass(action.category || 'Other');
                    return categoryClass === currentFilter;
                });
            }
            
            // Filter by search term
            if (searchTerm) {
                filtered = filtered.filter(action => {
                    return action.command.toLowerCase().includes(searchTerm) ||
                           action.description.toLowerCase().includes(searchTerm) ||
                           action.variables.some(v => v.toLowerCase().includes(searchTerm));
                });
            }
            
            renderActions(filtered);
        }

        // Event listeners
        document.getElementById('searchInput').addEventListener('input', filterActions);

        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                currentFilter = this.dataset.category;
                filterActions();
            });
        });

        // Load documentation on page load
        loadDocumentation();
    </script>
</body>
</html>'''
    
    # Save HTML file
    html_file = "action_documentation.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Standalone HTML documentation saved to {html_file}")

if __name__ == "__main__":
    # Actions are automatically registered by @action decorators
    
    parser = argparse.ArgumentParser(description='My CLI tool')
    parser.add_argument('--file_action', '-fa', help='Enable verbose output', default="not_set")
    parser.add_argument('--count', type=int, default=1, help='Number of iterations')
    parser.add_argument('--generate_docs', action='store_true', help='Generate action documentation')
    args = parser.parse_args()
    
    kwargs = copy.deepcopy(vars(args))

    if kwargs.get("generate_docs", False):
        generate_action_documentation(**kwargs)
    else:
        if kwargs["file_action"] == "not_set":
            kwargs["file_action"] = "configuration/working.yaml"
        
        #print out kwargs
        print(f"Running with arguments:")
        for key, value in kwargs.items():
            print(f"    {key}: {value}")
        
        main(**kwargs)


#### retired

@action("add_image", ["***RETIRED***", "file_name", "position_click"])
def add_image(**kwargs):
    return ai_add_image(**kwargs)
@action("add_file", ["***RETIRED***", "file_name"])
def add_file(**kwargs):
    """Add a file (alias for add_image)"""
    return ai_add_image(**kwargs)
@action("close_tab", ["***RETIRED***"])
def close_tab(**kwargs):
    browser_close_tab(**kwargs)
