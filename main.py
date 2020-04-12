import math
from PySide2 import QtCore, QtGui, QtWidgets
import compute


class EllipseWidget(QtWidgets.QWidget):
    update_position = QtCore.Signal(object)
    update_settings = QtCore.Signal()

    def __init__(self, parent=None):
        super(EllipseWidget, self).__init__(parent)

        self.circumference = 20
        self.setMouseTracking(True)

        self.reset()

    def reset(self):
        self.dragging = None
        self.foci = [(-2.5, 0), (2.5, 0)]
        self.boundary = None
        self.compute_ellipse()

    def regular(self, nvertices):
        self.dragging = None
        x = 2 * math.pi / nvertices
        self.foci = [
            (3 * math.cos(x * i), 3 * math.sin(x * i)) for i in range(nvertices)
        ]

        self.circumference = nvertices * 4
        self.update_settings.emit()

        self.boundary = None
        self.compute_ellipse()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            coords = self.pos2p(event.pos())
            for index, p in enumerate(self.foci):
                if compute.dist2((p[0] - coords[0], p[1] - coords[1])) < 0.3:
                    self.dragging = index
                    self.update()
                    return True
        return super(EllipseWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        location = self.pos2p(event.pos())
        self.update_position.emit(location)
        if self.dragging != None:
            new_foci = location
            self.foci[self.dragging] = new_foci
            self.update()
            self.compute_ellipse()
        return super(EllipseWidget, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            new_foci = self.pos2p(event.pos())
            if self.dragging != None:
                self.foci[self.dragging] = new_foci
                self.dragging = None
            else:
                self.foci.append(new_foci)
            self.update()
            self.compute_ellipse()
        if event.button() == QtCore.Qt.RightButton:
            coords = self.pos2p(event.pos())
            for index, p in enumerate(self.foci):
                if compute.dist2((p[0] - coords[0], p[1] - coords[1])) < 0.3:
                    del self.foci[index]
                    self.update()
                    self.compute_ellipse()
                    return True
        return super(EllipseWidget, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.compute_ellipse()

    def compute_ellipse(self):
        cs1 = self.pos2p(self.rect().topLeft())
        cs2 = self.pos2p(self.rect().bottomRight())
        self.boundary = compute.compute_boundary(
            self.foci, self.circumference, cs1, cs2
        )
        self.update()

    def pos2p(self, pos):
        center = self.rect().center()
        x, y = pos.x(), pos.y()
        granularity = compute.GRANULARITY
        return (
            (pos.x() - center.x()) / granularity,
            (pos.y() - center.y()) / granularity,
        )

    def p2pixel(self, pnt):
        granularity = compute.GRANULARITY
        center = self.rect().center()
        granularity = compute.GRANULARITY
        pix = (pnt[0] * granularity + center.x(), pnt[1] * granularity + center.y())
        return (int(pix[0]), int(pix[1]))

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        radius = 3
        for f in self.foci:
            x, y = self.p2pixel(f)
            qp.setBrush(QtGui.QBrush("blue"))
            qp.drawEllipse(x - radius, y - radius, 2 * radius, 2 * radius)
        if self.boundary != None:
            qp.setPen(QtGui.QPen("blue"))
            for index in range(len(self.boundary)):
                p1 = self.p2pixel(self.boundary[index - 1])
                p2 = self.p2pixel(self.boundary[index])
                qp.drawLine(QtCore.QPoint(*p1), QtCore.QPoint(*p2))
            # for f in self.boundary:
            #    qp.drawPoint(*self.p2pixel(f))
        if len(self.foci) > 0 and True:
            xsum = sum([x for x, _ in self.foci])
            ysum = sum([y for _, y in self.foci])
            x = xsum / len(self.foci)
            y = ysum / len(self.foci)
            x, y = self.p2pixel((x, y))
            qp.setPen(QtGui.QPen("maroon"))
            qp.drawEllipse(x - radius, y - radius, 2 * radius, 2 * radius)
        if len(self.foci) > 0 and True:

            def line(ep1, ep2):
                ep1 = self.p2pixel(ep1)
                ep2 = self.p2pixel(ep2)
                qp.drawLine(ep1[0], ep1[1], ep2[0], ep2[1])

            x, y = compute.foci_centroid(self.foci, line)
            x, y = self.p2pixel((x, y))
            qp.setPen(QtGui.QPen("green"))
            qp.drawEllipse(x - radius, y - radius, 2 * radius, 2 * radius)
        qp.end()


class EllipseStudio(QtWidgets.QMainWindow):
    MANUAL = """\
Left click -- place new foci
Right click -- remove foci
Left drag -- move foci"""

    def __init__(self, parent=None):
        super(EllipseStudio, self).__init__(parent)

        self.wid = QtWidgets.QWidget()
        self.layout = QtWidgets.QVBoxLayout(self.wid)

        self.mbar = self.menuBar()
        filemenu = self.mbar.addMenu("&File")
        filemenu.addAction("&Reset").triggered.connect(lambda: self.ell_wid.reset())
        filemenu.addAction("&Close").triggered.connect(lambda: self.close())

        ellipsemenu = self.mbar.addMenu("&Ellipse")
        ellipsemenu.addAction("Regular: &1 Foci").triggered.connect(
            lambda: self.ell_wid.regular(1)
        )
        ellipsemenu.addAction("Regular: &2 Foci").triggered.connect(
            lambda: self.ell_wid.regular(2)
        )
        ellipsemenu.addAction("Regular: &3 Foci").triggered.connect(
            lambda: self.ell_wid.regular(3)
        )
        ellipsemenu.addAction("Regular: &4 Foci").triggered.connect(
            lambda: self.ell_wid.regular(4)
        )
        ellipsemenu.addAction("Regular: &5 Foci").triggered.connect(
            lambda: self.ell_wid.regular(5)
        )

        self.label = QtWidgets.QLabel(self.MANUAL)
        self.circ_edit = QtWidgets.QLineEdit()

        self.ell_wid = EllipseWidget()
        self.pos_label = QtWidgets.QLabel("location")
        self.ell_wid.update_position.connect(self.show_location)
        self.ell_wid.update_settings.connect(self.upsettings)

        self.header = QtWidgets.QHBoxLayout()
        s1 = QtWidgets.QVBoxLayout()

        s1.addWidget(self.label)
        s1.addWidget(self.circ_edit)

        self.header.addLayout(s1)

        self.layout.addLayout(self.header)
        self.layout.addWidget(self.ell_wid, 30)
        self.layout.addWidget(self.pos_label)

        self.setCentralWidget(self.wid)

        self.circ_edit.setText(str(self.ell_wid.circumference))

        self.circ_edit.editingFinished.connect(self.recirc)

    def upsettings(self):
        self.circ_edit.setText(str(self.ell_wid.circumference))

    def recirc(self):
        self.ell_wid.circumference = float(self.circ_edit.text())
        self.ell_wid.compute_ellipse()

    def show_location(self, location):
        self.pos_label.setText("Location:  {}".format(location))


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    w = EllipseStudio()
    w.resize(600, 500)
    w.show()
    app.exec_()
