from enums.commonExtension import *
from utilities.fileUtils import *


class ListSorter:
    @staticmethod
    def sortListToDict(listOfPaths: list[str]):
        # Create reverse lookup: extension → group
        ext_to_grp = {}
        for group, exts in common_extensions_by_group.items():
            for ext in exts:
                ext_to_grp[ext] = group

        # Define the order you want groups to appear in
        preferred_order = [
            "Executables",
            "Images",
            "Audio",
            "Video",
            "Text Documents",
            "Code",
            "Archives",
            "Config Data",
            "Fonts",
            "Disk Images"
        ]

        # Initialize categorized dictionary
        categorized = {group: [] for group in preferred_order}
        categorized["misc"] = []

        for path in listOfPaths:
            extension = FileUtils.getExtension(path)
            group = ext_to_grp.get(extension, "misc")
            categorized[group].append(path)

        # Remove any empty groups to keep results clean
        sorted_categorized = {
            group: categorized[group] for group in preferred_order if categorized[group]
        }
        
        # Include misc if it has items
        if categorized["misc"]:
            sorted_categorized["misc"] = categorized["misc"]

        return sorted_categorized
