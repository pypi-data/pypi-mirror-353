import os
import pickle
import numpy as np

current_path = os.path.dirname(os.path.abspath(__file__))


def read_pickle(filename):
    with open(filename, "rb") as f:
        return pickle.load(f)


def get_ua_array(ua_dict_: dict):
    ua_array_ = []
    for brand_id in ua_dict_:
        model_list = ua_dict_[brand_id]
        for device_id in model_list:
            for device_ua in model_list[device_id]:
                ua_array_.append(device_ua)
    return ua_array_


ua_dict = read_pickle(current_path + "/device_ua.pkl")

ua_array = get_ua_array(ua_dict)

len_ua_array = len(ua_array)


def get_random_ua(size: int = 1):
    if size <= 0:
        raise ValueError("Size must be bigger than 0")

    if size > len_ua_array:
        raise ValueError(
            f"The size is bigger than the array size, please check the size, the size of ua_array is: {len_ua_array}")

    return np.random.choice(ua_array, size)


def get_random_ua_with_brand(brand_id, size: int = 1):
    if size <= 0:
        raise ValueError("Size must be bigger than 0")
    brand_ua = []
    model_list = ua_dict[brand_id]
    for device_id in model_list:
        for device_ua in model_list[device_id]:
            brand_ua.append(device_ua)
    len_brand_ua = len(brand_ua)
    if size > len_brand_ua:
        raise ValueError(
            f"The ua of this brand does not have enough size, please check the size, the size of this brand is: {len_brand_ua}")
    return np.random.choice(brand_ua, size)

