#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QVBoxLayout, QWidget, QSizePolicy, QPushButton, QLineEdit, QSlider, QLabel
from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QPalette, QColor, QPixmap
from PyQt5.QtGui import QPainter, QBrush, QPen
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import QSize

import math
from galaxy_minimap import yellow_dot_pos, white_dot_pos

class Color(QWidget):
    def __init__(self, color):
        super().__init__()
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(QPalette.Window, QColor(color))
        self.setPalette(p)

class GalaxyMapImage(QPixmap):
    def __init__(self, imfile="mapHD.png"):
        super().__init__(imfile)
        # map image is scaled such that the working region
        # is 1920x1920, starting at (642, 325)
        self._SCALES = (1920, 1920)
        self._OFFSETS = (642, 325)

    @property
    def aspect(self):
        return self.width()/self.height()

    def draw(self, painter, coord, x, y, w, h):
        painter.drawPixmap(x, y, w, h, self, 0, 0, self.width(), self.height())
        self.draw_north_star(painter, coord, x, y, w, h)
        self.draw_marker_connector(painter, coord, x, y, w, h)
        self.draw_marker(painter, coord, x, y, w, h)

    def draw_marker(self, painter, coord, x, y, w, h):
        painter.setPen(QPen(QColor("yellow"),  0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor("yellow"), Qt.SolidPattern))
        cx, cy = yellow_dot_pos(coord)
        cx *= self._SCALES[0]
        cx += self._OFFSETS[0]
        cx *= w/self.width()
        cx += x
        cy *= self._SCALES[1]
        cy += self._OFFSETS[1]
        cy *= h/self.height()
        cy += y
        painter.drawEllipse(QPointF(cx, cy), int(20*w/self.width()), int(20*w/self.width()))

    def draw_north_star(self, painter, coord, x, y, w, h):
        painter.setPen(QPen(QColor("white"), 0, Qt.SolidLine))
        painter.setBrush(QBrush(QColor("white"), Qt.SolidPattern))
        cx, cy = white_dot_pos(coord)
        cx *= self._SCALES[0]
        cx += self._OFFSETS[0]
        cx *= w/self.width()
        cx += x
        cy *= self._SCALES[1]
        cy += self._OFFSETS[1]
        cy *= h/self.height()
        cy += y
        painter.drawEllipse(QPointF(cx, cy), int(25*w/self.width()), int(10*w/self.width()))
        painter.setPen(QPen(QColor("white"), max(1, int(5*w/self.width())), Qt.SolidLine))
        painter.setBrush(QBrush(QColor("white"), Qt.NoBrush))
        painter.drawEllipse(QPointF(cx, cy), int(105*w/self.width()), int(42*w/self.width()))

    def draw_marker_connector(self, painter, coord, x, y, w, h):
        painter.setPen(QPen(QColor("white"), max(1, int(5*w/self.width())), Qt.SolidLine))
        painter.setBrush(QBrush(QColor("white"), Qt.SolidPattern))
        yx, yy = yellow_dot_pos(coord)
        yx *= self._SCALES[0]
        yx += self._OFFSETS[0]
        yx *= w/self.width()
        yx += x
        yy *= self._SCALES[1]
        yy += self._OFFSETS[1]
        yy *= h/self.height()
        yy += y
        wx, wy = white_dot_pos(coord)
        wx *= self._SCALES[0]
        wx += self._OFFSETS[0]
        wx *= w/self.width()
        wx += x
        wy *= self._SCALES[1]
        wy += self._OFFSETS[1]
        wy *= h/self.height()
        wy += y
        painter.drawLine(QPointF(wx, wy), QPointF(yx, yy))

class GalaxyNavigatorCanvas(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.width = None
        self.height = None
        self.adjusted_to_size = (-1, -1)
        self.coord = (0, 0, 0)

        self.map = GalaxyMapImage()

    # https://stackoverflow.com/a/61589941
    def resizeEvent(self, event):
        size = event.size()
        if size == self.adjusted_to_size:
            # Avoid infinite recursion. I suspect Qt does this for you,
            # but it's best to be safe.
            return
        self.adjusted_to_size = size

        full_width = size.width()
        full_height = size.height()
        width = min(full_width, full_height * self.map.aspect)
        height = min(full_height, full_width / self.map.aspect)

        h_margin = round((full_width - width) / 2)
        v_margin = round((full_height - height) / 2)

        self.setContentsMargins(h_margin, v_margin, h_margin, v_margin)

    def paintEvent(self, event):
        margins = self.contentsMargins()
        geometry = self.frameGeometry()
        usable_width = geometry.width() - margins.left() - margins.right()
        usable_height = geometry.height() - margins.top() - margins.bottom()
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        self.map.draw(painter, self.coord, margins.left(), margins.top(), usable_width, usable_height)

class TextboxSlider(QWidget):
    def __init__(self, min, max, update_func=None, label=None, parent=None):
        super().__init__(parent=parent)
        self.update_func = update_func
        self.min = min
        self.max = max
        
        self.layout = QVBoxLayout()

        if label is not None:
            self.label = QLabel(label)
            self.layout.addWidget(self.label)
            self.label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum))
        self.textbox = QLineEdit()
        self.textbox.setValidator(QDoubleValidator(min, max, 2, self))
        self.textbox.returnPressed.connect(self.onReturnPressed)
        self.slider = QSlider(Qt.Orientation(1))
        self.slider.setMinimum(int(self.min*100))
        self.slider.setMaximum(int(self.max*100))
        self.slider.setTickInterval(1)
        self.val = self.slider.value()/100
        self.textbox.setText(f"{self.val:.2f}")
        self.slider.valueChanged.connect(self.onSliderChange)
        self.layout.addWidget(self.textbox)
        self.layout.addWidget(self.slider)

        self.setLayout(self.layout)

    def onSliderChange(self, val):
        self.val = val/100
        self.textbox.setText(f"{self.val:.2f}")
        self.callUpdateFunc()

    def onReturnPressed(self):
        text = self.textbox.text()
        if self.textbox.validator().validate(text, 0)[0] == 2:
            self.val = float(text)
            self.slider.setValue(int(self.val*100))
        self.callUpdateFunc()

    def callUpdateFunc(self):
        if self.update_func is not None:
            self.update_func()

    def setVal(self, val):
        self.val = val
        self.textbox.setText(f"{self.val:.2f}")
        self.slider.setValue(int(self.val*100))
        self.callUpdateFunc()

class PortalCoordinateLabel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        title_text = QLabel("Portal Code:")
        title_text.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.layout.addWidget(title_text)

        self.portal_code = QLabel("000000000000")
        self.portal_code.setAlignment(Qt.AlignVCenter | Qt.AlignHCenter)
        self.layout.addWidget(self.portal_code)

        self.portal_code.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Ignored))
        self.portal_code.setFixedWidth(250)

    def update(self, coord):
        if not self.valid_coord(coord):
            self.portal_code.setText("Invalid Coord")
            self.portal_code.setStyleSheet("QLabel { color : red; font-size: 24pt; }")
            return
        self.portal_code.setStyleSheet("QLabel { color : black; font-size: 24pt; }")
        coord = (int(round(coord[0])), int(round(coord[1])), int(round(coord[2])))
        xxx = coord[0] & 0xfff
        yy = coord[1] & 0xff
        zzz = coord[2] & 0xfff
        self.portal_code.setText(f"1001{yy:02x}{zzz:03x}{xxx:03x}")

    def valid_coord(self, coord):
        if abs(int(round(coord[0]))) > 2047:
            return False
        if abs(int(round(coord[1]))) > 127:
            return False
        if abs(int(round(coord[2]))) > 2047:
            return False
        return True

class GalaxyNavigatorWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowTitle("NMS Galactic Navigator")

        self.canvas = GalaxyNavigatorCanvas(self)

        layout = QHBoxLayout()
        layout.addWidget(self.canvas)
        canvas_size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        canvas_size_policy.setHorizontalStretch(3)

        slider_layout = QVBoxLayout()
        slider_layout_widget = QWidget(parent=self)
        slider_layout_widget.setLayout(slider_layout)
        layout.addWidget(slider_layout_widget)

        self.theta_slider = TextboxSlider(0, 360, label="theta", parent=self, update_func=self.updateMap)
        self.radius_slider = TextboxSlider(0, (2*(400*2047)**2)**0.5, label="r", parent=self, update_func=self.updateMap)
        self.height_slider = TextboxSlider(-400*127, 400*127, label="z", parent=self, update_func=self.updateMap)
        self.portal_code = PortalCoordinateLabel()
        
        self.theta_slider.setVal(0)
        self.radius_slider.setVal(400*2047)
        self.height_slider.setVal(400*127)
        slider_layout.addWidget(self.radius_slider)
        slider_layout.addWidget(self.theta_slider)
        slider_layout.addWidget(self.height_slider)
        slider_layout.addWidget(self.portal_code)

        widget = QWidget(parent=self)
        widget.setLayout(layout)
        self.setCentralWidget(widget)
        self.canvas.setSizePolicy(canvas_size_policy)

        height = 512
        self.setGeometry(0, 0, int(1.4*height*self.canvas.map.aspect), height)

    def updateMap(self):
        theta = math.radians(self.theta_slider.val)
        radius = self.radius_slider.val
        height = self.height_slider.val
        x = radius * math.cos(theta)
        y = height
        z = -radius * math.sin(theta)
        coord = (x/400, y/400, z/400)
        self.canvas.coord = coord
        self.portal_code.update(coord)
        self.canvas.update()

if __name__ == "__main__":
    app = QApplication([])
    window = GalaxyNavigatorWindow()
    window.show()
    sys.exit(app.exec_())
