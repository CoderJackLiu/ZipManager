import sys
import os
import zipfile
import shutil
import configparser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QLabel, QProgressBar, QListWidget, QFileDialog, QWidget, QListWidgetItem,
    QPushButton, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData, QUrl
from PyQt5.QtGui import QDrag
from datetime import datetime  # 在文件顶部引入


class DraggableListWidget(QListWidget):
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            mime_data = QMimeData()
            file_path = item.text()  # 获取文件路径
            mime_data.setUrls([QUrl.fromLocalFile(file_path)])
            drag = QDrag(self)
            drag.setMimeData(mime_data)
            drag.exec_(Qt.CopyAction)


class CompressionWorker(QThread):
    progress = pyqtSignal(int)  # 整体进度
    completed = pyqtSignal(str)  # 压缩完成后的文件路径

    def __init__(self, folder_path, output_path):
        super().__init__()
        self.folder_path = folder_path
        self.output_path = output_path

    def run(self):
        total_files = sum([len(files) for _, _, files in os.walk(self.folder_path)])
        processed_files = 0

        with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(self.folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.folder_path)
                    zipf.write(file_path, arcname)
                    processed_files += 1
                    self.progress.emit(int((processed_files / total_files) * 100))
        self.completed.emit(self.output_path)


from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem  # 引入需要的类


# 替换 DraggableListWidget 为 QTableWidget
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("文件夹压缩管理工具")
        self.default_width = 550
        self.default_height = 900

        # 配置文件
        self.config = configparser.ConfigParser()
        self.config_file = "settings.ini"
        self.history_file = "history.ini"
        self.cache_path = ""
        self.history = []

        # 加载配置
        self.load_config()
        self.setGeometry(100, 100, self.window_width, self.window_height)
        self.center_window()  # 窗口居中

        # 主界面布局
        self.layout = QVBoxLayout()

        # 拖放区域
        self.label = QLabel("拖放文件夹到此区域")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("background-color: lightgray; font-size: 18px;")
        self.label.setFixedHeight(100)
        self.layout.addWidget(self.label)

        # 进度条
        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        # 文件列表（使用 QTableWidget）
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(2)  # 两列：文件路径和完成时间
        self.table_widget.setHorizontalHeaderLabels(["压缩文件路径", "完成时间"])
        self.table_widget.horizontalHeader().setStretchLastSection(True)  # 自动调整列宽
        self.layout.addWidget(self.table_widget)

        # 设置缓存路径按钮
        self.cache_button = QPushButton("设置缓存路径")
        self.cache_button.clicked.connect(self.set_cache_path)
        self.layout.addWidget(self.cache_button)

        container = QWidget()
        container.setLayout(self.layout)
        self.setCentralWidget(container)

        self.label.setAcceptDrops(True)
        self.label.dragEnterEvent = self.dragEnterEvent
        self.label.dropEvent = self.dropEvent

        # 加载历史记录
        self.load_history()

        self.worker = None

    def center_window(self):
        """将窗口居中显示"""
        screen = QApplication.primaryScreen().geometry()  # 获取屏幕尺寸
        size = self.geometry()  # 获取窗口尺寸
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )

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
        self.progress_bar.setValue(value)

    from PyQt5.QtCore import QMimeData, QUrl
    from PyQt5.QtGui import QDrag

    def start_drag(self):
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

    def table_drag_event(self, event):
        if event.buttons() == Qt.LeftButton:
            self.start_drag()

    def add_to_list(self, zip_path):
        # 获取当前时间
        completion_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # 提取文件名称
        file_name = os.path.basename(zip_path)

        # 在表格中添加行
        row_position = self.table_widget.rowCount()
        self.table_widget.insertRow(row_position)

        # 设置文件名称和完成时间
        self.table_widget.setItem(row_position, 0, QTableWidgetItem(file_name))
        self.table_widget.setItem(row_position, 1, QTableWidgetItem(completion_time))

        self.table_widget.setColumnWidth(0, 370)  # 文件名列宽度（可根据需求调整）
        self.table_widget.setColumnWidth(1, 130)  # 完成时间列宽度

        self.table_widget.setDragEnabled(True)
        self.table_widget.setAcceptDrops(True)
        self.table_widget.setDefaultDropAction(Qt.CopyAction)

        self.table_widget.mouseMoveEvent = self.table_drag_event

        # 添加到历史记录
        self.history.append(f"{file_name}|{completion_time}")
        self.save_history()

    def set_cache_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择缓存路径")
        if path:
            self.cache_path = path
            self.save_config()

    def load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_file):
            self.config.read(self.config_file)
            self.cache_path = self.config.get("Settings", "CachePath", fallback="")
            self.window_width = int(self.config.get("Settings", "WindowWidth", fallback=self.default_width))
            self.window_height = int(self.config.get("Settings", "WindowHeight", fallback=self.default_height))
        else:
            self.cache_path = ""
            self.window_width = self.default_width
            self.window_height = self.default_height

    def save_config(self):
        """保存配置文件"""
        self.config["Settings"] = {
            "CachePath": self.cache_path,
            "WindowWidth": str(self.width()),
            "WindowHeight": str(self.height())
        }
        with open(self.config_file, "w") as configfile:
            self.config.write(configfile)

    def load_history(self):
        """加载历史记录"""
        if os.path.exists(self.history_file):
            self.config.read(self.history_file)
            self.history = self.config.get("History", "Paths", fallback="").splitlines()
            for entry in self.history:
                if entry.strip():
                    file_name, completion_time = entry.split('|')
                    row_position = self.table_widget.rowCount()
                    self.table_widget.insertRow(row_position)

                    # 设置文件名称和完成时间
                    self.table_widget.setItem(row_position, 0, QTableWidgetItem(file_name))
                    self.table_widget.setItem(row_position, 1, QTableWidgetItem(completion_time))
                    # # 进一步微调
                    self.table_widget.setColumnWidth(0, 370)  # 文件名列宽度（可根据需求调整）
                    self.table_widget.setColumnWidth(1,  130)  # 完成时间列宽度
            # 确保加载的历史记录支持拖拽
            self.table_widget.setDragEnabled(True)
            self.table_widget.setDefaultDropAction(Qt.CopyAction)
            self.table_widget.mouseMoveEvent = self.table_drag_event



    def save_history(self):
        """保存历史记录"""
        entries = [f"{self.table_widget.item(row, 0).text()}|{self.table_widget.item(row, 1).text()}"
                   for row in range(self.table_widget.rowCount())]
        self.config["History"] = {"Paths": "\n".join(entries)}
        with open(self.history_file, "w") as historyfile:
            self.config.write(historyfile)

    def closeEvent(self, event):
        """关闭窗口时保存配置"""
        self.save_config()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
