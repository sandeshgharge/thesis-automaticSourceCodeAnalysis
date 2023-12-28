from PyQt6 import QtCore
from PyQt6.QtCore import QModelIndex, Qt

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if index.isValid():
            if role == Qt.ItemDataRole.DisplayRole: # or Qt.ItemDataRole.EditRole:
                value = self._data.iloc[index.row(), index.column()]
                return str(value)

    def rowCount(self, parent=QModelIndex()):
        return self._data.shape[0]

    def columnCount(self, parent=QModelIndex()):
        return self._data.shape[1]

    def headerData(self, section, orientation, role):
        # section is the index of the column/row.
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return str(self._data.columns[section])

            if orientation == Qt.Orientation.Vertical:
                return str(self._data.index[section])

    # for editing
    def flags(self, index):
        return Qt.ItemFlag.ItemIsSelectable|Qt.ItemFlag.ItemIsEnabled|Qt.ItemFlag.ItemIsEditable

    def setData(self, index, value, role):
        if role == Qt.ItemDataRole.EditRole:
            self._data.iloc[index.row(),index.column()] = value
            return True
        return False
