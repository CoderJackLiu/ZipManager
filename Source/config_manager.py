import configparser
import os


class ConfigManager:
    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config_file = config_file
        self.default_width = 550
        self.default_height = 900
        self.load_config()

    def load_config(self):
        if not os.path.exists(self.config_file):
            self.config["Settings"] = {
                "CachePath": "",
                "WindowWidth": str(self.default_width),
                "WindowHeight": str(self.default_height),
            }
            self.save_config()
        else:
            self.config.read(self.config_file)

    def save_config(self):
        with open(self.config_file, "w") as file:
            self.config.write(file)

    def get_cache_path(self):
        return self.config.get("Settings", "CachePath", fallback="")

    def set_cache_path(self, path):
        """设置缓存路径"""
        self.config["Settings"]["CachePath"] = path
        self.save_config()

    def get_window_dimensions_width(self):
        return int(self.config.get("Settings", "WindowWidth", fallback=self.default_width))

    def get_window_dimensions_height(self):
        return int(self.config.get("Settings", "WindowHeight", fallback=self.default_height))

    def save_window_dimensions(self, width, height):
        """保存窗口宽度和高度到配置文件"""
        self.config["Settings"]["WindowWidth"] = str(width)
        self.config["Settings"]["WindowHeight"] = str(height)
        self.save_config()
