import logging


class AppLogger:
    def __init__(self, name: str, level: int = logging.INFO):
        # Create a custom logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)

        # Check if logger already has handlers (to avoid duplicate handlers)
        if not self.logger.hasHandlers():
            # Create a console handler
            console_handler = logging.StreamHandler()
            console_handler.setLevel(level)

            # Create a formatter and set it for the handler
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            console_handler.setFormatter(formatter)

            # Add the handler to the logger
            self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger


app_logger = AppLogger(name="carvalue_logger").get_logger()
