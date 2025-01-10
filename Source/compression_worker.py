from PyQt5.QtCore import QThread, pyqtSignal
import os
import zipfile

class CompressionWorker(QThread):
    progress = pyqtSignal(int)
    completed = pyqtSignal(str)

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
