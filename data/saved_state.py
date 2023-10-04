import json
import traceback

from data.construction_menu import MenuState


def save_state(file_name: str, menu_state: MenuState):
    category_contents = {}

    for guid, category in menu_state.construction_categories.items():
        category_contents[guid] = content = {}
        content["items"] = [item.guid for item in category.contents]
        content["removed"] = [item_guid for item_guid in category.original_contents
                              if item_guid not in content["items"]]

    with open(file_name, 'w') as file:
        json.dump({"categories": category_contents}, file, indent=2)


def load_state(file_name: str, menu_state: MenuState):
    hidden_items = set()
    try:
        with (open(file_name, 'rt') as file):
            category_contents = json.load(file)["categories"]

            for guid, contents in category_contents.items():
                guid = int(guid)

                if guid not in menu_state.construction_categories \
                        or "items" not in contents:
                    continue

                category = menu_state.construction_categories[guid]
                for index, item_guid in enumerate(reversed(contents["items"])):
                    item_guid = int(item_guid)
                    if not menu_state.is_in(item_guid):
                        continue
                    item = menu_state.get(item_guid)

                    if item in category.contents[index:]:
                        target_index = category.contents.index(item, index)
                        category.contents.pop(target_index)
                    category.contents.insert(0, item)

                if "removed" not in contents:
                    continue

                for item_guid in contents["removed"]:
                    item_guid = int(item_guid)
                    if item_guid not in category.original_contents:
                        continue
                    hidden_items.add(item_guid)
                    if not menu_state.is_in(item_guid):
                        continue
                    item = menu_state.get(item_guid)
                    category.contents.remove(item)

    except Exception as error:
        print("Tried to load invalid state:")
        traceback.print_tb(error.__traceback__)
        return False, []

    return True, sorted(hidden_items)
