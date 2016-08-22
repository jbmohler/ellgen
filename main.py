from PySide import QtCore, QtGui
import compute

class EllipseWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(EllipseWidget, self).__init__(parent)

        self.circumference = 20

        self.dragging = None
        self.foci = []
        self.boundary = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            coords = self.pos2p(event.pos())
            for index, p in enumerate(self.foci):
                if compute.dist2((p[0]-coords[0], p[1]-coords[1])) < 0.3:
                    self.dragging = index
                    self.update()
                    return True
        return super(EllipseWidget, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging != None:
            new_foci = self.pos2p(event.pos())
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
                if compute.dist2((p[0]-coords[0], p[1]-coords[1])) < 0.3:
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
        self.boundary = compute.compute_boundary(self.foci, self.circumference, cs1, cs2)
        self.update()

    def pos2p(self, pos):
        center = self.rect().center()
        x, y = pos.x(), pos.y()
        granularity = compute.GRANULARITY
        return ((pos.x()-center.x())/granularity, (pos.y()-center.y())/granularity)

    def p2pixel(self, pnt):
        granularity = compute.GRANULARITY
        center = self.rect().center()
        granularity = compute.GRANULARITY
        pix = (pnt[0]*granularity+center.x(), pnt[1]*granularity+center.y())
        return (int(pix[0]), int(pix[1]))

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        radius = 3
        for f in self.foci:
            x, y = self.p2pixel(f)
            qp.setBrush(QtGui.QBrush('blue'))
            qp.drawEllipse(x-radius, y-radius, 2*radius, 2*radius)
        if self.boundary != None:
            qp.setPen(QtGui.QPen('blue'))
            for index in range(len(self.boundary)):
                p1 = self.p2pixel(self.boundary[index-1])
                p2 = self.p2pixel(self.boundary[index])
                qp.drawLine(QtCore.QPoint(*p1), QtCore.QPoint(*p2))
            #for f in self.boundary:
            #    qp.drawPoint(*self.p2pixel(f))
        if len(self.foci) > 0:
            xsum = sum([x for x, _ in self.foci])
            ysum = sum([y for _, y in self.foci])
            x = xsum / len(self.foci)
            y = ysum / len(self.foci)
            x, y = self.p2pixel((x, y))
            qp.setPen(QtGui.QPen('maroon'))
            qp.drawEllipse(x-radius, y-radius, 2*radius, 2*radius)

            #x, y = compute.foci_centroid(self.foci)
            #x, y = self.p2pixel((x, y))
            #qp.setPen(QtGui.QPen('green'))
            #qp.drawEllipse(x-radius, y-radius, 2*radius, 2*radius)
        qp.end()

class EllipseStudio(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(EllipseStudio, self).__init__(parent)

        self.wid = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout(self.wid)
        self.circ_edit = QtGui.QLineEdit()
        self.ell_wid = EllipseWidget()
        self.layout.addWidget(self.circ_edit)
        self.layout.addWidget(self.ell_wid)

        self.setCentralWidget(self.wid)

        self.circ_edit.setText(str(self.ell_wid.circumference))

        self.circ_edit.editingFinished.connect(self.recirc)

    def recirc(self):
        self.ell_wid.circumference = int(self.circ_edit.text())
        self.ell_wid.compute_ellipse()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = EllipseStudio()
    w.resize(600, 500)
    w.show()
    app.exec_()
