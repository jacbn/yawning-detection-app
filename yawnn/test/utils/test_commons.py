import unittest
from yawnnlib.utils import commons
from yawnnlib.lstm import eimuLSTM

import numpy as np

class TestCommons(unittest.TestCase):
    def test_directoryToModelData(self):
        commons.YAWN_TIME = 2
        model = eimuLSTM.EimuLSTMInput(sessionGap=1)
        (x1, y1), (x2, y2) = model.fromDirectory(f"{commons.PROJECT_ROOT}/test/test_data/directory_test", equalPositiveAndNegative=False)
        self.assertEqual(x1.shape[0] + x2.shape[0], 15)
        self.assertEqual(y1.shape[0] + y2.shape[0], 15)
        # 73 + 64 + 66 + 3 = 205 sensor readings in the 4 files.
        # this splits into 10 + 1 + 3 + 1 = 15 sets of 32Hz * commons.YAWN_TIME
        
        self.assertEqual(x1.shape[1:], (32 * commons.YAWN_TIME, 6))
        self.assertEqual(x2.shape[1:], (32 * commons.YAWN_TIME, 6))
        self.assertEqual(y1.shape[1], 1)
        self.assertEqual(y2.shape[1], 1)

    def test_mapToDirectory(self):
        f = lambda x, y, z: x
        fileNames = commons.mapToDirectory(f, f"{commons.PROJECT_ROOT}/test/test_data/directory_test")
        
        # test all returned files are in the directory
        self.assertTrue(sum([f'{commons.PROJECT_ROOT}/test/test_data/directory_test' not in x for x in fileNames]) == 0)
        
        strippedFileNames = [x.replace(f"{commons.PROJECT_ROOT}/test/test_data/directory_test/", "") for x in fileNames]
        self.assertSetEqual(set(["basic1.eimu", "basic2.eimu", "basic3.eimu", "short1.eimu"]), set(strippedFileNames))
        
    def test_equalizePositiveAndNegative(self):
        model = eimuLSTM.EimuLSTMInput()
        (_, y1), (_, y2) = model.fromDirectory(f"{commons.PROJECT_ROOT}/test/test_data/directory_test")
        # positive = 1, negative = 0, so sum of all should equal -sum of (all -1)
        self.assertEqual(np.sum(y1), -np.sum(y1 - 1))
        self.assertEqual(np.sum(y2), -np.sum(y2 - 1))
        
if __name__ == "__main__":
    unittest.main()
