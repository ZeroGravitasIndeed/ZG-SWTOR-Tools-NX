## ZeroGravitas SWTOR Tools Next (beta)
(Yep, we are doing the "Next" thang 😅)

**The ZG SWTOR Tools NX is the successor to the original [ZG SWTOR Tools](https://github.com/SWTOR-Slicers/ZG-SWTOR-Tools)**.

The same way the latter used the [**.granny2 Plug-in**](https://github.com/SWTOR-Slicers/Granny2-Plug-In-Blender-2.8x) (AKA .gr2 Importer) to gain object and character import features and build upon them, this one uses the new, vastly superior **SWTOR Input-Output Tools** add-on, so capable that it is able to do Character and Area assembling completely on its own.

As a consequence, the **ZG SWTOR Tools NX** drops such features, now redundant, and will focus on new stuff, such as:
* A **Character Designer** (in underwear so far) that can replace TORCommunity.com's missing one.

* An **Armor Gear importer** (not yet exposed). Ideally it would be combined with the Character Designer, *a la* TORC's. We'll see.

* And objects and materials tools and "quality of life" features.

### We are not deleting the old add-ons

They still work, and Blender 5.2 hasn't broken them. We'll keep them available, specially for those who can't move on from Blender 3.6 or 4.2, or need them for modding. They might receive some maintenance if necessary, within reason.

### Compatibility

* The ZG SWTOR Tools (and the SWTOR IO Tools it depends on) require **Blender 4.5 LTS as a minimum**, and so far it seems compatible with 5.2 LTS. One assumes that it *ought* to work with 5.0, 5.1, *maybe* 5.3, but please always check any issues with the latest minor version numbers of the LTS releases.

* A Blender installation can have both the old add-ons (ZG Tools/.gr2 importer combo) and the new ones (ZG Tools NX/SWTOR IO Tools combo), but **only a given pair** can be enabled at once, or conflicts may occur.

* The new SWTOR IO Tools add-on provides new SWTOR materials that disregard the custom panels of old. Their advantage is that they are less fragile against Blender bugs, easier to update for us (they exist in an internal .blend template file), and far easier to tweak and modify by you.
  
  The disadvantage is that the ZG Tools relied on the old materials for conversion to its own, tricked out custom ones offering extras such as pores, normal strength, etc. The thing is, they are still available in the IO Tools (until Blender breaks them *again* 😒). We are seeing about making a new converter that can also be used with other material templates, your own included.

### Installation

The new usual for Blender 4.x and 5.x: **just drop them onto any Blender window**. If no SWTOR IO Tools add-on is present, the ZG Tools NX features that depend on it will appear in red, disabled.

### Preferences

For now, almost no preferences are exposed: those old ones like the path to a game assets extraction's "resources" folder are now in the companion IO Tools add-on, meant to serve that data to any other add-ons that want to use its features under the hood.

The **ZG SWTOR Tools NX** keeps on having in its Sidebar's tab a **Status** panel that exposes some basic settings such as object scale on import, or auto-rigging, plus a button to open the preferences panel, that now leads to the IO Tools' one and exposes all its possible settings.

### This is a WIP

Expect Kill Bill sirens at any moment.