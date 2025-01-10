import os

from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QMimeData, QUrl


def center_window(window):
    """将窗口居中显示"""
    screen = window.screen().geometry()
    size = window.geometry()
    window.move(
        (screen.width() - size.width()) // 2,
        (screen.height() - size.height()) // 2,
    )

def setup_table_widget(table_widget):
    """初始化表格控件"""
    table_widget.setColumnCount(3)  # 3列：文件路径和完成时间 操作
    table_widget.setHorizontalHeaderLabels(["压缩文件路径", "完成时间","操作"])
    table_widget.horizontalHeader().setStretchLastSection(True)
    table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
    table_widget.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择
    table_widget.setDragEnabled(True)
    table_widget.setAcceptDrops(True)
    table_widget.setDefaultDropAction(Qt.CopyAction)

def populate_table_row(table_widget, file_name, completion_time, source_path, cache_path, recompress_callback):
    """向表格中添加一行，包括文件名、时间、按钮"""
    row_position = table_widget.rowCount()
    table_widget.insertRow(row_position)
    table_widget.setItem(row_position, 0, QTableWidgetItem(file_name))
    table_widget.setItem(row_position, 1, QTableWidgetItem(completion_time))

    # 添加重新压缩按钮
    button = QPushButton("重新压缩")
    button.clicked.connect(lambda: recompress_callback(source_path, os.path.join(cache_path, file_name)))
    table_widget.setCellWidget(row_position, 2, button)

    # 设置列宽
    table_widget.setColumnWidth(0, 350)
    table_widget.setColumnWidth(1, 150)
    table_widget.setColumnWidth(2, 30)

def enable_drag_and_drop(table_widget, cache_path):
    """启用表格的拖拽功能"""
    def table_drag_event(event):
        if event.buttons() == Qt.LeftButton:
            selected_row = table_widget.currentRow()
            if selected_row != -1:
                file_name_item = table_widget.item(selected_row, 0)
                if file_name_item:
                    file_name = file_name_item.text()
                    file_path = os.path.join(cache_path, file_name)

                    # 设置拖拽数据
                    mime_data = QMimeData()
                    mime_data.setUrls([QUrl.fromLocalFile(file_path)])
                    drag = QDrag(table_widget)
                    drag.setMimeData(mime_data)
                    drag.exec_(Qt.CopyAction)

    table_widget.mouseMoveEvent = table_drag_event