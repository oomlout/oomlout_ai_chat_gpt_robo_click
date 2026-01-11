# Script to add @action decorators to all action functions
# This will be manually applied - just showing the pattern

ACTIONS_TO_ADD = [
    ('add_file', '["file_name"]', 'Add a file (alias for add_image)'),
    ('add_image', '["file_name", "position_click"]', 'Add an image file to the current context'),
    ('ai_fix_yaml_copy_paste', '["file_input", "file_output", "remove_top_level", "new_item_name", "search_and_replace"]', 'Fix YAML formatting from copy-pasted content'),
    ('ai_save_image', '["file_name", "position_click", "mode_ai_wait"]', 'Save AI-generated image'),
    ('ai_save_text', '["file_name_full", "file_name_clip", "clip"]', 'Save text content from AI'),
    ('ai_set_mode', '["mode"]', 'Set AI mode (e.g., deep_research)'),
    ('close_tab', '[]', 'Close the current browser tab'),
    ('convert_svg_to_pdf', '["file_input", "file_output"]', 'Convert SVG file to PDF format'),
    ('corel_add_text', '["text", "x", "y", "font", "font_size", "bold", "italic"]', 'Add text in CorelDRAW'),
    ('corel_add_text_box', '["text", "x", "y", "width", "height", "font", "font_size", "bold", "italic"]', 'Add text box in CorelDRAW'),
    ('corel_close_file', '[]', 'Close current file in CorelDRAW'),
    ('corel_convert_to_curves', '["ungroup", "delay"]', 'Convert selected items to curves in CorelDRAW'),
    ('corel_copy', '[]', 'Copy selected items in CorelDRAW'),
    ('corel_export', '["file_name", "file_destination", "file_type", "delay"]', 'Export file from CorelDRAW'),
    ('corel_group', '[]', 'Group selected items in CorelDRAW'),
    ('corel_import', '["file_name", "file_source", "x", "y", "width", "height", "max_dimension", "angle", "special"]', 'Import file into CorelDRAW'),
    ('corel_object_order', '["order"]', 'Change object stacking order in CorelDRAW'),
    ('corel_open', '["file_name", "file_source"]', 'Open file in CorelDRAW'),
    ('corel_page_goto', '["page_number"]', 'Navigate to specific page in CorelDRAW'),
    ('corel_paste', '["x", "y", "width", "height"]', 'Paste copied items in CorelDRAW'),
    ('corel_save', '["file_name"]', 'Save current file in CorelDRAW'),
    ('corel_save_as', '["file_name", "file_destination"]', 'Save file with new name in CorelDRAW'),
    ('corel_select_all', '[]', 'Select all objects in CorelDRAW'),
    ('corel_set_position', '["x", "y"]', 'Set position of selected items in CorelDRAW'),
    ('corel_set_rotation', '["angle"]', 'Set rotation angle of selected items in CorelDRAW'),
    ('corel_set_size', '["width", "height", "max_dimension", "select_all"]', 'Set size of selected items in CorelDRAW'),
    ('corel_trace', '["file_name", "remove_background_color_from_entire_image", "delay_trace", "number_of_colors", "detail_minus", "smoothing", "corner_smoothness"]', 'Trace bitmap image in CorelDRAW'),
    ('corel_trace_full', '["file_source", "file_source_trace", "file_destination", "delay_trace", "delay_png", "max_dimension", "detail_minus", "x", "y", "number_of_colors", "remove_background_color_from_entire_image", "smoothing", "corner_smoothness"]', 'Complete trace workflow in CorelDRAW'),
    ('file_copy', '["file_source", "file_destination"]', 'Copy file from source to destination'),
    ('image_crop', '["file_input", "file_output", "crop"]', 'Crop image to specified format'),
    ('image_upscale', '["file_input", "file_output", "upscale_factor", "crop"]', 'Upscale image resolution'),
    ('image_quad_swap_for_tile', '["file_input", "file_output"]', 'Swap image quadrants for tiling'),
    ('new_chat', '["description", "log_url"]', 'Open new chat session'),
    ('continue_chat', '["url_chat", "log_url"]', 'Continue existing chat session'),
    ('query', '["text", "delay", "mode_ai_wait", "method"]', 'Send query to AI'),
    ('save_image_generated', '["file_name", "position_click", "mode_ai_wait"]', 'Save AI-generated image'),
    ('save_image_search_result', '["index", "file_name", "overwrite", "position_click"]', 'Save image from search results'),
    ('text_jinja_template', '["file_template", "file_source", "file_output", "search_and_replace", "convert_to_pdf", "convert_to_png"]', 'Process text using Jinja template'),
    ('wait_for_file', '["file_name", "file_name_1", "file_name_2", "file_name_3", "file_name_4", "file_name_5", "file_name_6"]', 'Wait for file(s) to exist before proceeding'),
]

# Print decorator lines to add above each function
for command, vars, desc in ACTIONS_TO_ADD:
    print(f'@action("{command}", {vars})')
    print(f'def {command}(**kwargs):')
    print(f'    """{desc}"""')
    print()
