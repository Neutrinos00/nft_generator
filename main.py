# -*- coding: utf-8 -*-
""":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
NFT GENERATOR
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::"""

from functools import reduce
from operator import mul
import os
import json
import random
import re
from datetime import datetime

from PIL import Image
import numpy as np
import blend_modes


class Asset:

    def __init__(
        self,
        filepath: str,
        assetType: str,
        filter: str = None,
    ) -> None:
        self.filepath = filepath
        self.assetType = re.findall(r'[a-zA-Z]+', assetType)[0]
        self.filter = filter

        filename = os.path.basename(filepath)
        self.name = filename.split("-")[0]

        self.probability = int(re.findall(r'\d+', filename)[0])


class AssetsGenerator:

    def __init__(self, datapath: str) -> None:
        self.datapath = datapath

    def generateAssets(self) -> list:
        asset_types = []
        for foldname in sorted(os.listdir(self.datapath)):
            foldpath = os.path.join(self.datapath, foldname)
            if os.path.isdir(foldpath):
                asset_type = {
                    "name": foldname,
                    "assets": None,
                    "filters": [],
                }
                print("- ", foldname, end='')
                _list = []
                for filename in sorted(os.listdir(foldpath)):
                    filepath = os.path.join(foldpath, filename)
                    if os.path.isfile(filepath) and (".png" in filename or ".PNG" in filename):
                        _list.append(Asset(filepath, foldname))
                    elif os.path.isdir(filepath):
                        print("     filter : ", filename, end='')
                        _asset_type = {
                            "filter_name": filename,
                            "assets": None,
                        }
                        __list = []
                        for _filename in os.listdir(filepath):
                            _filepath = os.path.join(filepath, _filename)
                            if os.path.isfile(_filepath):
                                __list.append(
                                    Asset(_filepath, foldname,
                                          filter=_filename)
                                )
                        # if not self._checkIntegrity(__list, filename):
                        #     return
                        _asset_type["assets"] = self._defineProbability(__list)
                        print(" : ok assets = ", len(__list), end="")
                        asset_type["filters"].append(_asset_type)
                    else:
                        pass
                # if not self._checkIntegrity(_list, foldname):
                #     return
                asset_type["assets"] = self._defineProbability(_list)
            print(" : ok assets = ", len(_list))
            asset_types.append(asset_type)
        return asset_types

    def _checkIntegrity(self, asset_list: list, name: str) -> bool:
        if not sum([asset.probability for asset in asset_list]) == 100:
            print("error of proba in : ", name)
            return False
        else:
            return True

    def _defineProbability(self, asset_list: list) -> None:
        current_probabilities = [asset.probability for asset in asset_list]
        tot = sum(current_probabilities)
        new_probabilities = [
            (ele / tot) * 100 for ele in current_probabilities]
        for i in range(len(asset_list)):
            asset_list[i].probability = new_probabilities[i]
        return asset_list


class NFTGenerator:

    def __init__(
        self,
        assetTypes: list,
        outputPath: str,
        N_NFT: int,
        filters: list = True,
        display: bool = False,
    ) -> None:

        self.assetTypes = assetTypes
        self.outputPath = outputPath
        self.N_NFT = N_NFT
        self.filters = filters
        self.display = True

        self.debug = True

    def build(self) -> None:
        for i in range(self.N_NFT):
            self._generateSingleNFT(i)

    def _generateSingleNFT(self, index: int) -> None:
        asset_list = self._buildSingleAssetList(index)
        self._mergeAssetsAndSaveNFTFile(asset_list, index)
        self._saveMetaData(asset_list, index)

    def _buildSingleAssetList(self, index: int) -> list:
        # definition of a weighted random choice
        def _chooseRandomly(_asset_list: list) -> Asset:
            probabilities = [ele.probability / 100
                             for ele in _asset_list]
            return random.choices(
                population=_asset_list, weights=probabilities, k=1
            )[0]

        # setting filter of the choosen base
        def _setFilterOfBase(choosenBase: Asset) -> str:
            for filter in self.filters:
                filt = re.findall(r'[a-zA-Z]+', filter)
                base_name = re.findall(r'[a-zA-Z]+', choosenBase.name)
                print(filt, base_name)
                if filt == base_name:
                    choosenBase.filter = filter

        # get base asset type from asset list
        baseType = self.assetTypes[0]["assets"]

        # choose a base randomly from proba
        choosenBase = _chooseRandomly(baseType)

        # get the filter from the choosen base if this filter exist
        _setFilterOfBase(choosenBase)

        # loop over assetTypes (beginning after base assetType)
        assetList = [choosenBase]
        for assetType in self.assetTypes[1:]:
            # check if the choosenBase has a filter and if it is present in filters of assetType
            if choosenBase.filter is not None and len(assetType["filters"]) != 0:
                choosenAsset = None
                for _filt in assetType["filters"]:
                    if _filt["filter_name"] == choosenBase.filter:
                        choosenAsset = _chooseRandomly(_filt["assets"])
                if choosenAsset is None:
                    choosenAsset = _chooseRandomly(assetType["assets"])
            # if not choose an asset from assets present in asset_type
            else:
                choosenAsset = _chooseRandomly(assetType["assets"])
            # fill asset_list with the choosen asset
            assetList.append(choosenAsset)
            if self.debug:
                asset_type_name = assetType["name"]
                print(
                    f"{index}: base={choosenBase.name}: basefilter={choosenBase.filter}: assettype={asset_type_name}: asset={choosenAsset.name}: assetfilter={choosenAsset.filter}"
                )
        return assetList

    def _mergeAssetsAndSaveNFTFile(self, asset_list: list, index: int) -> None:
        def old_version(images: list) -> Image:
            bg = images[0]
            for _img in images[1:]:
                bg.paste(_img, (0, 0), _img)
            return bg

        def blend(images: list) -> Image:
            arrays = [np.array(image).astype(float) for image in images]
            bg = arrays[0]
            for arr in arrays[1:]:
                bg = blend_modes.soft_light(bg, arr, opacity=0.5)
            bg = np.uint8(bg)
            return Image.fromarray(bg)

        images = [Image.open(asset.filepath) for asset in asset_list]
        bg = old_version(images)
        #bg = blend(images)

        self._saveFinalImage(bg, index)

    def _saveFinalImage(self, image: Image, index: int) -> None:
        def save() -> None:
            image.save(savepath)
            print(f"img save in {savepath}")
            if self.display:
                image.show(str(index))
                return

        if not self.debug:
            try:
                # save of image
                savepath = os.path.join(self.outputPath, str(index) + ".png")
                save()
                # if error due to inexistant output path create it and save
            except FileNotFoundError:
                print("outpath does not exist : path is created")
                os.mkdir(self.outputPath)
                save()

    def _saveMetaData(self, asset_list: list, index: int) -> None:
        # attributes are relatated of choosen asset in each asset_type
        attributes = [
            {asset.assetType: [asset.name]} for asset in asset_list
        ]
        # rarity is definied by the product of all proba of choosen asset in each asset_type
        rarity = reduce(mul,  [asset.probability /
                        100 for asset in asset_list])
        # definition of meta data
        data = {
            "name": str(index),
            "description": "CAT",
            "image": str(index) + ".png",
            "edition": 5,
            "date": str(datetime.now()),
            "attributes": attributes,
            "rarity": rarity,
            "filter": asset_list[0].filter,
        }

        if not self.debug:
            try:
                # save of meta data
                savepath = os.path.join(self.outputPath, str(index) + ".json")
                with open(savepath, 'w') as outfile:
                    json.dump(data, outfile)
                print(f"meta save in {savepath}")
            except:
                print("Error saving metadata")


def getConfig() -> dict:
    # get configuration info from config.json file
    JSON_PATH = "./config.json"
    try:
        with open(JSON_PATH, "r") as f:
            config = json.load(f)

        try:
            inputpath = config["INPUT_PATH"]
            outputs = config["OUTPUT_PATH"]
            filters = config["FILTERS"]
            display = config["DISPLAY"]
        except:
            print(
                "error in extraction of info from config.json file : check data and json format"
            )

        print(f"  input_data_path = {inputpath}")
        print(f"  outputs_path = {outputs}")
        print(f"  filters = {filters}")
        print(f"  display mode = {display}")

        return config

    except FileNotFoundError:
        print("config.json file does not exist in executed repository")
        return


def main() -> None:
    print("\n **** Welcom to custom NFT Generator ! **** \n")
    print("config : \n")
    config = getConfig()

    if config:
        N_NFT = int(input('\nGive an NFT number to generate : '))
        path = config["INPUT_PATH"]

        print("\nData generation & check\n")
        assetTypes = AssetsGenerator(path).generateAssets()

        print("\nData : ok\n")
        print("NFT generation : \n")
        NFTGenerator(
            assetTypes=assetTypes,
            outputPath=config["OUTPUT_PATH"],
            N_NFT=N_NFT,
            filters=config["FILTERS"],
            display=config["DISPLAY"],
        ).build()


if __name__ == '__main__':
    main()
