import os

from PyQt5.QtCore import QMimeData, QUrl, Qt
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QTableWidgetItem, QPushButton, QMessageBox


class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file

    def load_history(self, table_widget, cache_path, recompress_callback):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                for line in file.readlines():
                    file_name, completion_time, source_path = line.strip().split('|')
                    row_position = table_widget.rowCount()
                    table_widget.insertRow(row_position)
                    table_widget.setItem(row_position, 0, QTableWidgetItem(file_name))
                    table_widget.setItem(row_position, 1, QTableWidgetItem(completion_time))

                    # 添加重新压缩按钮
                    button = QPushButton("重新压缩")
                    button.clicked.connect(
                        lambda _, sp=source_path, zp=os.path.join(cache_path, file_name): recompress_callback(sp, zp))
                    table_widget.setCellWidget(row_position, 2, button)

                    table_widget.setColumnWidth(0, 350)
                    table_widget.setColumnWidth(1, 150)
                    table_widget.setColumnWidth(2, 30)

        # 确保加载的历史记录支持拖拽
        table_widget.setDragEnabled(True)
        table_widget.setDefaultDropAction(Qt.CopyAction)

        # 定义拖拽事件
        def table_drag_event(event):
            if event.buttons() == Qt.LeftButton:
                selected_row = table_widget.currentRow()
                if selected_row != -1:
                    file_name_item = table_widget.item(selected_row, 0)
                    if file_name_item:
                        file_name = file_name_item.text()
                        file_path = os.path.join(cache_path, file_name)

                        mime_data = QMimeData()
                        mime_data.setUrls([QUrl.fromLocalFile(file_path)])
                        drag = QDrag(table_widget)
                        drag.setMimeData(mime_data)
                        drag.exec_(Qt.CopyAction)

        # 绑定事件
        table_widget.mouseMoveEvent = table_drag_event

    def recompress(self, source_path, zip_path):
        if not os.path.exists(source_path):
            QMessageBox.warning(None, "错误", "源文件路径不存在，无法重新压缩！")
            return
        #调用main_window.py中的compress_folder方法





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
