# -*- coding: utf-8 -*-

import os

from package.asset import Asset


class AssetsGenerator:

    def __init__(self, datapath: str) -> None:
        self.datapath = datapath

        self.dna_list = []

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
                        _asset_type["assets"] = self._defineProbability(__list)
                        print(" : ok assets = ", len(__list), end="")
                        asset_type["filters"].append(_asset_type)

                    else:
                        pass

                asset_type["assets"] = self._defineProbability(_list)

            print(" : ok assets = ", len(_list))
            asset_types.append(asset_type)

        return asset_types

    def _defineProbability(self, asset_list: list) -> None:
        # normalization of probabilities
        current_probabilities = [asset.probability for asset in asset_list]
        tot = sum(current_probabilities)
        new_probabilities = [
            (ele / tot) * 100 for ele in current_probabilities
        ]
        # redefinition
        for i in range(len(asset_list)):
            asset_list[i].probability = new_probabilities[i]
        return asset_list
