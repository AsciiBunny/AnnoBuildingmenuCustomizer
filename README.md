
# Anno Building-menu Customizer (ABC)

As dlc's and mods add more and more options to your building-menu it can quickly feel cluttered. This tool lets you change it to your liking and then generate a mod to put it in game.


## Installation

Download the zip under [releases](https://github.com/AsciiBunny/AnnoBuildingmenuCustomizer/releases), extract to an empty folder and run ABC.exe . 

If you prefer you can also run from source by running `main.py` using Python 3.10+. Dependencies are in requirements.txt .
    
## Contributing

Contributions are always welcome!

ABC uses Python 3.10, used libraries are all in requirements.txt.

`main.py` starts the application, the argument `no_mods` can be used for quicker starting times during development. `extract_assets_xml.py` and `filter_icons.py` are used to extract and process the raw game assets in `/raw/ `.

`setup.py` is used to compile to a standalone application using cx_Freeze. Configuration is found in this py file, use argument `build` to run it.


## Credits

 - The awesome people in the Anno 1800 Modding Discord for technical help
 - Casper for being my annoying muse

