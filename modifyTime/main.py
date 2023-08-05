'''
Description: 文件夹只有创建时间
Autor: dulun
Date: 2023-07-25 17:35:48
LastEditors: dulun
LastEditTime: 2023-07-30 21:02:30
'''
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QFileDialog, QComboBox, QLabel, QLineEdit,QTableWidget,QCheckBox, QMessageBox, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from PyQt5.QtCore import pyqtSignal
import time, win32file, win32con
import pywintypes
import enum
import json

class FileDropArea(QLabel):
    # 定义自定义信号
    drop_event_signal = pyqtSignal(list)

    def __init__(self):
        super().__init__()

        self.setText("将文件/文件夹拖拽到此处")
        self.setAlignment(Qt.AlignCenter)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = event.mimeData().urls()
        file_paths = [url.toLocalFile() for url in files]
        self.setText("\n".join(file_paths))

        # 发射自定义信号，并将 file_paths 作为参数传递
        self.drop_event_signal.emit(file_paths)

class FileTimeModifier(QMainWindow):
    def __init__(self):
        super().__init__()
        self.memory_setting = self.getMemory()
        self.mode = self.memory_setting['mode']
        self.modify_pros = self.memory_setting['modify']
        self.modify_list = []
        self.unit2digit = {'天':0, "时":1, "分":2, "秒":3}
        self.initUI()
        # 连接 FileDropArea 类的自定义信号与相应的槽函数
        self.drop_area.drop_event_signal.connect(self.handle_drop_event)

    def getMemory(self):
        return json.load(open('./memory.json', 'r', encoding='utf-8'))

    def initUI(self):
        self.setWindowTitle('文件时间修改')
        self.setGeometry(300, 200, 400, 550)
        # self.setGeometry(300, 200, 800, 950)
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        # Create a grid layout
        layout = QGridLayout()

        # layout = QHBoxLayout()
        # layout.setSpacing(5)  # 设置间距为5个像素

        label = QLabel("选用模式", self)
        layout.addWidget(label, 0,0)
        self.combo_box = QComboBox()
        self.combo_box.addItem("时间整体延后")
        self.combo_box.addItem("时间整体调前")
        self.combo_box.setCurrentIndex(0 if self.mode==1 else 1)
        self.combo_box.currentIndexChanged.connect(self.on_combobox_changed)
        layout.addWidget(self.combo_box, 0, 1, 1, 2)

        self.table_widget = QTableWidget(self)
        self.table_widget.setColumnCount(3)
        self.table_widget.setRowCount(7)

        # Set header labels
        header_labels = ["修改项目", "改变量", "单位"]
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        # Add checkboxes for each row
        for row, label in enumerate(["文件创建时间", "文件修改时间", "文件访问时间", '文件夹创建时间', '文件夹修改时间', '文件夹访问时间',"使用总输入框"]):
            checkbox = QCheckBox(label, self)
            checkbox.setChecked(self.modify_pros[label]['valid'])
            self.table_widget.setCellWidget(row, 0, checkbox)

        # Add input boxes for each row
        for row, label in enumerate(["文件创建时间", "文件修改时间", "文件访问时间", "文件夹创建时间", '文件夹修改时间', '文件夹访问时间','使用总输入框']):
            input_box = QLineEdit(self)
            input_box.setText(str(self.modify_pros[label]['num']))
            self.table_widget.setCellWidget(row, 1, input_box)

        # Add combo boxes for each row
        units = ["天", "时", "分", "秒"]
        for row, label in enumerate(["文件创建时间", "文件修改时间", "文件访问时间", "文件夹创建时间", '文件夹修改时间', '文件夹访问时间', '使用总输入框']):
            combo_box = QComboBox(self)
            combo_box.addItems(units)
            combo_box.setCurrentIndex(self.unit2digit[self.modify_pros[label]['unit']])
            self.table_widget.setCellWidget(row, 2, combo_box)
        layout.addWidget(self.table_widget, 1,0,6,3)

        self.file_button = QPushButton("选择文件")
        self.folder_button = QPushButton("选择文件夹")
        self.file_button.clicked.connect(self.show_file_dialog)
        self.folder_button.clicked.connect(self.show_folder_dialog)
        layout.addWidget(self.file_button, 3, 0, 1, 3)
        layout.addWidget(self.folder_button, 4, 0, 1, 3)

        self.drop_area = FileDropArea()
        layout.addWidget(self.drop_area, 5, 0, 1, 3)

        self.modify_button = QPushButton('修改时间', self)
        self.modify_button.clicked.connect(self.modify_time)
        layout.addWidget(self.modify_button, 6, 0, 1, 3)

        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.file_path = ""

    def setFileDropAreaText(self, file_paths):
        self.drop_area.setText("\n".join(file_paths))
    
    def handle_drop_event(self, file_paths):
        # 在这里处理 FileDropArea 类的 dropEvent 发生时的逻辑
        self.modify_list = file_paths
        print("modify_list:", self.modify_list)

    def show_file_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # 弹出多个文件选择对话框
        file_paths, _ = QFileDialog.getOpenFileNames(self, "选择多个文件", "", "All Files (*);;Text Files (*.txt)", options=options)
        self.modify_list = []
        if file_paths:
            print("选择的文件列表：")
            for file_path in file_paths:
                print(file_path)
                self.modify_list.append(file_path)
            self.setFileDropAreaText(self.modify_list)
        else:
            self.setFileDropAreaText(["未选择文件或取消了选择"])

    def show_folder_dialog(self):
        options = QFileDialog.Options()
        folder_name = QFileDialog.getExistingDirectory(self, "选择文件夹", "", options=options)
        self.modify_list = []
        if folder_name:
            self.modify_list.append(folder_name)
            self.setFileDropAreaText(self.modify_list)
        else:
            self.setFileDropAreaText(["未选择文件或取消了选择"])

    def show_file_or_folder_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        # 弹出文件或文件夹选择对话框
        # file_or_folder_path = QFileDialog.getExistingDirectory(self, "选择文件或文件夹", "", options=options)
        file_path, _ = QFileDialog.getOpenFileName(self, "选择文件", "", "All Files (*);;Text Files (*.txt)", options=options)

        if file_path:
            print(f"选择的文件或文件夹：{file_path},{_}")

    def on_combobox_changed(self, index):
        selected_option = self.combo_box.currentText()
        if selected_option == "时间整体延后":
            self.mode = 1
        elif selected_option == "时间整体调前":
            self.mode = -1
    
    def select_file(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_path, _ = QFileDialog.getOpenFileName(self, "Select File", "", "All Files (*)", options=options)

        if file_path:
            self.file_path = file_path

    def adjust_folder_creation_time(folder_path, hours):
        if not os.path.exists(folder_path):
            print("文件夹不存在")
            return

        # 获取当前时间
        current_time = time.time()

        # 计算调整后的时间戳
        adjusted_creation_time = current_time + hours * 3600

        # 转换时间戳为 FILETIME 格式
        filetime = pywintypes.Time(adjusted_creation_time)

        # 打开文件夹并设置文件夹的创建时间
        handle = win32file.CreateFile(
            folder_path,
            win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,  # 添加该参数以支持文件夹操作
            None
        )

        win32file.SetFileTime(handle, filetime, None, None)

        win32file.CloseHandle(handle)

        print(f"成功调整文件夹 '{folder_path}' 的创建时间")
    
    def transfer_time(self, time_str, unit):
        try:
            time_int = float(time_str)  # Try to convert the string to a float
            if unit=="天":
                time_int = time_int * 24 * 60 * 60
            elif unit=='时':
                time_int = time_int * 60 * 60
            elif unit=='分':
                time_int = time_int * 60
            return time_int  # If successful, the string is a valid number
        except ValueError:
            return False 

    def adjust_file_time(self, file_name):
        # Get current timestamps
        file_info = os.stat(file_name)
        creation_time = file_info.st_ctime
        modify_time = file_info.st_mtime
        access_time = file_info.st_atime

        # 打开文件并设置文件的创建时间
        handle = win32file.CreateFile(
            file_name,
            win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_ATTRIBUTE_NORMAL,
            None
        )

        # original_times = win32file.GetFileTime(handle)
        # creation_time =  pywintypes.Time(original_times[0]).value
        # modify_time = pywintypes.Time(original_times[1]).value
        # access_time = pywintypes.Time(original_times[2]).value

        if self.modify_pros['文件创建时间']['valid']:
            print("文件创建时间")
            if self.modify_pros['使用总输入框']['valid']:
                time_int = self.transfer_time(self.modify_pros['使用总输入框']['num'], self.modify_pros['使用总输入框']['unit'])
            else:
                time_int = self.transfer_time(self.modify_pros['文件创建时间']['num'], self.modify_pros['文件创建时间']['unit'])
            creation_time = creation_time + self.mode*time_int
        if self.modify_pros['文件修改时间']['valid']:
            print("文件修改时间。。。")
            if self.modify_pros['使用总输入框']['valid']:
                time_int = self.transfer_time(self.modify_pros['使用总输入框']['num'], self.modify_pros['使用总输入框']['unit'])
            else:
                time_int = self.transfer_time(self.modify_pros['文件修改时间']['num'], self.modify_pros['文件修改时间']['unit'])
            modify_time = modify_time + self.mode*time_int
        if self.modify_pros['文件访问时间']['valid']:
            print("文件访问时间")
            if self.modify_pros['使用总输入框']['valid']:
                time_int = self.transfer_time(self.modify_pros['使用总输入框']['num'], self.modify_pros['使用总输入框']['unit'])
            else:
                time_int = self.transfer_time(self.modify_pros['文件访问时间']['num'], self.modify_pros['文件访问时间']['unit'])
            access_time = access_time + self.mode*time_int
        # 设置文件的时间
        creation_time = pywintypes.Time(creation_time)
        win32file.SetFileTime(handle, CreationTime = creation_time)
        win32file.CloseHandle(handle)
        os.utime(file_name, (access_time, modify_time))
        self.setFileDropAreaText(["文件时间修改完成"])

    def adjust_folder_time(self, file_name):
        file_info = os.stat(file_name)
        creation_time = file_info.st_ctime
        modify_time = file_info.st_mtime
        access_time = file_info.st_atime

        # 打开文件并设置文件的创建时间
        handle = win32file.CreateFile(
            file_name,
            win32con.GENERIC_WRITE,
            win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
            None,
            win32con.OPEN_EXISTING,
            win32con.FILE_FLAG_BACKUP_SEMANTICS,  # 添加该参数以支持文件夹操作
            None
        )

        # original_times = win32file.GetFileTime(handle)
        # creation_time =  pywintypes.Time(original_times[0]).value
        # modify_time = pywintypes.Time(original_times[1]).value
        # access_time = pywintypes.Time(original_times[2]).value

        if self.modify_pros['文件夹创建时间']['valid']:
            print("文件夹创建时间")
            if self.modify_pros['使用总输入框']['valid']:
                time_int = self.transfer_time(self.modify_pros['使用总输入框']['num'], self.modify_pros['使用总输入框']['unit'])
            else:
                time_int = self.transfer_time(self.modify_pros['文件夹创建时间']['num'], self.modify_pros['文件夹创建时间']['unit'])
            creation_time = creation_time + self.mode*time_int
        if self.modify_pros['文件夹修改时间']['valid']:
            print("文件夹修改时间。。。")
            if self.modify_pros['使用总输入框']['valid']:
                time_int = self.transfer_time(self.modify_pros['使用总输入框']['num'], self.modify_pros['使用总输入框']['unit'])
            else:
                time_int = self.transfer_time(self.modify_pros['文件夹修改时间']['num'], self.modify_pros['文件夹修改时间']['unit'])
            modify_time = modify_time + self.mode*time_int
        if self.modify_pros['文件夹访问时间']['valid']:
            print("文件夹访问时间")
            if self.modify_pros['使用总输入框']['valid']:
                time_int = self.transfer_time(self.modify_pros['使用总输入框']['num'], self.modify_pros['使用总输入框']['unit'])
            else:
                time_int = self.transfer_time(self.modify_pros['文件夹访问时间']['num'], self.modify_pros['文件夹访问时间']['unit'])
            access_time = access_time + self.mode*time_int
        # 设置文件的时间
        creation_time = pywintypes.Time(creation_time)
        win32file.SetFileTime(handle, CreationTime = creation_time)
        win32file.CloseHandle(handle)
        os.utime(file_name, (access_time, modify_time))
        self.setFileDropAreaText(["文件夹时间修改完成"])
    # def adjust_folder_time(self, file_name):
    #     file_info = os.stat(file_name)
    #     creation_time = file_info.st_ctime
    #     if self.modify_pros['文件夹创建时间']['valid']:
    #         time_int = self.transfer_time(self.modify_pros['文件夹创建时间']['num'], self.modify_pros['文件夹创建时间']['unit'])
    #         creation_time = creation_time + self.mode*time_int
    #         # 转换时间戳为 FILETIME 格式
    #         filetime = pywintypes.Time(creation_time)

    #         # 打开文件夹并设置文件夹的创建时间
    #         handle = win32file.CreateFile(
    #             file_name,
    #             win32con.GENERIC_WRITE,
    #             win32con.FILE_SHARE_READ | win32con.FILE_SHARE_WRITE,
    #             None,
    #             win32con.OPEN_EXISTING,
    #             win32con.FILE_FLAG_BACKUP_SEMANTICS,  # 添加该参数以支持文件夹操作
    #             None
    #         )

    #         win32file.SetFileTime(handle, filetime, None, None)

    #         win32file.CloseHandle(handle)

    #         self.setFileDropAreaText(["成功调整文件夹的创建时间"])
    
    def update_modify_setting(self):
        if self.combo_box.currentText() == '时间整体调前':
            self.mode = -1
        else:
            self.mode = 1

        item = self.table_widget.cellWidget(0,0)
        if item.isChecked():
            self.modify_pros['文件创建时间']['valid'] = True
            cell_widget = self.table_widget.cellWidget(0, 1)
            self.modify_pros['文件创建时间']['num'] = cell_widget.text()
            cell_widget = self.table_widget.cellWidget(0, 2)
            self.modify_pros['文件创建时间']['unit'] = cell_widget.currentText()
        else:
            self.modify_pros['文件创建时间']['valid'] = False

        item = self.table_widget.cellWidget(1,0)
        if item.isChecked():
            self.modify_pros['文件修改时间']['valid'] = True
            cell_widget = self.table_widget.cellWidget(1, 1)
            self.modify_pros['文件修改时间']['num'] = cell_widget.text()
            cell_widget = self.table_widget.cellWidget(1, 2)
            self.modify_pros['文件修改时间']['unit'] = cell_widget.currentText()
        else:
            self.modify_pros['文件修改时间']['valid'] = False
        
        item = self.table_widget.cellWidget(2,0)
        if item.isChecked():
            self.modify_pros['文件访问时间']['valid'] = True
            cell_widget = self.table_widget.cellWidget(2, 1)
            self.modify_pros['文件访问时间']['num'] = cell_widget.text()
            cell_widget = self.table_widget.cellWidget(2, 2)
            self.modify_pros['文件访问时间']['unit'] = cell_widget.currentText()
        else:
            self.modify_pros['文件访问时间']['valid'] = False
        
        item = self.table_widget.cellWidget(3,0)
        if item.isChecked():
            self.modify_pros['文件夹创建时间']['valid'] = True
            cell_widget = self.table_widget.cellWidget(3, 1)
            self.modify_pros['文件夹创建时间']['num'] = cell_widget.text()
            cell_widget = self.table_widget.cellWidget(3, 2)
            self.modify_pros['文件夹创建时间']['unit'] = cell_widget.currentText()
        else:
            self.modify_pros['文件夹创建时间']['valid'] = False
        
        item = self.table_widget.cellWidget(4,0)
        if item.isChecked():
            self.modify_pros['文件夹修改时间']['valid'] = True
            cell_widget = self.table_widget.cellWidget(4, 1)
            self.modify_pros['文件夹修改时间']['num'] = cell_widget.text()
            cell_widget = self.table_widget.cellWidget(4, 2)
            self.modify_pros['文件夹修改时间']['unit'] = cell_widget.currentText()
        else:
            self.modify_pros['文件夹修改时间']['valid'] = False

        item = self.table_widget.cellWidget(5,0)
        if item.isChecked():
            self.modify_pros['文件夹访问时间']['valid'] = True
            cell_widget = self.table_widget.cellWidget(5, 1)
            self.modify_pros['文件夹访问时间']['num'] = cell_widget.text()
            cell_widget = self.table_widget.cellWidget(5, 2)
            self.modify_pros['文件夹访问时间']['unit'] = cell_widget.currentText()
        else:
            self.modify_pros['文件夹访问时间']['valid'] = False

        item = self.table_widget.cellWidget(6,0)
        if item.isChecked():
            self.modify_pros['使用总输入框']['valid'] = True
            cell_widget = self.table_widget.cellWidget(6, 1)
            self.modify_pros['使用总输入框']['num'] = cell_widget.text()
            cell_widget = self.table_widget.cellWidget(6, 2)
            self.modify_pros['使用总输入框']['unit'] = cell_widget.currentText()
        else:
            self.modify_pros['使用总输入框']['valid'] = False

        self.memory_setting['modify']=self.modify_pros
        self.memory_setting['mode']=self.mode
    
    def is_compressed_file(self, file_path):
        known_compression_formats = ['.zip', '.rar', '.tar.gz']
        # 获取文件的扩展名
        _, file_extension = os.path.splitext(file_path)
        
        # 判断文件扩展名是否在已知的压缩包格式列表中
        if file_extension in known_compression_formats:
            return True
        else:
            return False

    def modify_time(self):
        self.update_modify_setting()
        if len(self.modify_list)!=0:
            tmp = self.modify_list.copy()
            for file_name in self.modify_list:
                if self.is_compressed_file(file_name):
                    continue
                if os.path.isfile(file_name):
                    self.adjust_file_time(file_name)
                elif os.path.isdir(file_name):
                    self.adjust_folder_time(file_name)
                    for name in os.listdir(file_name):
                        file_path = os.path.join(file_name, name)
                        self.modify_list.append(file_path)
                else:
                    self.setFileDropAreaText(["文件不合法"])
            self.modify_list = tmp
        else:
            self.setFileDropAreaText(["请先选择文件/文件夹"])

    def closeEvent(self, event):
        self.update_modify_setting()
        try:
            with open('./memory.json', 'w', encoding='utf-8') as f:
                # print(self.memory_setting)
                json.dump(self.memory_setting, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # 处理保存失败的情况，例如弹出错误对话框
            QMessageBox.critical(self, "Error", "Failed to save memory_setting to momery.json: " + str(e))

        event.accept()
#     datas=[('.\\memory.json', '.')],
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = FileTimeModifier()
    window.show()
    sys.exit(app.exec_())
