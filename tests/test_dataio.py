import unittest
import os
import pyatmos

class DataIO(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._input_clima_dat_filename = os.path.join(dir_path, 'input_clima.dat')
        super().__init__(*args, **kwargs)

    def test_read_input_clima_dat(self):
        input_clima = pyatmos.util.read_file(self._input_clima_dat_filename)
        print(input_clima)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
