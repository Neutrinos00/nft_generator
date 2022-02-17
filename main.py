# -*- coding: utf-8 -*-

from package.nft_gen import NFTGenerator
from package.assets_gen import AssetsGenerator
import json
import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning)


def getConfig() -> dict:
    # get configuration info from config.json file
    JSON_PATH = "./config.json"
    try:
        with open(JSON_PATH, "r") as f:
            config = json.load(f)

        try:
            inputpath = config["INPUT_PATH"]
            outputs = config["OUTPUT_PATH"]
            CIP = config["CIP"]
            filters = config["FILTERS"]
            display = config["DISPLAY"]
        except:
            print(
                "error in extraction of info from config.json file : check data and json format"
            )

        print(f"  input_data_path = {inputpath}")
        print(f"  outputs_path = {outputs}")
        print(f"  CIP = {CIP}")
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
            CIP=config["CIP"],
            filters=config["FILTERS"],
            display=config["DISPLAY"],
            debug=False,
        ).build()


if __name__ == '__main__':
    main()
