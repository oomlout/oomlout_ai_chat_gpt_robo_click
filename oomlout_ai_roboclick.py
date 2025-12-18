import random
import argparse
from statistics import mode
import yaml
import robo
import copy
import sys
import os
import pyautogui

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
            for key, value in result.items():
                workings[key] = value
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
    result = ""
    action = kwargs.get("action", {})
    command = action.get("command")
    #add_file
    if command == "add_file":
        result = add_file(**kwargs)
    if command == "add_image":
        result = add_image(**kwargs)
    #ai ones
    #ai_fix_yaml_copy_paste
    if command == "ai_fix_yaml_copy_paste":
        ai_fix_yaml_copy_paste(**kwargs)
    #ai_save_image
    elif command == "ai_save_image":
        save_image_generated(**kwargs)
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
    #convert svg_to_pdf
    elif command == "convert_svg_to_pdf":
        convert_svg_to_pdf(**kwargs)
    #corel add text        
    elif command == "corel_add_text":
        corel_add_text(**kwargs)
    elif command == "corel_add_text_box":
        corel_add_text_box(**kwargs)    
    elif command == "corel_close_file":
        corel_close_file(**kwargs)   
    #corel_convert_to_curves
    elif command == "corel_convert_to_curves":
        corel_convert_to_curves(**kwargs)
    #corel_group
    elif command == "corel_group":
        corel_group(**kwargs)     
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
    #set_rotation
    elif command == "corel_set_rotation":
        corel_set_rotation(**kwargs)
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
    #image_crop
    elif command == "image_crop":
        image_crop(**kwargs)
    #image_upscale
    elif command == "image_upscale":
        image_upscale(**kwargs)
    #image quad shift
    elif command == "image_quad_swap_for_tile":
        image_quad_swap_for_tile(**kwargs)
    elif command == "new_chat":
        kwargs
        result = new_chat(**kwargs)
        new_result = {}
        new_result["url_chat"] = result
        result = new_result
    elif command == "continue_chat":
        result = continue_chat(**kwargs)    
    elif command == "query":
        query(**kwargs)
    elif command == "save_image_generated":
        save_image_generated(**kwargs)
    elif command == "save_image_search_result":
        save_image_search_result(**kwargs)
    #text_jinja_template
    elif command == "text_jinja_template":
        text_jinja_template(**kwargs)
    elif command == "wait_for_file":
        result = wait_for_file(**kwargs)
    #if result is "exit", break the loop
    
    #if result is "exit_no_tab", dont close the tab
    return result
#actions


def add_image_tab_version_doesnt_work_if_rtext_box_not_selected(**kwargs):
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

def add_file(**kwargs):
    return add_image(**kwargs)

def add_image(**kwargs):
    return_value = ""
    print("add_image -- adding an image")
    #kwargs["position_click"] = [750,995]

    position_click = kwargs.get("position_click", [738, 982])
    #when the sidebar is closed
    #position_click = kwargs.get("position_click", [628, 982])
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


def ai_fix_yaml_copy_paste(**kwargs):
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

##### convert commands
def convert_svg_to_pdf(**kwargs):
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

def corel_add_text(**kwargs):
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

def corel_add_text_box(**kwargs):
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

def corel_copy(**kwargs):
    print("corel_copy -- copying selected items in corel")
    #copy selected items in corel
    robo.robo_corel_copy(**kwargs)


def corel_close_file(**kwargs):
    print("corel_close_file -- closing corel")
    #close corel
    robo.robo_corel_close_file(**kwargs)

def corel_convert_to_curves(**kwargs):
    print("corel_convert_to_curves -- converting selected items to curves in corel")
    action = kwargs.get("action", {})
    delay_convert = action.get("delay", 5)
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["delay"] = delay_convert
    robo.robo_corel_convert_to_curves(**kwargs2)

def corel_export(**kwargs):
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

def corel_group(**kwargs):
    print("corel_group -- grouping selected items in corel")
    #group selected items in corel
    robo.robo_corel_group(**kwargs)

def corel_import(**kwargs):
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
    #if file_name is "" try file_source
    if file_name == "":
        file_name = action.get("file_source", "")
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
    if file_name == "":
        file_name = action.get("file_destination", "")
    
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

#corel set rotation
def corel_set_rotation(**kwargs):
    print("corel_set_rotation -- setting rotation")
    action = kwargs.get("action", {})
    angle = action.get("angle", 0)
    
    kwargs2 = copy.deepcopy(kwargs)
    kwargs2["angle"] = angle
    robo.robo_corel_set_rotation(**kwargs2)

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

def corel_trace(**kwargs):
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

#image_crop
def image_crop(**kwargs):
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

def image_quad_swap_for_tile(**kwargs):
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
def image_upscale(**kwargs):
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

def continue_chat(**kwargs):
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

def query(**kwargs):
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
        
        

def save_image_generated(**kwargs):
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

def text_jinja_template(**kwargs):
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
