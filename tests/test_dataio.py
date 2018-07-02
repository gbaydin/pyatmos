import unittest
import os
import pyatmos

class DataIO(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        self._input_clima_dat_file_name = os.path.join(dir_path, 'input_clima.dat')
        self._input_photchem_dat_file_name = os.path.join(dir_path, 'input_photchem.dat')
        super().__init__(*args, **kwargs)

    def test_read_input_clima_dat(self):
        input_clima = pyatmos.util.read_file(self._input_clima_dat_file_name)
        print('\ninput_clima', input_clima)
        self.assertTrue(True)

    def test_read_input_phototchem_dat(self):
        input_photchem = pyatmos.util.read_file(self._input_photchem_dat_file_name)
        print('\ninput_photchem', input_photchem)
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main(verbosity=2)
