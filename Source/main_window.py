import os

from PyQt5.QtGui import QDrag
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QProgressBar, QTableWidget, QPushButton, QWidget, \
    QMessageBox, QTableWidgetItem
from PyQt5.QtCore import Qt, QMimeData, QUrl
from compression_worker import CompressionWorker
from config_manager import ConfigManager
from history_manager import HistoryManager
from ui_helpers import center_window, setup_table_widget
import threading
import keyboard
import win32gui
import win32con
import win32api

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件夹压缩管理工具")

        # 配置文件管理
        self.config_manager = ConfigManager("settings.ini")
        self.history_manager = HistoryManager("history.ini")

        self.cache_path = self.config_manager.get_cache_path()
        self.setGeometry(100, 100, self.config_manager.get_window_dimensions_width(),
                         self.config_manager.get_window_dimensions_height())
        center_window(self)

        # 主界面布局
        self.layout = QVBoxLayout()

        # 修改：增加“拖放文件夹到此区域”UI的高度
        self.label = QLabel("拖放文件夹到此区域")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: lightgray; font-size: 18px;")
        self.label.setFixedHeight(150)  # 调高到 150 像素
        self.layout.addWidget(self.label)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.table_widget = QTableWidget()
        setup_table_widget(self.table_widget)

        self.cache_button = QPushButton("设置缓存路径")
        self.cache_button.clicked.connect(self.set_cache_path)

        self.layout.addWidget(self.table_widget)
        self.layout.addWidget(self.cache_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        # 加载历史记录
        self.history_manager.load_history(self.table_widget, self.cache_path, self.recompress)

        # 拖拽支持
        self.label.setAcceptDrops(True)
        self.label.dragEnterEvent = self.dragEnterEvent
        self.label.dropEvent = self.dropEvent

        # 启动全局快捷键监听线程
        self.hotkey_thread = threading.Thread(target=self.listen_hotkey, daemon=True)
        self.hotkey_thread.start()

        self.worker = None

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            folder_path = url.toLocalFile()
            if os.path.isdir(folder_path):
                self.compress_folder(folder_path)

    def compress_folder(self, folder_path):
        if not self.cache_path:
            QMessageBox.warning(self, "提示", "请先设置缓存路径！")
            self.set_cache_path()  # 跳转到设置缓存路径界面
            if not self.cache_path:  # 如果用户取消了设置路径，则直接返回
                return

        output_path = os.path.join(self.cache_path, os.path.basename(folder_path) + ".zip")
        self.worker = CompressionWorker(folder_path, output_path)
        self.worker.progress.connect(self.update_progress)
        self.worker.completed.connect(self.add_to_list)
        self.worker.start()

    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)

    def add_to_list(self, zip_path, source_path):
        """添加压缩完成后的文件记录到表格中，避免重复"""
        from datetime import datetime
        completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        file_name = os.path.basename(zip_path)

        # 检查是否存在相同的文件名
        for row in range(self.table_widget.rowCount()):
            existing_file_name = self.table_widget.item(row, 0).text()
            if existing_file_name == file_name:
                # 更新时间
                self.table_widget.setItem(row, 1, QTableWidgetItem(completion_time))
                # 更新历史记录
                self.history_manager.update_entry(file_name, completion_time,source_path)
                return

        # 不存在则添加新记录
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(file_name))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(completion_time))


        # 添加重新压缩按钮
        button = QPushButton("重新压缩")
        button.clicked.connect(lambda: self.recompress(source_path, zip_path))
        self.table_widget.setCellWidget(row_position, 2, button)

        self.table_widget.setColumnWidth(0, 350)
        self.table_widget.setColumnWidth(1, 150)
        self.table_widget.setColumnWidth(2, 30)
        # 添加到历史记录
        self.history_manager.add_entry(file_name, completion_time,source_path)

    def recompress(self, source_path, zip_path):
        if not os.path.exists(source_path):
            QMessageBox.warning(self, "错误", "源文件路径不存在，无法重新压缩！")
            return
        self.compress_folder(source_path)

    def table_drag_event(self, event):
        """处理表格拖拽事件"""
        if event.buttons() == Qt.LeftButton:
            selected_row = self.table_widget.currentRow()
            if selected_row != -1:
                file_name_item = self.table_widget.item(selected_row, 0)
                file_name = file_name_item.text()

                # 在缓存路径中拼接文件完整路径
                file_path = os.path.join(self.cache_path, file_name)

                # 创建拖拽对象
                mime_data = QMimeData()
                mime_data.setUrls([QUrl.fromLocalFile(file_path)])
                drag = QDrag(self.table_widget)
                drag.setMimeData(mime_data)
                drag.exec_(Qt.CopyAction)

    def set_cache_path(self):
        """设置缓存路径"""
        from PyQt5.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "选择缓存路径")
        if path:
            self.cache_path = path
            self.config_manager.set_cache_path(path)

    def closeEvent(self, event):
        """窗口关闭事件，保存当前窗口大小"""
        self.config_manager.save_window_dimensions(self.width(), self.height())
        event.accept()

    def toggle_pin(self, checked):
        """切换窗口置顶状态"""
        if checked:
            self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(self.windowFlags() & ~Qt.WindowStaysOnTopHint)
        self.show()  # 刷新窗口状态

    def listen_hotkey(self):
        """监听全局快捷键"""
        keyboard.add_hotkey("ctrl+shift+f", self.activate_window)

    def activate_window(self):
        """通过模拟输入激活窗口"""
        hwnd = int(self.winId())  # 获取窗口句柄

        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 恢复窗口

        # 模拟 ALT 键以强制切换
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_EXTENDEDKEY, 0)
        win32gui.SetForegroundWindow(hwnd)  # 将窗口置于最前
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_EXTENDEDKEY | win32con.KEYEVENTF_KEYUP, 0)

    def set_hotkey(self, new_hotkey):
        """动态设置全局快捷键"""
        keyboard.clear_all_hotkeys()  # 清除旧快捷键
        keyboard.add_hotkey(new_hotkey, self.activate_window)  # 设置新快捷键
