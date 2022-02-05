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


class Asset:
    """ 
    Asset Defined by:
        - filepath (C:/.../Mad_Barbarian-30.png)
        - name (Mad_Barbarian)
        - type (base, mounth , ...)
        - filter (Barbarian) None if no filter
        - probability in percent (30)
    """

    def __init__(self, filepath: str, filters: list) -> None:
        self.filepath = filepath

        filename = os.path.basename(filepath)
        self.name = filename.split("-")[0]

        type = os.path.split(os.path.split(filepath)[0])[1]
        self.type = re.findall(r'[a-zA-Z]+', type)[0]

        self.probability = int(re.findall(r'\d+', filename)[0])

        self.filter = None
        for _filter in filters:
            if _filter in self.name:
                self.filter = _filter


class NFTGenerator:
    """ NFT Generator object

    Steps are as follows:

        1) Extraction, build of Asset objects and storage in _asset_type list attr
        2) Check probailities of assets integrity
        3)
    """

    def __init__(
        self,
        path: str,
        outputPath: str,
        filters: list,
        display: bool,
        debug: bool = False
    ) -> None:
        # few checks for noobs ===================
        if not isinstance(path, str):
            raise TypeError(f"{path} Arg should be of type string")
        if not os.path.isdir(path):
            raise IOError(f"{path} Arg is not a directory")

        if not isinstance(outputPath, str):
            raise TypeError(f"{outputPath} Arg should be of type string")

        if not isinstance(filters, list) or None:
            raise TypeError(f"{filters} Arg should be of type list or None")

        if not isinstance(display, bool):
            raise TypeError(f"{display} Arg should be of type bool")
        # ========================================

        self.path = path
        self.outputPath = outputPath
        self.filters = filters
        self.display = display
        self.debug = debug

        self._asset_types = []

    def build(self, N_NFT: int) -> None:
        # few checks for noobs ==================
        if not isinstance(N_NFT, int):
            raise TypeError(f"{N_NFT} should be of type integer")
        else:
            if not N_NFT > 0:
                raise ValueError("the number of NFT should be strictly > 0")
        # =======================================

        # extraction of assets
        self._fetchAndBuildAssets()
        # # verification of probabilities by filter and asset type then generation of N nfts
        if self._checkProbabilities():
            for i in range(N_NFT):
                self._generateSingleNFT(i)

    def _fetchAndBuildAssets(self) -> None:
        # extraction, creation and storage of asset objects by asset_types
        for foldname in sorted(os.listdir(self.path)):
            foldpath = os.path.join(self.path, foldname)
            if os.path.isdir(foldpath):
                _l = []
                for filename in os.listdir(foldpath):
                    filepath = os.path.join(foldpath, filename)
                    if os.path.isfile(filepath) and (".png" in filename or ".PNG" in filename):
                        _l.append(Asset(filepath, self.filters))
                self._asset_types.append(_l)

    def _checkProbabilities(self) -> bool:
        # TODO

        return True

    def _generateSingleNFT(self, index: int) -> None:
        # generation of an asset list with respect to filter and probabilities
        asset_list = self._buildSingleAssetList()
        savepath = self._mergeAssetsAndSaveNFTFile(asset_list, index)
        self._saveMetaData(asset_list, index)

    def _buildSingleAssetList(self) -> list:
        # choose a random base
        base_type = self._asset_types[0]
        probabilities = [ele.probability / 100 for ele in base_type]
        choosen_base = random.choices(
            population=base_type, weights=probabilities, k=1
        )[0]
        # build a list of asset with respect to the filter of the choosen base
        asset_list = [choosen_base]
        for asset_type in self._asset_types[1:]:

            # check is there any filter in asset_type
            # get list of probabilties for all asset of the same filter for an asset type
            # probabilities = [
            #     ele.probability / 100 for ele in asset_type if ele.filter == choosen_base.filter
            # ]
            # # fill asset_list with a random choice for an asset_type
            # asset_list.append(
            #     random.choices(population=asset_type,
            #                    weights=probabilities, k=1)[0]
            # )

            # TMP
            asset_list.append(
                random.choice(asset_type)
            )
            #

        return asset_list

    def _mergeAssetsAndSaveNFTFile(self, asset_list: list, index: int) -> None:
        # generate a list of images from asset object in asset_list
        images = [Image.open(asset.filepath) for asset in asset_list]

        # merge images to build final image
        bg = images[0]
        for _img in images[1:]:
            bg.paste(_img, (0, 0), _img)

        # save process and create output directory if not exist
        def save() -> None:
            bg.save(savepath)
            print(f"img save in {savepath}")
            if self.display:
                bg.show(str(index))
                return

        if self.debug:
            [print(asset.name) for asset in asset_list]
            bg.show(str(index))
        else:
            try:
                savepath = os.path.join(self.outputPath, str(index) + ".png")
                save()
            except FileNotFoundError:
                print("outpath does not exist : path is created")
                os.mkdir(self.outputPath)
                save()

    def _saveMetaData(self, asset_list: list, index: int) -> None:
        # define attribute of characters
        attributes = [
            {asset.type: [asset.name]} for asset in asset_list
        ]
        rarity = reduce(mul,  [asset.probability /
                        100 for asset in asset_list])
        # define data for metadata file
        data = {
            "name": str(index),
            "description": "CAT",
            "image": str(index) + ".png",
            "edition": 5,
            "date": str(datetime.now()),
            "attributes": attributes,
            "rarity": rarity
        }
        # save process
        if self.debug:
            print(data)
        else:
            savepath = os.path.join(self.outputPath, str(index) + ".json")
            with open(savepath, 'w') as outfile:
                json.dump(data, outfile)
            print(f"meta save in {savepath}")


def fetch_config():
    JSON_PATH = "./config.json"
    try:
        with open(JSON_PATH, "r") as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        print("config.json file does not exist in executed repository")
        return


def main() -> None:
    print("\n **** Welcom to custom NFT Generator ! **** ")
    print("\n Be aware and check if : \n\
         1- config.json file is well filled and provided \n\
         2- data repository containing only asset folds are provided")
    print("\n")
    N_NFT = int(input('Give an NFT number to generate : '))
    print("\n")

    config = fetch_config()
    if config:
        if os.path.exists(config["INPUT_PATH"]):
            NFTGenerator(
                path=config["INPUT_PATH"],
                outputPath=config["OUTPUT_PATH"],
                filters=config["FILTERS"],
                display=config["DISPLAY"],
                # debug=True,
            ).build(N_NFT=N_NFT)
    input()


if __name__ == "__main__":
    main()
