# -*- coding: utf-8 -*-

""" Please see licence for personnal use """

import os
import json


class MetaDataGenerator:

    def __init__(
        self,
        outputPath: str,
        CIP: bool = False,
        type: str = None,
    ) -> None:

        self.outputPath = outputPath
        self.CIP = CIP
        self.type = type

    def _basis_generation(self, asset_list: list, index: int) -> dict:
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

    def _transformed_generation(self, basisMetaData: dict) -> dict:
        attr = basisMetaData["attributes"]
        # replace EyesExpression key to EyesBrows
        if "EyesExpression" in attr:
            attr["EyesBrows"] = attr.pop("EyesExpression")

        # replace Attributes
        # attr["Mouth"] = attr["Mouth"].replace("_")
        # attr["Piercings"] = attr["Piercings"].replace("percings_", "", 1)
        # attr["Robotic"] = attr["Robotic"].replace("_Skull", "", 1)
        # attr["Robotic"] = attr["Robotic"].replace("_Skull_Short_Hair", "", 1)
        return basisMetaData

    def _CIP_generation(self, transformedMetaData: dict, index: int) -> dict:
        policy_ID = "null"
        asset_name = f"ProjectEND{index}"
        name = "ProjectEND #{:05d}".format(index)
        image = "ipfs://{:05d}.png".format(index)
        newMetaData = {
            "721": {
                policy_ID: {
                    asset_name: {
                        "Project": "Project E.N.D",
                        "name": name,
                        "image": image,
                        "attributes": transformedMetaData["attributes"],
                        "twitter": "https://twitter.com/Project__End",
                        "website": "https://www.Project__END.art",
                    },
                    "type": self.type,
                }
            }
        }
        return newMetaData

    def generate(
        self,
        asset_list: list,
        index: int,
        debug: bool = False,
    ) -> None:

        basisMetaData = self._basis_generation(asset_list, index)
        transformedMetaData = self._transformed_generation(basisMetaData)

        if self.CIP:
            transformedMetaData = self._CIP_generation(
                transformedMetaData, index)

        if not debug:
            try:
                savepath = os.path.join(self.outputPath, str(index) + ".json")
                with open(savepath, 'w') as outfile:
                    json.dump(transformedMetaData, outfile)
                #print(f"meta save in {savepath}")
            except:
                print("Error saving metadata")
        else:
            print("basis meta data =", basisMetaData)
            print("transf meta data =", transformedMetaData)
