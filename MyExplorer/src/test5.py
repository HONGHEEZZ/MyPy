import os, sys

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

if __name__ == '__main__' :

    app = QApplication( sys.argv )

    treeView = QTreeView()
    treeView.setSortingEnabled( True )
    treeView.setObjectName("treeView")

    fsm = QFileSystemModel()
    fsm.setRootPath( 'C:\My Stuff\Movies' )

    def selectZeroZero( path ) :
        if fsm.rowCount( fsm.index( path ) ) :
            treeView.setCurrentIndex( fsm.index( 0, 0, fsm.index( path ) ) )

    fsm.directoryLoaded.connect( selectZeroZero )

    treeView.setModel( fsm )
    treeView.setRootIndex( fsm.index( 'C:\My Stuff\Movies' ) )

    treeView.setHeaderHidden( True )
    treeView.hideColumn( 1 )
    treeView.hideColumn( 2 )
    treeView.hideColumn( 3 )

    treeView.show()

    sys.exit( app.exec_() )