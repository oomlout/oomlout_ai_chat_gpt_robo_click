import oomp
import copy

def load_parts(**kwargs):
    make_files = kwargs.get("make_files", True)
    #print "loading parts" plus the module name get the module name from the filename using __name__
    print(f"  loading parts {__name__}")
    create_generic(**kwargs)

def create_generic(**kwargs):
    print(f"  creating sellers")
    parts = []

    part_details = {}
    part_details["classification"] = "social_platform"
    part_details["type"] = "user"
    part_details["size"] = "whatnot"
    part_details["color"] = ""
    part_details["description_main"] = ""
    part_details["description_extra"] = ""
    part_details["manufacturer"] = ""
    part_details["part_number"] = ""

    default_empty = part_details.copy()

    profiles = []
    user = {}
    user["description_main"] = "lily_betts"
    user["description_extra"] = "food_fudge"
    user["link_social_platform_whatnot"] = f"https://www.whatnot.com/en-GB/user/{user['description_main']}"
    user["style"] = "work_and_chat"
    user["notes"] = "makes fudge in her kitchen, starts morning"
    profiles.append(user)
    user = {}
    user["description_main"] = "flowermama98"
    user["description_extra"] = "clothing_kid_clothing_woman_makeup_beauty"
    user["link_social_platform_whatnot"] = f"https://www.whatnot.com/en-GB/user/{user['description_main']}"
    user["style"] = "show_and_wait"
    user["notes"] = "kids clothes rail in background quite closed shot, just a put up and offer style"
    profiles.append(user)
    
    oomp.add_parts(parts, **kwargs)


if __name__ == "__main__":
    # run the function
    load_parts()    
    