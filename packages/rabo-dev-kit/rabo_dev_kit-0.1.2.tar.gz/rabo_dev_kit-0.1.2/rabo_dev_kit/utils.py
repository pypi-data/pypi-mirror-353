import os


def get_parameter_topic():
    return os.getenv('CONTROLLER_PARAMETER_TOPIC', '')