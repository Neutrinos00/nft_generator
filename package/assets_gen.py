# -*- coding: utf-8 -*-

""" Please see licence for personnal use """

import os

from package.asset import Asset


class AssetsGenerator:

    def __init__(self, datapath: str) -> None:
        self.datapath = datapath

    def generateAssets(self) -> list:
        # init the list of asset types
        asset_types = []
        # loop over folders to build asset types
        for i, foldname in enumerate(sorted(os.listdir(self.datapath))):
            foldpath = os.path.join(self.datapath, foldname)

            if os.path.isdir(foldpath):
                asset_type = {
                    "name": foldname,
                    "assets": None,
                    "filters": [],
                }
                print("- ", foldname, end='')

                # init the list of assets
                _list = []
                # loop over files to build asset
                for j, filename in enumerate(sorted(os.listdir(foldpath))):
                    filepath = os.path.join(foldpath, filename)

                    # if the file is a file -> fill asset list
                    if os.path.isfile(filepath) and (".png" in filename or ".PNG" in filename):
                        _list.append(
                            Asset(filepath, foldname, ID=int(str(i)+str(j))))

                    # if file is a dir this a filter
                    elif os.path.isdir(filepath):
                        print("     filter : ", filename, end='')
                        _asset_type = {
                            "filter_name": filename,
                            "assets": None,
                        }

                        # init the asset list of a filter
                        __list = []
                        # loop over files in filter
                        for k, _filename in enumerate(os.listdir(filepath)):
                            _filepath = os.path.join(filepath, _filename)
                            if os.path.isfile(_filepath):
                                __list.append(
                                    Asset(
                                        _filepath,
                                        foldname,
                                        filter=_filename,
                                        ID=int(str(i)+str(j)+str(k))
                                    )
                                )

                        # fill assets list value of asset type (filter)
                        _asset_type["assets"] = self._defineProbability(__list)
                        print(" : ok assets = ", len(__list), end="")
                        asset_type["filters"].append(_asset_type)

                    # pass if the file does not respect the format
                    else:
                        pass

                # fill assets list value of asset type
                asset_type["assets"] = self._defineProbability(_list)

            # fille asset types list
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
