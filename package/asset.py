# -*- coding: utf-8 -*-

import os
import re


class Asset:
    """ Basic asset define by : 

    """

    def __init__(
        self,
        filepath: str,
        assetType: str,
        filter: str = None,
    ) -> None:

        self.filepath = filepath
        self.filter = filter
        self.assetType = re.findall(r'[a-zA-Z]+', assetType)[0]
        self.name = os.path.basename(filepath).split("-")[0]
        self.probability = int(re.findall(
            r'\d+', os.path.basename(filepath))[0])
