# -*- coding: utf-8 -*-

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

from package.asset import Asset


class NFTGenerator:
    """ Generator of NFT """

    def __init__(
        self,
        assetTypes: list,
        outputPath: str,
        N_NFT: int,
        filters: list = True,
        display: bool = False,
        debug: bool = False,
    ) -> None:

        self.assetTypes = assetTypes
        self.outputPath = outputPath
        self.N_NFT = N_NFT
        self.filters = filters
        self.display = display
        self.debug = debug

        self._DNA_list = []

    def build(self) -> None:
        for i in range(self.N_NFT):
            self._generateSingleNFT(i)

    def _generateSingleNFT(self, index: int) -> None:
        asset_list = self._buildSingleAssetList(index)
        if self._DNA_check(asset_list):
            self._mergeAssetsAndSaveNFTFile(asset_list, index)
            self._saveMetaData(asset_list, index)
        else:
            self._generateSingleNFT(index)

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
                    f"{index}: base={choosenBase.name}: \
                        basefilter={choosenBase.filter}: \
                        assettype={asset_type_name}: \
                        asset={choosenAsset.name}: \
                        assetfilter={choosenAsset.filter}"
                )
        return assetList

    def _DNA_check(self, asset_list: list) -> bool:
        ID_list = [asset.ID for asset in asset_list]
        if self.debug:
            print(ID_list)

        if ID_list not in self._DNA_list:
            self._DNA_list.append(ID_list)
            return True
        else:
            return False

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
                bg = blend_modes.normal(bg, arr, opacity=1)
            bg = np.uint8(bg)
            return Image.fromarray(bg)

        images = [Image.open(asset.filepath) for asset in asset_list]
        bg = blend(images)

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
