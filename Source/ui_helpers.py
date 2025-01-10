from PyQt5.QtWidgets import QTableWidget
from PyQt5.QtCore import Qt

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
    table_widget.setColumnCount(2)  # 两列：文件路径和完成时间
    table_widget.setHorizontalHeaderLabels(["压缩文件路径", "完成时间"])
    table_widget.horizontalHeader().setStretchLastSection(True)
    table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # 禁止编辑
    table_widget.setSelectionBehavior(QTableWidget.SelectRows)  # 整行选择
    table_widget.setSelectionMode(QTableWidget.SingleSelection)  # 单行选择
    table_widget.setDragEnabled(True)
    table_widget.setAcceptDrops(True)
    table_widget.setDefaultDropAction(Qt.CopyAction)
