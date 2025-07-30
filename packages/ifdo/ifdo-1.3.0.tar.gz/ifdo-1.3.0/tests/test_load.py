import datetime

import json

from ifdo import iFDO, ImageData


def test_load_image_example():
    with open("tests/ifdo-image-example.json") as file:
        json_data = json.load(file)

    ifdo = iFDO.from_dict(json_data)

    assert ifdo.image_set_header.image_set_name == "SO268 SO268-1_21-1_OFOS SO_CAM-1_Photo_OFOS"
    assert isinstance(ifdo.image_set_items["SO268-1_21-1_OFOS_SO_CAM-1_20190304_083724.JPG"], ImageData)
    assert ifdo.image_set_items["SO268-1_21-1_OFOS_SO_CAM-1_20190304_083724.JPG"].image_datetime == datetime.datetime(
        2019, 3, 4, 8, 37, 24
    )


def test_load_video_example():
    with open("tests/ifdo-video-example.json") as file:
        json_data = json.load(file)

    ifdo = iFDO.from_dict(json_data)

    assert ifdo.image_set_header.image_set_name == "SO268 SO268-1_21-1_OFOS SO_CAM-1_Photo_OFOS"
    image_data = ifdo.image_set_items["SO268-1_21-1_OFOS_SO_CAM-1_20190304_083724.JPG"]
    if isinstance(image_data, list):
        assert image_data[1].image_datetime == datetime.datetime(2019, 3, 4, 8, 37, 25)
    else:
        assert image_data.image_datetime == datetime.datetime(2019, 3, 4, 8, 37, 25)
