import logging


def set_logger_level_error(env=locals()):
    if "spark" in list(env.keys()):
        logger = env["spark"]._jvm.org.apache.log4j
        logging.getLogger("py4j.java_gateway").setLevel(logging.ERROR)