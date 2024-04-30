#!/usr/bin/env python3

import common
import pprint


def main():
    youtube = common.get_resource()

    request = youtube.videoCategories().list(
        part="snippet",
        regionCode="US",
    )
    response = request.execute()

    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(response)


if __name__ == "__main__":
    main()
