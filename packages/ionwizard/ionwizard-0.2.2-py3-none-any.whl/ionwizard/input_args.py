import argparse


def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", type=str, required=False)
    parser.add_argument("-k", type=str, required=False)
    config_args, pip_args = parser.parse_known_args()
    config_name = config_args.c
    license_key_file = config_args.k
    return config_name, license_key_file, pip_args
