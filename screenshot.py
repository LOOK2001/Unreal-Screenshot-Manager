import os
import sys
import glob
#sys.path.append(r'C:/ndibin/python37/Lib/site-packages')
from PySide6 import QtWidgets, QtCore, QtGui
from PySide6.QtWidgets import QTreeWidget, QTreeWidgetItem
import unreal
import threading
from functools import partial


SCREENSHOT_PATH = "C:/Xicheng/Work/software/Epic Games/Unreal Projects/Xicheng/Screenshots"


class MainWindow(QtWidgets.QMainWindow):

    winName = 'Screenshot Manager'

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle(self.winName)
        
        self.worker_thread = None

        if not os.path.exists(SCREENSHOT_PATH):
            os.makedirs(SCREENSHOT_PATH)

        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        self.create_widgets()
        self.init_widgets()
        #self.initToolBar()
        
        #output_path = "C:/Xicheng/Work/software/Epic Games/Unreal Projects/Xicheng/Screenshots/screenshot.png"
        #take_screenshot(output_path)

        self.populate_collection_view()

    def create_widgets(self):
        layout = QtWidgets.QHBoxLayout(self)

        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setMaximumSize(150, 400)
        self.tree_widget.setMinimumSize(50, 380)
        self.tree_widget.header().hide()
        # Create a QDockWidget
        self.tree_dock_widget = QtWidgets.QDockWidget("Collections", self)
        self.tree_dock_widget.setWidget(self.tree_widget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.tree_dock_widget)
        #layout.addWidget(self.tree_dock_widget, stretch=1)
        
        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setMinimumSize(150, 400)
        self.list_widget.setIconSize(QtCore.QSize(500, int(50 * 0.5625)))
        self.list_widget.setGridSize(QtCore.QSize(500 + 4, int(50 * 0.5625) + 16))
        # Create a QDockWidget
        self.list_dock_widget = QtWidgets.QDockWidget("Screenshots", self)
        self.list_dock_widget.setWidget(self.list_widget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.list_dock_widget)
        #layout.addWidget(self.list_dock_widget, stretch=2)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def init_widgets(self):
        self.tree_widget.clicked.connect(self.on_click)
        
        self.tree_widget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tree_widget.customContextMenuRequested.connect(self.collections_context_menu)
        
    def stop_worker_threads(self):
        """
        Stops all worker threads.
        """
        self.list_widget.clear()
        if self.worker_thread and self.worker_thread.is_alive():
            self.worker_thread.stop()
            self.worker_thread.wait()
        
    def on_click(self):
        """
        Called when an item in the tree view is clicked.
        """
        #self.stop_worker_threads()
        self.list_widget.clear()
        
        item = self.tree_widget.currentItem()
        if item is not None:
            if item.data(0, QtCore.Qt.UserRole) is not None:
                self.populate_angle_images(item)
                #self.worker_thread = threading.Thread(target=self.populate_angle_images, args=(item))
                #self.worker_thread.start()
            else:
                self.populate_collection_images(item)
                #self.worker_thread = threading.Thread(target=self.populate_collection_images, args=(item))
                #self.worker_thread.start()
                
    def populate_angle_images(self, item):
        pass
    
    def get_item_path(self, item):
        path = []
        while item is not None:
            path.insert(0, item.text(0))
            item = item.parent()
        path = '/'.join(path)
        return path
    
    def get_all_images(self, item):
        all_images = []
        path = os.path.join(SCREENSHOT_PATH, self.get_item_path(item)).replace('\\', '/')
        print('path:', path)
        images = glob.glob(f'{path}/*')
        for img in images:
            all_images.append(img.replace('\\', '/'))
        print('images:', images)
        return all_images
    
    def populate_collection_images(self, item):
        self.list_widget.clear()
        extensions = ['.png', '.jpg', '.jpeg']

        all_leaf_items = self.get_all_leaf_items(item)
        print('all_leaf_items:', all_leaf_items)
        if all_leaf_items is None:
            return
        
        for child in all_leaf_items:
            imgs = self.get_all_images(child)
            print('imgs:', imgs)
            for file_path in imgs:
                print('file_path:', file_path)
                img_name = file_path.split('/')[-1]
                img = QtGui.QImage(file_path)
                pixmap = QtGui.QPixmap.fromImage(img)
                icon = QtGui.QIcon(pixmap)
                item = QtWidgets.QListWidgetItem()
                item.setIcon(icon)
                item.setText(img_name)
                print('add item:', item)
                self.list_widget.addItem(item)
                
        value = 150
        #self.list_widget.setIconSize(QtCore.QSize(150, 150))
        self.list_widget.setIconSize(QtCore.QSize(value, int(value * 0.5625)))
        self.list_widget.setGridSize(QtCore.QSize(value + 4, int(value * 0.5625) + 16))
        
        
    def get_all_leaf_items(self, item):
        leaf_items = []
        print('item:', item.childCount())
        for i in range(item.childCount()):
            child = item.child(i)
            print('child:', child)
            if child.childCount() == 0:
                leaf_items.append(child)
            else:
                leaf_items.extend(self.get_all_leaf_items(child))
        return leaf_items
    
    def populate_collection_view(self, filter=''):
        self.tree_widget.clear()
        dirs = os.listdir(SCREENSHOT_PATH)
        dirs = [d.split('/')[-1] for d in dirs]
        dirs.sort()
        
        for dir in dirs:
            if filter.lower() in dir.lower():
                parent_item = QtWidgets.QTreeWidgetItem()
                parent_item.setText(0, dir)
                self.tree_widget.addTopLevelItem(parent_item)
                
                children_dirs = os.listdir(os.path.join(SCREENSHOT_PATH, dir).replace('\\', '/'))
                children_names = [d.split('/')[-1] for d in children_dirs]
                
                for child in children_names:
                    child_item = QtWidgets.QTreeWidgetItem()
                    child_item.setText(0, child)
                    parent_item.addChild(child_item)
                
    def add_collection(self):
        text = "test"
        new_path = os.path.join(SCREENSHOT_PATH, text).replace(os.sep, '/')
        if 
            
    def collections_context_menu(self):
        item = self.tree_widget.currentItem()
        menu = QtWidgets.QMenu(self)
        
        if item is not None:
            if item.data(0, QtCore.Qt.UserRole) is not None:
                menu.addAction('Go To Angle', partial(self.go_to_angle, item.data(0, QtCore.Qt.UserRole)))

        menu.addSeparator()
        menu.addAction('Add Collection...', self.add_collection)
        menu.addAction('Refresh', self.populate_collection_view)
        menu.exec_(QtGui.QCursor.pos())
        
            
def take_screenshot(output_path):
    """
    Captures a screenshot in Unreal Engine.
    
    :param output_path: Full path where the screenshot will be saved (e.g., "C:/Path/To/Screenshot.png").
    """
    # Use the high-resolution screenshot function
    screenshot_settings = unreal.AutomationLibrary.take_high_res_screenshot(
        1920,
        1080,
        filename=output_path
    )

    if screenshot_settings:
        unreal.log(f"Screenshot saved to {output_path}")
    else:
        unreal.log_error("Failed to take a screenshot")


def main():
    # 1. SETUP - this step can automatically run on editor startup when added to your init_unreal.py
    import unreal_qt
    unreal_qt.setup()  

    # 2. CREATE WIDGET - create your qt widget
    # every widget you make after setup won't block the editor & have unreal styling
    w = MainWindow()

    # 3. WRAP WIDGET - (optional) manage garbage collection, add darkbar, stay on top
    unreal_qt.wrap(w)

    # 4. SHOW WIDGET - if using stay on top this needs to run after the wrap stage
    w.show()
