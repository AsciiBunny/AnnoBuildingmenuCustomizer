from lxml import etree
from lxml.etree import XMLParser

new_doc = etree.ElementTree(etree.Element("Assets"))

doc = etree.parse("raw/assets.xml")
root = doc.getroot()

# Collect the actual menu structure
construction_menu = root.xpath("//Asset[Template='ConstructionMenu']")[0]
construction_menu.tag = "ConstructionMenu"
new_doc.getroot().append(construction_menu, )

# Augment menu structure with bundled "A_Modified_Ornaments_Tab" tabs
dep_doc = etree.parse(
    "resources/template_mod/[Addon] A_Modified_Ornaments_Tab/data/config/export/main/asset/ornaments_buildmenu_modify.include.xml",
    parser=XMLParser(recover=True, remove_comments=True)
)

construction_menu.xpath("//Moderate/OrnamentsMode/OrnamentsSource/Categories")[0].extend(
    dep_doc.xpath("//ModOp[@Type='addNextSibling' and contains(@Path,'Moderate/OrnamentsMode/OrnamentsSource')]")[0]
)
construction_menu.xpath("//Colony01/OrnamentsMode/OrnamentsSource/Categories")[0].extend(
    dep_doc.xpath("//ModOp[@Type='addNextSibling' and contains(@Path,'Colony01/OrnamentsMode/OrnamentsSource')]")[0]
)
construction_menu.xpath("//Moderate/OrnamentsMode/OrnamentsCategory/Categories")[0].extend(
    dep_doc.xpath("//ModOp[@Type='addNextSibling' and contains(@Path,'Moderate/OrnamentsMode/OrnamentsCategory')]")[0]
)
construction_menu.xpath("//Colony01/OrnamentsMode/OrnamentsCategory/Categories")[0].extend(
    dep_doc.xpath("//ModOp[@Type='addNextSibling' and contains(@Path,'Colony01/OrnamentsMode/OrnamentsCategory')]")[0]
)

construction_menu.xpath("//ConstructionMenu/RegionMenu/Arctic")[0].extend(
    dep_doc.xpath("//ModOp[@Type='add' and contains(@Path,'ConstructionMenu/RegionMenu/Arctic')]")[0]
)
construction_menu.xpath("//ConstructionMenu/RegionMenu/Africa")[0].extend(
    dep_doc.xpath("//ModOp[@Type='add' and contains(@Path,'ConstructionMenu/RegionMenu/Africa')]")[0]
)

# Collect all Construction Categories
categories = etree.Element("ConstructionCategory")
new_doc.getroot().append(categories)
for element in root.xpath("//Asset[Template='ConstructionCategory']"):
    category_guid = int(element.xpath("Values/Standard/GUID/text()")[0])
    if category_guid in [1911, 1912, 500946, 500951, 501004, 25000195]:
        continue
    categories.append(element)

# Collect all "A_Modified_Ornaments_Tab" Construction Categories
text_overrides = {
    1337505000: "Mods",
    1337505001: "Mods",
    1337505006: "Mods",
    1337505014: "Mods",

    1337505018: "Harbor",
    1337505019: "Harbor",
    1337505020: "Harbor",
    1337505021: "Harbor"

}
for element in dep_doc.xpath("//Asset[Template='ConstructionCategory']"):
    name = element.xpath("Values/Standard/Name/text()")[0]
    if name == "duplicate":
        continue
    category_guid = int(element.xpath("Values/Standard/GUID/text()")[0])
    if category_guid in text_overrides:
        category_text = element.xpath("Values/Text/LocaText/English/Text")[0]
        category_text.text = text_overrides[category_guid]
    categories.append(element)

# Scan all Construction Categories for the mentioned guids
used_guids = set()
for category in categories:
    for item in category.xpath("Values/ConstructionCategory/BuildingList/Item/Building/text()"):
        guid = int(item)
        used_guids.add(guid)

# Set up containing nodes
buildings = etree.Element("Building")
production_chains = etree.Element("ProductionChain")
extensions = etree.Element("Extension")
new_doc.getroot().append(buildings)
new_doc.getroot().append(production_chains)
new_doc.getroot().append(extensions)

second_pass = set()


# Scan over every asset to find all used_guids

def pass_all_assets(target_guids):
    for asset in root.xpath("//Asset[Values/Standard/GUID]"):
        asset_id = asset.xpath("Values/Standard/GUID")[0].text
        if int(asset_id) in target_guids:
            trimmed = etree.Element("Asset")
            trimmed.append(etree.Element("Values"))
            values = trimmed[0]

            is_building = False
            is_production_chain = False
            is_construction_category = False
            is_extension = False

            for element in asset.xpath("Values/Standard | Values/Text"):
                values.append(element)

            for element in asset.xpath("BaseAssetGUID"):
                assert is_extension is False
                values.addprevious(element)
                second_pass.add(int(element.text))
                is_extension = True

            for element in asset.xpath("Values/Building"):
                assert is_building is False
                building_node = etree.Element("Building")
                for building_element in asset.xpath(
                        "Values/Building/AssociatedRegions | Values/Building/BuildingCategoryName"):
                    building_node.append(building_element)
                values.append(building_node)
                is_building = True

            for element in asset.xpath("Template[text()='Tree']"):
                assert is_building is False
                is_building = True

            for element in asset.xpath("Values/ProductionChain"):
                assert is_production_chain is False
                values.append(element)
                is_production_chain = True

            for element in asset.xpath("Values/ConstructionCategory"):
                assert is_construction_category is False
                values.append(element)
                is_construction_category = True

            if is_extension:
                extensions.append(trimmed)
            elif is_building:
                buildings.append(trimmed)
            elif is_production_chain:
                production_chains.append(trimmed)
            else:
                assert False, etree.tostring(asset, pretty_print=True)


pass_all_assets(used_guids)
pass_all_assets(second_pass)

new_doc.write("resources/assets-extracted.xml", pretty_print=True)
