import os
import logging


if not os.path.exists('logs'):
    os.mkdir("logs")


def get_logger(log_path):
    logging.basicConfig( handlers=[ logging.FileHandler(f"logs/{log_path}")], format='%(asctime)s - %(name)s - %(message)s', level=logging.INFO)
    return logging.getLogger()
