import os

from ui_helpers import populate_table_row, enable_drag_and_drop


class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file

    def load_history(self, table_widget, cache_path, recompress_callback):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                for line in file.readlines():
                    file_name, completion_time, source_path = line.strip().split('|')
                    populate_table_row(
                        table_widget, file_name, completion_time, source_path, cache_path, recompress_callback
                    )
            # 启用拖拽功能
            enable_drag_and_drop(table_widget, cache_path)
    # 修改 save_history 方法，保存源文件路径
    def save_history(self, table_widget):
        with open(self.history_file, "w") as file:
            for row in range(table_widget.rowCount()):
                file_name = table_widget.item(row, 0).text()
                completion_time = table_widget.item(row, 1).text()
                source_path = table_widget.item(row, 2).text()
                file.write(f"{file_name}|{completion_time}|{source_path}\n")

    # 添加历史记录时保存源文件路径
    def add_entry(self, file_name, completion_time, source_path):
        with open(self.history_file, "a") as file:
            file.write(f"{file_name}|{completion_time}|{source_path}\n")

    def update_entry(self, file_name, completion_time, source_path):
        """更新历史记录中的文件时间戳和源文件路径"""
        if os.path.exists(self.history_file):
            lines = []
            with open(self.history_file, "r") as file:
                for line in file.readlines():
                    # 分割成文件名、时间戳、源文件路径
                    parts = line.strip().split('|')
                    if len(parts) == 3:
                        name, time, path = parts
                    else:
                        # 如果源文件路径缺失，设置默认空路径
                        name, time = parts
                        path = ""

                    # 如果匹配到文件名，更新时间戳和源文件路径
                    if name == file_name:
                        time = completion_time
                        path = source_path
                    lines.append(f"{name}|{time}|{path}\n")

            # 覆盖写入文件
            with open(self.history_file, "w") as file:
                file.writelines(lines)
