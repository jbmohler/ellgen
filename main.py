from PySide import QtCore, QtGui
import compute

class EllipseWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(EllipseWidget, self).__init__(parent)

        self.foci = []
        self.boundary = None

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.foci.append(self.pos2p(event.pos()))
            self.update()
        return super(EllipseWidget, self).mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print('computing')
            print(self.foci)
            self.boundary = compute.compute_boundary(self.foci, 20)
            self.update()

    def pos2p(self, pos):
        x, y = pos.x(), pos.y()
        granularity = compute.GRANULARITY
        return (x/granularity - compute.CANVAS_SIZE/2, y/granularity - compute.CANVAS_SIZE/2)

    def p2pixel(self, pnt):
        granularity = compute.GRANULARITY
        x = (pnt[0]+compute.CANVAS_SIZE/2, pnt[1]+compute.CANVAS_SIZE/2)
        return (int(x[0]*granularity), int(x[1]*granularity))

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        for f in self.foci:
            qp.drawPoint(*self.p2pixel(f))
        if self.boundary != None:
            for f in self.boundary:
                qp.drawPoint(*self.p2pixel(f))
        qp.end()

if __name__ == '__main__':
    app = QtGui.QApplication([])
    w = QtGui.QMainWindow()
    w.setCentralWidget(EllipseWidget())
    w.show()
    app.exec_()
