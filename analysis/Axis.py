class Axis():
    def __init__(self, index, title, units=None):
        self.index = index
        self.title = title
        self.units = units
        if units:
            self.funits = '{0} [{1}]'.format(self.title, self.units)
        else:
            self.funits = self.title

        self.label = self._get_latex_lable()

    def _get_latex_lable(self):

        label_dict = {
                'O2' : 'O$_2$',
                'CH4' : 'CH$_4$',
                'H2' : 'H$_2$',
                'H2O' : 'H$_2$O',
                }
        try:
            return label_dict[self.index]
        except KeyError:
            return self.index
