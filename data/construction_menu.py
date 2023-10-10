import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from lxml import etree
from lxml.etree import _Element, XMLParser

from data.mod import Mod, open_auto_encoding
from data.util import resource_path


class Session(Enum):
    OLD_WORLD = "Moderate"
    NEW_WORLD = "Colony01"
    ARCTIC = "Arctic"
    ENBESA = "Africa"
    META = "Meta"

    def get_name(self):
        return Session_Names[self]


Session_Names = {
    Session.OLD_WORLD: "Old World",
    Session.NEW_WORLD: "New World",
    Session.ARCTIC: "Arctic",
    Session.ENBESA: "Enbesa",
    Session.META: "Meta",
}


class TabType(Enum):
    FUNCTIONAL_BY_TIER = "functional_by_tier"
    FUNCTIONAL_BY_CATEGORY = "functional_by_category"
    ORNAMENTAL_BY_SOURCE = "ornamental_by_source"
    ORNAMENTAL_BY_CATEGORY = "ornamental_by_category"

    def get_name(self):
        return Type_Names[self]


Type_Names = {
    TabType.FUNCTIONAL_BY_TIER: "Functional by Tier",
    TabType.FUNCTIONAL_BY_CATEGORY: "Functional by Category",
    TabType.ORNAMENTAL_BY_SOURCE: "Ornamental by Source",
    TabType.ORNAMENTAL_BY_CATEGORY: "Ornamental by Category",
}


@dataclass
class Building:
    guid: int
    name: str
    text: str
    icon_path: Path

    sessions: list[Session]


@dataclass
class ConstructionCategory:
    guid: int
    name: str
    text: str
    icon_path: Path

    contents: list[Building, "ConstructionCategory"] = field(default_factory=list)
    original_contents: list[int] = field(default_factory=list)
    parentNode = False

    def set_contents(self, items, menu_state: "MenuState"):
        self.contents.clear()
        for item_guid in items:
            if menu_state.is_in(item_guid):
                self.contents.append(menu_state.get(item_guid))


@dataclass
class ConstructionMenuTab:
    by_tier: list[ConstructionCategory]
    by_category: list[ConstructionCategory]
    decorations_by_source: list[ConstructionCategory]
    decorations_by_category: list[ConstructionCategory]

    def get_list(self, type: TabType):
        match type:
            case TabType.FUNCTIONAL_BY_TIER:
                return self.by_tier
            case TabType.FUNCTIONAL_BY_CATEGORY:
                return self.by_category
            case TabType.ORNAMENTAL_BY_SOURCE:
                return self.decorations_by_source
            case TabType.ORNAMENTAL_BY_CATEGORY:
                return self.decorations_by_category


@dataclass
class MenuState:
    menu: dict[Session, ConstructionMenuTab]
    construction_categories: dict[int, ConstructionCategory]
    buildings: dict[int, Building]
    production_chains: dict[int, Building]

    def is_in(self, guid):
        return guid in self.construction_categories or guid in self.buildings or guid in self.production_chains

    def get(self, guid):
        if guid in self.construction_categories:
            return self.construction_categories[guid]

        if guid in self.buildings:
            return self.buildings[guid]

        if guid in self.production_chains:
            return self.production_chains[guid]

        return None


def clean_icon_path(icon_path: Path, mod_path: Path):
    if type(icon_path) != Path:
        try:
            icon_path = Path(str(icon_path))
        except:
            return "no_img"

    if len(icon_path.parts) < 1:
        return "no_img"

    # try mod path
    mod_icon_path = mod_path / icon_path
    if mod_icon_path.exists():
        return mod_icon_path

    # change extension
    icon_path_parts = list(icon_path.parts)
    icon_path_parts[-1] = icon_path_parts[-1].strip()[:-4] + ".dds"
    icon_path = Path(*icon_path_parts)

    # try mod path with dds extension
    mod_icon_path = mod_path / icon_path
    mod_icon_path_parts = list(mod_icon_path.parts)
    mod_icon_path_parts[-1] = mod_icon_path_parts[-1].strip()[:-4] + "_0.dds"
    mod_icon_path = Path(*mod_icon_path_parts)
    mod_icon_path = resource_path(mod_icon_path)
    if mod_icon_path.exists():
        return mod_icon_path

    if len(icon_path.parts) < 5 or icon_path.parts[4] != "3dicons":
        return "no_img"

    # try basegame icons
    icon_path_parts[-1] = icon_path_parts[-1].strip()[:-4] + ".png"
    path_parts = ["icons"] + icon_path_parts[5:]
    path = Path(*path_parts)

    path = resource_path(path)

    if path.exists():
        return path

    print(mod_path, icon_path)
    print(mod_icon_path, path)
    return "no_img"


def import_extracted_buildings(root: _Element, base_game: Mod):
    buildings = dict()
    for building_node in root.xpath("Building/Asset/Values"):
        building = import_building(building_node, base_game)
        buildings[building.guid] = building

    print("[Info] Loaded", len(buildings.keys()), "Buildings from xml")
    return buildings


def import_building(building_node: _Element, mod: Mod):
    guid = int(building_node.xpath("Standard/GUID/text()")[0])
    name = (building_node.xpath("Standard/Name/text()") or [""])[0]
    text = (building_node.xpath("Text/LocaText/English/Text/text()") or [""])[0]
    icon_path = (building_node.xpath("Standard/IconFilename/text()") or [""])[0]
    regions_text = building_node.xpath("Building/AssociatedRegions/text()")
    sessions = []

    if name == "":
        print("[Warning] Empty name:", etree.tostring(building_node))

    icon_path = clean_icon_path(icon_path, mod.path)

    if len(regions_text) > 0:
        for region in regions_text[0].split(";"):
            if region not in Session._value2member_map_:
                print("[Warning] Invalid region:", region)
                continue
            session = Session(region)
            sessions.append(session)
    return Building(guid, name, text, icon_path, sessions)


def extend_building(node: _Element, base_asset: Building, mod: Mod):
    guid = int(node.xpath("Standard/GUID/text()")[0])
    name = (node.xpath("Standard/Name/text()") or [base_asset.name])[0]
    text = (node.xpath("Text/LocaText/English/Text/text()") or [base_asset.text])[0]
    icon_path = (node.xpath("Standard/IconFilename/text()") or [base_asset.icon_path])[0]
    regions_text = node.xpath("Building/AssociatedRegions/text()")
    sessions = []

    if name == "":
        print("[Warning] Empty name:", etree.tostring(node))

    icon_path = clean_icon_path(icon_path, mod.path)

    if len(regions_text) > 0:
        for region in regions_text[0].split(";"):
            if region not in Session._value2member_map_:
                print("[Warning] Invalid region:", region)
                continue
            session = Session(region)
            sessions.append(session)
    if len(sessions) == 0:
        sessions = base_asset.sessions.copy()
    return Building(guid, name, text, icon_path, sessions)


def import_extracted_production_chains(root: _Element, base_game: Mod):
    production_chains = dict()
    for chain_node in root.xpath("ProductionChain/Asset/Values"):
        production_chain = import_production_chain(chain_node, base_game)
        production_chains[production_chain.guid] = production_chain

    print("[Info] Loaded", len(production_chains.keys()), "Production Chains from xml")
    return production_chains


def import_production_chain(chain_node: _Element, mod: Mod):
    guid = int(chain_node.xpath("Standard/GUID/text()")[0])
    name = (chain_node.xpath("Standard/Name/text()") or [""])[0]
    text = (chain_node.xpath("Text/LocaText/English/Text/text()") or [""])[0]
    icon_path = (chain_node.xpath("Standard/IconFilename/text()") or [""])[0]

    if name == "":
        print("[Warning] Empty name:", etree.tostring(chain_node))

    icon_path = clean_icon_path(icon_path, mod.path)

    return Building(guid, name, text, icon_path, [])


def extend_production_chain(chain_node: _Element, base_asset: Building, mod: Mod):
    guid = int(chain_node.xpath("Standard/GUID/text()")[0])
    name = (chain_node.xpath("Standard/Name/text()") or [base_asset.name])[0]
    text = (chain_node.xpath("Text/LocaText/English/Text/text()") or [base_asset.text])[0]
    icon_path = (chain_node.xpath("Standard/IconFilename/text()") or [base_asset.icon_path])[0]

    if name == "":
        print("[Warning] Empty name:", etree.tostring(chain_node))

    icon_path = clean_icon_path(icon_path, mod.path)

    return Building(guid, name, text, icon_path, [])


def import_extracted_extensions(root: _Element, buildings: dict[int, Building], production_chains: dict[int, Building],
                                base_game):
    for extension_node in root.xpath("Extension/Asset"):
        base_asset_guid = int(extension_node.xpath("BaseAssetGUID/text()")[0])
        values_node = extension_node.xpath("Values")[0]
        if base_asset_guid in buildings:
            building = extend_building(values_node, buildings[base_asset_guid], base_game)
            buildings[building.guid] = building
        elif base_asset_guid in production_chains:
            production_chain = extend_production_chain(values_node, production_chains[base_asset_guid], base_game)
            production_chains[production_chain.guid] = production_chain


def import_extracted_construction_category_extensions(root: _Element, menu_state: MenuState, base_game):
    for extension_node in root.xpath("Extension/Asset"):
        base_asset_guid = int(extension_node.xpath("BaseAssetGUID/text()")[0])
        values_node = extension_node.xpath("Values")[0]
        if base_asset_guid in menu_state.buildings or base_asset_guid in menu_state.production_chains:
            pass
        elif base_asset_guid in menu_state.construction_categories:
            base_asset = menu_state.construction_categories[base_asset_guid]
            category = extend_construction_category(values_node, base_asset, base_game)
            menu_state.construction_categories[category.guid] = category
        else:
            pass
            # building = import_building(values_node, base_game)
            # print("[Warning] Unloaded base asset:", base_asset_guid, building.name)


def import_extracted_construction_categories(root: _Element, menu_state: MenuState, base_game: Mod):
    construction_categories = menu_state.construction_categories
    for node in root.xpath("ConstructionCategory/Asset/Values"):
        construction_category = import_construction_category(node, base_game)
        construction_categories[construction_category.guid] = construction_category

    import_extracted_construction_category_extensions(root, menu_state, base_game)

    for node in root.xpath("ConstructionCategory/Asset/Values"):
        import_construction_category_contents(node, menu_state)

    for extension_node in root.xpath("Extension/Asset/Values"):
        guid = int(extension_node.xpath("Standard/GUID/text()")[0])
        if guid in construction_categories:
            import_construction_category_contents(extension_node, menu_state)

    print("[Info]", "Loaded", len(construction_categories.keys()), "Construction Categories from xml")
    return construction_categories


def import_construction_category(node: _Element, mod: Mod):
    guid_node = node.xpath("Standard/GUID/text()")
    guid = int(guid_node[0])
    name = node.xpath("Standard/Name/text()")[0]
    text = (node.xpath("Text/LocaText/English/Text/text()") or [""])[0]
    icon_path = (node.xpath("Standard/IconFilename/text()") or [""])[0]

    if text == "" and False:
        print("[Warning]", "Unnamed category: ", etree.tostring(node))

    icon_path = clean_icon_path(icon_path, mod.path)

    return ConstructionCategory(guid, name, text, icon_path)


def extend_construction_category(node: _Element, base_category, mod: Mod):
    guid = int(node.xpath("Standard/GUID/text()")[0])
    name = node.xpath("Standard/Name/text()")[0]
    text = (node.xpath("Text/LocaText/English/Text/text()") or [base_category.text])[0]
    icon_path = (node.xpath("Standard/IconFilename/text()") or [base_category.icon_path])[0]

    if text == "" and False:
        print("[Warning]", "Unnamed category: ", etree.tostring(node))

    icon_path = clean_icon_path(icon_path, mod.path)

    category = ConstructionCategory(guid, name, text, icon_path)
    category.base_category = base_category
    return category


def import_construction_category_contents(node: _Element, menu_state: MenuState):
    guid = int(node.xpath("Standard/GUID/text()")[0])
    construction_category = menu_state.construction_categories[guid]

    for item in node.xpath("ConstructionCategory/BuildingList/Item"):
        building_node = item.xpath("Building")
        vector_node = item.xpath("VectorElement/InheritedIndex")

        if building_node:
            item_guid = int(building_node[0].text)
        elif vector_node:
            vector_index = int(vector_node[0].text)
            item_guid = construction_category.base_category.contents[vector_index].guid
        else:
            print("[Warning]", "Invalid ConstructionCategory/Item: ", guid, construction_category.name)
            continue

        reference = menu_state.get(item_guid) if menu_state.is_in(item_guid) else None

        if type(reference) == ConstructionCategory:
            construction_category.parentNode = True

        if not reference:
            print("[Warning]", "unloaded reference:", item_guid, "in", guid, construction_category.name)
            continue

        construction_category.contents.append(reference)


def import_construction_category_additions(root: _Element, menu_state: MenuState):
    for element in root.xpath(
            "//ModOp[(@Type='add' or @Type='addNextSibling' or @Type='addPrevSibling' or @Type='replace') "
            "and ./Item/Building]"):

        if not element.get("GUID"):
            xpath_value: str = element.get("Path")
            if xpath_value.startswith("//*[self::BuildingList]") or xpath_value.startswith(
                    "//ConstructionCategory/BuildingList"):
                guids = [category_guid for category_guid in menu_state.construction_categories.keys()]
                only_if_found = True
            else:
                print("[Warning]", "Too complex: ", etree.tostring(element))
                continue
        else:
            guids = [int(guid.strip()) for guid in element.get("GUID").split(",")]
            only_if_found = False

        position_hint = None
        positions = re.findall("Building\\s*=\\s*['\"](\\d+)['\"]", element.get("Path", ""))
        if len(positions) >= 1:
            position_hint = int(positions[0])

        modop_type = element.get("Type")

        building_guids = element.xpath("Item/Building/text()")
        for guid in guids:
            if guid in menu_state.construction_categories:
                category = menu_state.construction_categories[guid]
                target_index = len(category.contents)
                if position_hint and modop_type != "add" and menu_state.is_in(position_hint):
                    target_building = menu_state.get(position_hint)
                    if target_building in category.contents:
                        target_index = category.contents.index(target_building)

                        if modop_type in ["addNextSibling", "replace"]:
                            target_index += 1

                if only_if_found and target_index == len(category.contents):
                    continue

                for building_guid in building_guids:
                    building_guid = int(building_guid)
                    if menu_state.is_in(building_guid):
                        assert menu_state.get(building_guid)
                        category.contents.insert(target_index, menu_state.get(building_guid))
                    else:
                        print("[Warning]", "unloaded reference:", building_guid, "in", guid, category.name)


def import_construction_menu(root: _Element, construction_categories: dict[int, ConstructionCategory]):
    menu_node: _Element = root.xpath("ConstructionMenu/Values/ConstructionMenu/RegionMenu")[0]
    menu = dict()
    for session_node in menu_node:
        session = Session(session_node.tag)

        by_tier = import_construction_menu_tab(session_node.xpath("CategoryMode/Tier"), construction_categories)
        by_category = import_construction_menu_tab(session_node.xpath("CategoryMode/BuildingCategory"),
                                                   construction_categories)
        decorations_by_source = import_construction_menu_tab(session_node.xpath("OrnamentsMode/OrnamentsSource"),
                                                             construction_categories)
        decorations_by_category = import_construction_menu_tab(session_node.xpath("OrnamentsMode/OrnamentsCategory"),
                                                               construction_categories)

        menu_item = ConstructionMenuTab(by_tier, by_category, decorations_by_source, decorations_by_category)
        menu[session] = menu_item

    print("[Info]", "Loaded 1 Construction Menu from xml")
    return menu


def import_construction_menu_tab(node: [_Element], construction_categories: dict[int, ConstructionCategory]):
    if not node:
        return []
    else:
        node = node[0]
    categories = node.xpath("Categories/Item/Category/text()")
    assert len(categories) == len(node.xpath("Categories/Item"))
    menu_tab_categories = []
    for category_id in categories:
        category_id = int(category_id)
        category = construction_categories[category_id] if category_id in construction_categories.keys() else None
        if not category:
            print("Invalid construction menu category [", category_id, "] in", node.getparent().tag, "/", node.tag)
        menu_tab_categories.append(category)

    return menu_tab_categories


def read_extracted_assets() -> MenuState:
    assets = etree.parse(resource_path("assets-extracted.xml"))
    root = assets.getroot()

    base_game = Mod(Path("."), True)

    buildings = import_extracted_buildings(root, base_game)
    production_chains = import_extracted_production_chains(root, base_game)
    import_extracted_extensions(root, buildings, production_chains, base_game)

    partial_menu_state = MenuState({}, {}, buildings, production_chains)

    construction_categories = import_extracted_construction_categories(root, partial_menu_state, base_game)

    parent_nodes = 0
    for category in construction_categories:
        if construction_categories[category].parentNode:
            parent_nodes += 1
    print("[Info]", parent_nodes, "Parent categories")

    menu = import_construction_menu(root, construction_categories)

    return MenuState(menu, construction_categories, buildings, production_chains)


def read_mod_assets(menu_state: MenuState, mods: dict[str, Mod], load_order: list[str]):
    for mod_name in load_order:
        read_mod_content(menu_state, mods[mod_name])

    for mod_name in load_order:
        read_mod_menu_additions(menu_state, mods[mod_name])


def read_mod_content(menu_state: MenuState, mod: Mod):
    if mod.name == "beau_customized_building_menu":
        return
    # print("[Loading]", mod.full_name, mod.path)
    xml = construct_xml(mod.path, mod.path, "./data/config/export/main/asset/assets.xml")
    if not xml:
        return

    # Import Mod's created Buildings
    for element in xml.xpath("//ModOp/Asset/Values[Building]"):
        building = import_building(element, mod)
        menu_state.buildings[building.guid] = building

    # Import Mod's created Production Chains
    for element in xml.xpath("//ModOp/Asset[Template='ProductionChain']/Values"):
        production_chain = import_production_chain(element, mod)
        menu_state.production_chains[production_chain.guid] = production_chain

    # Import BaseAssetGUID nodes
    for element in xml.xpath("//ModOp/Asset[BaseAssetGUID]"):
        base_asset_guid = int(element.xpath("BaseAssetGUID/text()")[0])
        values_node = element.xpath("Values")[0]
        if base_asset_guid in menu_state.buildings:
            building = extend_building(values_node, menu_state.buildings[base_asset_guid], mod)
            menu_state.buildings[building.guid] = building
        elif base_asset_guid in menu_state.production_chains:
            production_chain = extend_production_chain(values_node, menu_state.production_chains[base_asset_guid], mod)
            menu_state.production_chains[production_chain.guid] = production_chain
        elif base_asset_guid in menu_state.construction_categories:
            building = import_building(values_node, mod)
            print("[Warning] Unloaded base asset:", base_asset_guid, building.name)
        else:
            pass
            # building = import_building(values_node, mod)
            # print("[Warning] Unloaded base asset:", base_asset_guid, building.name)


def read_mod_menu_additions(menu_state: MenuState, mod: Mod):
    if mod.name == "beau_customized_building_menu":
        return
    print("[Loading]", mod.full_name, mod.path)
    xml = construct_xml(mod.path, mod.path, "./data/config/export/main/asset/assets.xml")
    if not xml:
        return

    # Import Mod's created ConstructionCategories without contents
    found_categories = xml.xpath("//ModOp/Asset[Template='ConstructionCategory']/Values")
    for element in found_categories:
        construction_category = import_construction_category(element, mod)
        if construction_category.guid in menu_state.construction_categories:
            if mod.name == "A_Modified_Ornaments_Tab":
                continue
            else:
                print("[Warning]", "Duplicate category:", construction_category.guid, construction_category.name)
        menu_state.construction_categories[construction_category.guid] = construction_category

    # Now import the contents
    for element in found_categories:
        import_construction_category_contents(element, menu_state)

    # Import every node that adds Items to Construction Categories
    import_construction_category_additions(xml.getroot(), menu_state)


def construct_xml(mod_path: Path, path: Path, glob: str):
    if glob[0] == "/":
        path = mod_path
        glob = glob[1:]

    asset_files = list(path.glob(glob))
    if len(asset_files) < 1:
        if glob != "./data/config/export/main/asset/assets.xml":
            print("Does not exist:", path, glob)
        return
    assert len(asset_files) == 1

    file = open_auto_encoding(asset_files[0], "r")
    xml = etree.parse(file, parser=XMLParser(recover=True, remove_comments=True))
    if xml.getroot().tag.casefold() != "ModOps".casefold():
        print("[Warning]", "Invalid xml file:", path, glob)
        return

    includes: list[_Element] = xml.xpath("//Include")
    for include in includes:
        include_xml = construct_xml(mod_path, asset_files[0].parent, include.get("File"))
        include_ops = include_xml.xpath("//ModOp")
        for op in include_ops:
            include.addnext(op)

    return xml


def store_base_state(menu: MenuState):
    for name, category in menu.construction_categories.items():
        for building in category.contents:
            category.original_contents.append(building.guid)
