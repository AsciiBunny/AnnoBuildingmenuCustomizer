import shutil
from pathlib import Path

from lxml import etree

from data.construction_menu import ConstructionMenuTab, Session, TabType, ConstructionCategory


def generate_mod(construction_menu: dict[Session, ConstructionMenuTab], out_folder: Path):
    out_folder = out_folder / "[Misc] Customized Building Menu (Generated mod)"
    copy_mod_folder(out_folder)

    new_doc = etree.ElementTree(etree.Element("ModOps"))
    root = new_doc.getroot()

    for session, menu in construction_menu.items():
        for tab_type in TabType:
            for category in menu.get_list(tab_type):
                modop = generate_category_group(category)
                root.append(modop)

    xml_path = Path(out_folder / "data" / "config" / "export" / "main" / "asset" / "assets.xml")
    new_doc.write(xml_path, pretty_print=True)
    print("Exported mod")


def copy_mod_folder(out_folder: Path):
    shutil.copytree(Path("resources/template_mod"), out_folder, dirs_exist_ok=True)


def generate_category_replace_modop(category: ConstructionCategory):
    modop = etree.Element("ModOp", {"Type": "replace", "GUID": str(category.guid),
                                    "Path": "/Values/ConstructionCategory/BuildingList"})
    buildingList = etree.Element("BuildingList")
    modop.append(buildingList)
    for building in category.contents:
        item = etree.Element("Item")
        buildingList.append(item)
        building_node = etree.Element("Building")
        item.append(building_node)
        building_node.text = str(building.guid)
    return modop


# Add RemoveMe tag first
# Remove every known building
# Add Item tags before RemoveMe
# Remove RemoveMe
def generate_category_group(category: ConstructionCategory):
    modop = etree.Element("Group")

    modop.append(etree.Element("ModOp", {"Type": "addPrevSibling", "GUID": str(category.guid),
                                         "Path": "/Values/ConstructionCategory/BuildingList/Item[1]",
                                         "Condition": "/Values/ConstructionCategory/BuildingList[Item]"}))
    modop[0].append(etree.Element("RemoveMe"))

    modop.append(etree.Element("ModOp", {"Type": "add", "GUID": str(category.guid),
                                         "Path": "/Values/ConstructionCategory/BuildingList",
                                         "Condition": "/Values/ConstructionCategory/BuildingList[not(Item)]"}))
    modop[1].append(etree.Element("RemoveMe"))

    modop.append(generate_category_remove_group(category))
    modop.append(generate_category_add_group(category))

    modop.append(etree.Element("ModOp", {"Type": "remove", "GUID": str(category.guid),
                                         "Path": "/Values/ConstructionCategory/BuildingList/RemoveMe"}))
    return modop


def generate_category_remove_group(category: ConstructionCategory):
    modops = etree.Element("Group")
    for item_guid in category.original_contents:
        modops.append(generate_remove_modop(item_guid, category.guid))
    return modops


def generate_remove_modop(to_remove: int, category_guid: int):
    return etree.Element("ModOp", {"Type": "remove", "GUID": str(category_guid),
                                   "Path": "/Values/ConstructionCategory/BuildingList/Item[Building='" + str(
                                       to_remove) + "']"})


def generate_category_add_group(category: ConstructionCategory):
    modops = etree.Element("Group")
    for item in category.contents:
        modops.append(generate_add_modop(item.guid, category.guid))
    return modops


def generate_add_modop(item_id: int, category_guid: int):
    modop = etree.Element("ModOp", {"Type": "addPrevSibling", "GUID": str(category_guid),
                                    "Path": "/Values/ConstructionCategory/BuildingList/RemoveMe"})
    item = etree.Element("Item")
    item.append(etree.Element("Building"))
    item[0].text = str(item_id)
    modop.append(item)
    return modop
