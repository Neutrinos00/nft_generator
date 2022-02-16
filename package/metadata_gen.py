# -*- coding: utf-8 -*-

""" Please see licence for personnal use """

import os
import json


# {
#     "image": "1.png",
#     "attributes": {
#         "Base": "tattoos.scribble",
#         "Mouth": "Regular.Stubble,
#         "Eyecolor": "BLUE",
#         "Eyebrows": "regular",
#         "Piercings": "silver",
#         "Robotic": "robotic_mouth"
#     }
# }


class MetaDataGenerator:

    def __init__(self, outputPath: str) -> None:

        self.outputPath = outputPath

    def _basis_generation(self, asset_list: list, index: int):
        # definition of basis attributes
        attributes = {}
        for asset in asset_list:
            _dict = {asset.assetType: asset.name}
            attributes.update(_dict)

        # definition of basis meta data
        return {
            "image": str(index) + ".png",
            "attributes": attributes,
        }

    def _transformed_generation(self, basisMetaData: dict):
        attr = basisMetaData["attributes"]
        # transform EyesExpression key to EyesBrows
        if "EyesExpression" in attr:
            attr["EyesBrows"] = attr.pop("EyesExpression")

        return basisMetaData

    def generate(
        self,
        asset_list: list,
        index: int,
        debug: bool = False,
    ) -> None:

        basisMetaData = self._basis_generation(asset_list, index)
        transformedMetaData = self._transformed_generation(basisMetaData)

        if not debug:
            try:
                savepath = os.path.join(self.outputPath, str(index) + ".json")
                with open(savepath, 'w') as outfile:
                    json.dump(transformedMetaData, outfile)
                print(f"meta save in {savepath}")
            except:
                print("Error saving metadata")
        else:
            print("basis meta data =", basisMetaData)
            print("transf meta data =", transformedMetaData)
