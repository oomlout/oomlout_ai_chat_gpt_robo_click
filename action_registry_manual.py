"""
Action Registration Helper

This file contains the manual action registry that can be imported
instead of using decorators. This is easier to maintain than decorating
every function.

Simply import this at the top of oomlout_ai_roboclick.py:
    from action_registry_manual import register_all_actions
    
Then call it after importing:
    register_all_actions()
"""

# Complete list of all actions with their metadata
ACTIONS_METADATA = {
    "add_file": {
        "description": "Add a file (alias for add_image)",
        "variables": ["file_name"]
    },
    "add_image": {
        "description": "Add an image file to the current context",
        "variables": ["file_name", "position_click"]
    },
    "ai_fix_yaml_copy_paste": {
        "description": "Fix YAML formatting from copy-pasted content",
        "variables": ["file_input", "file_output", "remove_top_level", "new_item_name", "search_and_replace"]
    },
    "ai_save_image": {
        "description": "Save AI-generated image",
        "variables": ["file_name", "position_click", "mode_ai_wait"]
    },
    "ai_save_text": {
        "description": "Save text content from AI",
        "variables": ["file_name_full", "file_name_clip", "clip"]
    },
    "ai_set_mode": {
        "description": "Set AI mode (e.g., deep_research)",
        "variables": ["mode"]
    },
    "close_tab": {
        "description": "Close the current browser tab",
        "variables": []
    },
    "convert_svg_to_pdf": {
        "description": "Convert SVG file to PDF format",
        "variables": ["file_input", "file_output"]
    },
    "corel_add_text": {
        "description": "Add text in CorelDRAW",
        "variables": ["text", "x", "y", "font", "font_size", "bold", "italic"]
    },
    "corel_add_text_box": {
        "description": "Add text box in CorelDRAW",
        "variables": ["text", "x", "y", "width", "height", "font", "font_size", "bold", "italic"]
    },
    "corel_close_file": {
        "description": "Close current file in CorelDRAW",
        "variables": []
    },
    "corel_convert_to_curves": {
        "description": "Convert selected items to curves in CorelDRAW",
        "variables": ["ungroup", "delay"]
    },
    "corel_copy": {
        "description": "Copy selected items in CorelDRAW",
        "variables": []
    },
    "corel_export": {
        "description": "Export file from CorelDRAW",
        "variables": ["file_name", "file_destination", "file_type", "delay"]
    },
    "corel_group": {
        "description": "Group selected items in CorelDRAW",
        "variables": []
    },
    "corel_import": {
        "description": "Import file into CorelDRAW",
        "variables": ["file_name", "file_source", "x", "y", "width", "height", "max_dimension", "angle", "special"]
    },
    "corel_object_order": {
        "description": "Change object stacking order in CorelDRAW",
        "variables": ["order"]
    },
    "corel_open": {
        "description": "Open file in CorelDRAW",
        "variables": ["file_name", "file_source"]
    },
    "corel_page_goto": {
        "description": "Navigate to specific page in CorelDRAW",
        "variables": ["page_number"]
    },
    "corel_paste": {
        "description": "Paste copied items in CorelDRAW",
        "variables": ["x", "y", "width", "height"]
    },
    "corel_save": {
        "description": "Save current file in CorelDRAW",
        "variables": ["file_name"]
    },
    "corel_save_as": {
        "description": "Save file with new name in CorelDRAW",
        "variables": ["file_name", "file_destination"]
    },
    "corel_select_all": {
        "description": "Select all objects in CorelDRAW",
        "variables": []
    },
    "corel_set_position": {
        "description": "Set position of selected items in CorelDRAW",
        "variables": ["x", "y"]
    },
    "corel_set_rotation": {
        "description": "Set rotation angle of selected items in CorelDRAW",
        "variables": ["angle"]
    },
    "corel_set_size": {
        "description": "Set size of selected items in CorelDRAW",
        "variables": ["width", "height", "max_dimension", "select_all"]
    },
    "corel_trace": {
        "description": "Trace bitmap image in CorelDRAW",
        "variables": ["file_name", "remove_background_color_from_entire_image", "delay_trace", "number_of_colors", "detail_minus", "smoothing", "corner_smoothness"]
    },
    "corel_trace_full": {
        "description": "Complete trace workflow in CorelDRAW",
        "variables": ["file_source", "file_source_trace", "file_destination", "delay_trace", "delay_png", "max_dimension", "detail_minus", "x", "y", "number_of_colors", "remove_background_color_from_entire_image", "smoothing", "corner_smoothness"]
    },
    "file_copy": {
        "description": "Copy file from source to destination",
        "variables": ["file_source", "file_destination"]
    },
    "image_crop": {
        "description": "Crop image to specified format",
        "variables": ["file_input", "file_output", "crop"]
    },
    "image_upscale": {
        "description": "Upscale image resolution",
        "variables": ["file_input", "file_output", "upscale_factor", "crop"]
    },
    "image_quad_swap_for_tile": {
        "description": "Swap image quadrants for tiling",
        "variables": ["file_input", "file_output"]
    },
    "new_chat": {
        "description": "Open new chat session",
        "variables": ["description", "log_url"]
    },
    "continue_chat": {
        "description": "Continue existing chat session",
        "variables": ["url_chat", "log_url"]
    },
    "query": {
        "description": "Send query to AI",
        "variables": ["text", "delay", "mode_ai_wait", "method"]
    },
    "save_image_generated": {
        "description": "Save AI-generated image",
        "variables": ["file_name", "position_click", "mode_ai_wait"]
    },
    "save_image_search_result": {
        "description": "Save image from search results",
        "variables": ["index", "file_name", "overwrite", "position_click"]
    },
    "text_jinja_template": {
        "description": "Process text using Jinja template",
        "variables": ["file_template", "file_source", "file_output", "search_and_replace", "convert_to_pdf", "convert_to_png"]
    },
    "wait_for_file": {
        "description": "Wait for file(s) to exist before proceeding",
        "variables": ["file_name", "file_name_1", "file_name_2", "file_name_3", "file_name_4", "file_name_5", "file_name_6"]
    }
}

def register_all_actions(registry, globals_dict):
    """
    Register all actions from the metadata dict into the given registry.
    
    Args:
        registry: The ACTION_REGISTRY dict to populate
        globals_dict: The globals() dict to look up function objects
    """
    for command_name, metadata in ACTIONS_METADATA.items():
        if command_name in globals_dict:
            func = globals_dict[command_name]
            registry[command_name] = {
                'function': func,
                'description': metadata['description'],
                'variables': metadata['variables']
            }
            print(f"Registered action: {command_name}")
        else:
            print(f"Warning: Function '{command_name}' not found in globals")
    
    print(f"Total actions registered: {len(registry)}")
    return registry
