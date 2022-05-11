# Romhack Races Baserom

This is the official baserom for creating Super Mario World race levels for [Romhack Races](https://romhackraces.com/). This baserom is tailor-made for both race level creation as well as general purpose hacking, but a lot of the changes made and patches included are to accommodate Kaizo level design in particular.

See the [baserom Wiki page](https://github.com/romhackraces/baserom/wiki/Changes-or-Additions-to-Vanilla-Super-Mario-World) for a detailed breakdown of the changes made to the base game. 

## Getting Started

The first thing you are going to do is patch your copy of unmodified Super Mario World with the `RHR4.bps` patch found in the main folder of this baserom, ensuring it has the name 'RHR4' and an extension of `.smc` when completed. This patch contains all of the changes already made so you can get going straightaway on building your Romhack Race level.

If you change the filename of your ROM be sure to rename the ancillary files included in this baserom and change all instances of `RHR4` found in the build scripts (usually specified by `ROM_NAME`) otherwise they will not work as intended.


### Helpful Scripts

To make life easier for you as a hacker, this baserom comes some helpful scripts to automate the process of applying additional custom assets to your ROM as well as for backing things up and creating a patch for distribution.

- `@build_baserom.bat` Does a lot of the work for you when it comes to inserting custom assets into your ROM by present a list the options corresponding to each of the tools. Additionally will create a BPS patch for distribution.
- `@backup_baserom.bat` Some basic backup options that leverages some Lunar Magic features to export all modified levels, edited map16 and/or shared palettes from your ROM, as well as a basic way to create a time-stamped backup of your ROM file, and create a BPS patch on demand.
- `@restore_from_backup.bat` Options to create a fresh ROM, restore global assets from a time-stamped based backup and imports previously-exported levels, map16 and palettes into it. Requires Lunar Magic and the backup scripts to be run first.
- `@tool_defines.bat` DO NOT RUN THIS! This file is just a series of definitions for where and what to download for the baserom tools, this is used by the other scripts.

See the [Wiki page](https://github.com/romhackraces/baserom/wiki/Using-the-Build-Scripts) for more information about these scripts.

## More Information

For more information about the creating levels for Romhack Races or for additional documentation about what is in the baserom check out the [baserom Wiki](https://github.com/romhackraces/baserom/wiki). If you need to view documentation for large resources included in the baserom, such as the Retry System, the `Docs` folder included in this baserom contains the relevant material.

If you have feedback or would like additional support with the baserom from the Romhack Races team, please visit the `#baserom-support` in the Romhack Races Discord server.

### Resource Credits

It is good practice to keep track of all resources used in your hacks if you can help it and credit their authors. See the included [CREDITS.txt](CREDITS.txt) file for a list of all resources included in the baserom or visit the [corresponding wiki page](https://github.com/romhackraces/baserom/wiki/Resources-Used-in-the-Baserom).

### Contributing

If you have suggestions or improvements for this baserom feel free to open issues or contribute to it on [GitHub](https://github.com/romhackraces/baserom) or reach out on Discord to one of the Romhack Races team. Important: this project has no license nor do the authors or organizers claim any rights to the resources included in this project, those remain the rights of their respective authors.