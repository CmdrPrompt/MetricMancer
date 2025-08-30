import unittest
from src.report.root_info import RootInfo
from src.report.file_info import FileInfo

class TestRootInfo(unittest.TestCase):
    def test_root_info_initialization(self):
        file1 = FileInfo(path='file1.py', complexity=10.0)
        file2 = FileInfo(path='file2.py', complexity=20.0)
        
        root_info = RootInfo(path='root1', average=15.0, files=[file1, file2])

        self.assertEqual(root_info.path, 'root1')
        self.assertEqual(root_info.average, 15.0)
        self.assertEqual(len(root_info.files), 2)
        self.assertEqual(root_info.files[0].path, 'file1.py')
        self.assertEqual(root_info.files[1].path, 'file2.py')

if __name__ == '__main__':
    unittest.main()