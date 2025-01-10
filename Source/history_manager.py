import os

from PyQt5.QtCore import QMimeData, QUrl, Qt
from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QTableWidgetItem


class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file

    def load_history(self, table_widget, cache_path):
        """加载历史记录到表格中"""
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as file:
                for line in file.readlines():
                    file_name, completion_time = line.strip().split('|')
                    row_position = table_widget.rowCount()
                    table_widget.insertRow(row_position)
                    table_widget.setItem(row_position, 0, QTableWidgetItem(file_name))
                    table_widget.setItem(row_position, 1, QTableWidgetItem(completion_time))

                    table_widget.setColumnWidth(0, 370)
                    table_widget.setColumnWidth(1, 130)
                    table_widget.setItem(row_position, 1, QTableWidgetItem(completion_time))

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

    def save_history(self, table_widget):
        """保存表格中的历史记录到文件"""
        with open(self.history_file, "w") as file:
            for row in range(table_widget.rowCount()):
                file_name = table_widget.item(row, 0).text()
                completion_time = table_widget.item(row, 1).text()
                file.write(f"{file_name}|{completion_time}\n")

    def add_entry(self, file_name, completion_time):
        """添加单个历史记录到文件"""
        with open(self.history_file, "a") as file:
            file.write(f"{file_name}|{completion_time}\n")
