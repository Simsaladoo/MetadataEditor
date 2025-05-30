# MetadataEditor
Unreal Meta-data direct editor tool

This tool operates within the Content Browser's right-click context menu on any class of user-select asset and allows for viewing, editing and saving Metadata key/values.

The UI is implemented using init_unreal.py that runs on Editor startup, and uses git to download the required dependency packages, qtpy/PySide.  They were be saved within the Project/Saved folder under /site-dependencies.

-Simsaladoo