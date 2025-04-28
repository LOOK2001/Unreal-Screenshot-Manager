import os
import time
import glob
import json
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
        self.icon_size_changed()

    def create_widgets(self):
        layout = QtWidgets.QHBoxLayout(self)

        self.tree_widget = QTreeWidget(self)
        self.tree_widget.setMaximumSize(150, 600)
        self.tree_widget.setMinimumSize(80, 580)
        self.tree_widget.header().hide()
        # Create a QDockWidget
        self.tree_dock_widget = QtWidgets.QDockWidget("Collections", self)
        self.tree_dock_widget.setWidget(self.tree_widget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.tree_dock_widget)
        #layout.addWidget(self.tree_dock_widget, stretch=1)
        
        self.list_widget = QtWidgets.QListWidget(self)
        self.list_widget.setViewMode(QtWidgets.QListView.IconMode)
        self.list_widget.setMinimumSize(300, 600)
        # Create a QDockWidget
        self.list_dock_widget = QtWidgets.QDockWidget("Screenshots", self)
        self.list_dock_widget.setWidget(self.list_widget)
        self.addDockWidget(QtCore.Qt.TopDockWidgetArea, self.list_dock_widget)
        #layout.addWidget(self.list_dock_widget, stretch=2)

        self.icon_size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal, self)
        self.icon_size_slider.setMinimum(32)
        self.icon_size_slider.setMaximum(1024)
        self.icon_size_slider.setValue(64)
        self.icon_size_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        layout.addWidget(self.icon_size_slider)

        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def init_widgets(self):
        self.tree_widget.clicked.connect(self.on_click)
        self.icon_size_slider.valueChanged.connect(self.icon_size_changed)
        
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

    def icon_size_changed(self):
        value = self.icon_size_slider.value()
        self.list_widget.setIconSize(QtCore.QSize(value, int(value * 0.5625)))
        self.list_widget.setGridSize(QtCore.QSize(value + 4, int(value * 0.5625) + 16))
                
    def populate_angle_images(self, item):
        print(item)
        print(item.text(0))
        self.list_widget.clear()

        #file_path = f'{SCREENSHOT_PATH}/{item.parent().text(0)}/{item.text(0).rstrip()}'
        
        images = self.get_all_images(item)
        for image_path in images:
            if image_path.endswith('.png') or image_path.endswith('jpg'):
                base_name = os.path.basename(image_path)
                base_name = os.path.splitext(base_name)[0]
                new_item = QtWidgets.QListWidgetItem()
                new_item.setIcon(QtGui.QIcon(image_path))
                new_item.setText(base_name)
                new_item.setData(QtCore.Qt.UserRole, os.path.join(image_path))
                self.list_widget.addItem(new_item)

    
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
        images = glob.glob(f'{path}/*')
        for img in images:
            all_images.append(img.replace('\\', '/'))
        return all_images
    
    def populate_collection_images(self, item):
        self.list_widget.clear()
        extensions = ['.png', '.jpg', '.jpeg']

        all_leaf_items = self.get_all_leaf_items(item)
        if all_leaf_items is None:
            return
        
        for child in all_leaf_items:
            imgs = self.get_all_images(child)
            for file_path in imgs:
                filename, file_extension = os.path.splitext(file_path)
                if file_extension not in extensions:
                    continue
                img_name = os.path.basename(filename)
                img = QtGui.QImage(file_path)
                pixmap = QtGui.QPixmap.fromImage(img)
                icon = QtGui.QIcon(pixmap)
                item = QtWidgets.QListWidgetItem()
                item.setIcon(icon)
                item.setText(img_name)
                self.list_widget.addItem(item)
                
        value = 150
        #self.list_widget.setIconSize(QtCore.QSize(150, 150))
        self.list_widget.setIconSize(QtCore.QSize(value, int(value * 0.5625)))
        self.list_widget.setGridSize(QtCore.QSize(value + 4, int(value * 0.5625) + 16))
        
        
    def get_all_leaf_items(self, item):
        leaf_items = []
        for i in range(item.childCount()):
            child = item.child(i)
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

                collection_data = get_angle_info(os.path.join(SCREENSHOT_PATH, dir).replace('\\', '/'))
                for data in collection_data:
                    child_item = QtWidgets.QTreeWidgetItem()
                    child_item.setText(0, data[0])
                    child_item.setData(0, QtCore.Qt.UserRole, data)
                    parent_item.addChild(child_item)
                
    def add_collection(self):
        text, ok = QtWidgets.QInputDialog.getText(self, 'New Item', 'Please Name the New Collections:')
        if ok:
            collection_path = os.path.join(SCREENSHOT_PATH, text).replace(os.sep, '/')
            if not os.path.exists(collection_path):
                os.makedirs(collection_path)
                self.populate_collection_view()
            
    def collections_context_menu(self):
        item = self.tree_widget.currentItem()
        menu = QtWidgets.QMenu(self)
        
        if item:
            if item.data(0, QtCore.Qt.UserRole) is not None:
                menu.addAction('Go To Angle', partial(self.set_viewport_transform, item.data(0, QtCore.Qt.UserRole)))
                menu.addAction('Capture Angle', partial(self.capture_angle, item))
            else:
                menu.addAction('Add Camera Angle...', partial(self.add_camera_angle, item))

        menu.addSeparator()
        menu.addAction('Add Collection...', self.add_collection)
        menu.addAction('Refresh', self.refresh)
        menu.exec_(QtGui.QCursor.pos())

    def refresh(self):
        item = self.tree_widget.currentItem()
        if item is not None:
            self.populate_angle_images(item)

    def add_camera_angle(self, item: QtWidgets.QTreeWidgetItem):
        name, ok = QtWidgets.QInputDialog.getText(self, 'New Item', 'New Camera Angle Name:' )
        if ok:
            path = f'{SCREENSHOT_PATH}/{item.text(0).rstrip()}'
            camera_orientation = add_camera_angle(path, name)
            child_item = QtWidgets.QTreeWidgetItem()
            child_item.setText(0, name)
            child_item.setData(0, QtCore.Qt.UserRole, camera_orientation)
            item.addChild(child_item)
            self.capture_angle(child_item)
            self.populate_collection_view()

    def capture_angle(self, item):
        name = item.text(0).rstrip()
        transform = item.data(0, QtCore.Qt.UserRole)
        path = f'{SCREENSHOT_PATH}/{item.parent().text(0).rstrip()}/{name}'
        if not os.path.exists(path):
            os.makedirs(path)
        num = len(os.listdir(path)) + 1
        if num < 100:
            if num < 10:
                num = f'00{num}'
            else:
                num = f'0{num}'
        name += f'-{num}'
        self.set_viewport_transform(transform)
        take_screenshot(path, name)
        self.populate_angle_images(item)

    def set_viewport_transform(self, transform):
        print("transform:", transform)
        location = transform[1]
        rotation = transform[2]
        #location = unreal.Vector(location[0], location[1], location[2])
        #rotation = unreal.Rotator(rotation[0], rotation[1], rotation[2])
        # Apply new position and rotation

        world = unreal.UnrealEditorSubsystem().get_editor_world()
        actor = unreal.EditorActorSubsystem().get_actor_reference("/Script/Engine.CameraActor'/Game/Map/Tank.Tank:PersistentLevel.CameraActor_UAID_A4AE1229F2DB595602_1222694975'")
        unreal.UnrealEditorSubsystem().set_level_viewport_camera_info(location, rotation)

        # actor_subsystem = unreal.EditorActorSubsystem()
        # all_actors = actor_subsystem.get_all_level_actors()
        # camera_actors = [actor for actor in all_actors if isinstance(actor, unreal.CameraActor) or isinstance(actor, unreal.CineCameraActor)]
        # print("rotation:", rotation)
        # camera_actors[0].set_actor_location_and_rotation(location, rotation, False, True)

        
def add_camera_angle(path, name):
    file_content = get_angle_info(path) or []
    #viewport_client = unreal.EditorLevelLibrary.get_level_viewport_camera_info()
    viewport_client = unreal.UnrealEditorSubsystem().get_level_viewport_camera_info()

    cam_location = [viewport_client[0].x, viewport_client[0].y, viewport_client[0].z]
    cam_rotation = [viewport_client[1].pitch, viewport_client[1].yaw, viewport_client[1].roll]
    print("cam_rotation1:", viewport_client)
    print("cam_rotation2:", cam_rotation)
    file_content = [name, cam_location, cam_rotation]

    json_file = f'{path}/cameraAngles.json'

    # Save camera angles into json file
    data = []
    if not os.path.exists(json_file):
        with open(json_file, "w") as file:
            # Initialize with an empty list
            json.dump(data, file)

    with open(json_file, "r") as file:
        data = json.load(file)
    data.append(file_content)

    with open(json_file, 'w') as file:
        json.dump(data, file, indent=4)
    return file_content


def get_angle_info(path):
    file_path = f'{path}/cameraAngles.json'.replace(os.sep, '/')
    file_content = []

    if not os.path.exists(file_path):
        return file_content

    with open(file_path, 'r') as file:
        file_content = json.load(file)
    return file_content

            
def take_screenshot(output_path, name):
    """
    Captures a screenshot in Unreal Engine.
    
    :param output_path: Full path where the screenshot will be saved (e.g., "C:/Path/To/Screenshot.png").
    """
    output_path = f'{output_path}/{name}.jpg'
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
