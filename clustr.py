from argparse import ArgumentParser
import os
import pickle as cPickle
from astropy.table import Table
import numpy as np
import reglib  # Regression library
import matplotlib.pyplot as plt
import linmix

# We'll define useful classes here
''' Parse command line arguments '''
parser = ArgumentParser()
# Required argument for catalog
parser.add_argument('catalog', help='FITS catalog to open')
# Required arguement for axes
valid_axes = ['l500kpc', 'lr2500', 'lr500', 'lr500cc', 't500kpc', 'tr2500',
              'tr500', 'tr500cc', 'lambda']
parser.add_argument('y', help='what to plot on y axis', choices=valid_axes)
parser.add_argument('x', help='what to plot on x axis', choices=valid_axes)
# Optional argument for file prefix
parser.add_argument('-p', '--prefix', help='prefix for output file')
# Optional arguments for any flag cuts
# FIX: in the future, make an allowed choices vector work!
parser.add_argument(
    '-f',
    '--flags',
    nargs='+',
    type=str,
    help=('Input any desired flag cuts as a list of flag names '
    '(with "" and no spaces!)')
)

def fits_label(axis_name):
    ''' Get the FITS column label for `axis_name` '''
    labels = {
        'lambda': 'lambda',
        'l500kpc': '500_kiloparsecs_band_lumin',
        'lr2500': 'r2500_band_lumin',
        'lr500': 'r500_band_lumin',
        'lr500cc': 'r500_core_cropped_band_lumin',
        't500kpc': '500_kiloparsecs_temperature',
        'tr2500': 'r2500_temperature',
        'tr500': 'r500_temperature',
        'tr500cc': 'r500_core_cropped_temperature'
    }

    return labels[axis_name]

class Config:
    '''
    Used for CluStR config processing
    Some options:
    - scale_luminosity: Divide luminosity columns by E(z)^-3/2
    '''
    _required_keys = []
    _default_run_name = 'clustr'
    def __init__(self, config_file, run_options):
        with open(config_file, 'r') as stream:

            self._config = yaml.safe_load(stream)

        self.run_options = run_options
        if run_options.run_name is None:
            self.run_name = _default_run_name
        else:
            self.run_name = run_options.run_name
        return

    # The following are so we can access the config
    # values similarly to a dict
    def __getitem__(self, key):
        return self._config.__dict__[key]

    def __setitem__(self, key, value):
        self._config.__dict__[key] = value

    def __delitem__(self, key):
        del self._config.__dict__[key]

    def __contains__(self, key):
        return key in self._config.__dict__

    def __len__(self):
        return len(self._config.__dict__)

    def __repr__(self):
        return repr(self._config.__dict__)

    "def run_name():"

class Catalog:
    #read/load the fits table that contains the data
    def __init__(self,cat_file_name,config):
        self.file_name = cat_file_name

        #self.property = config.property # for example

        self._load_catalog()

        return

    def _load_catalog(self):
        self.cat_table = Table.read(self.file_name)

        # could do other things...

        return
    #just for fun!
    #def plot_data(self, xcol, ycol, size=8, ylog=False):
        #x = self.table[xcol]
        #y = self.table[ycol]

        #plt.scatter(x, y)
        #plt.xlabel(xcol)
        #plt.ylabel(ycol)

        #if ylog is True:
        #    plt.yscale('log')
        #plt.gcf().set_size_inches(size, size) #get current figure then set size
        #plt.show()

        return


def Ez(z):
    Om = 0.3
    H_0 = 0.7
    h = H_0/100
    return np.sqrt(Om*(1.+z)**3 + h)

class Data:
    '''
    This class takes a catalog table, and grabs only the relevant columns
    for the desired fit using the config dictionary.

    config is expected to act like a dictionary
    '''
    #take data frome the Catalog Class and pick rows and columns we want to fit
    #dont call flag in main call it here
    def __init__(self, config, catalog):
        self.get_data(config, catalog)

        return

    def run_config(self):
        config_results = config.rlf #run Config's function rlf and get the results. maybe?
        return config_results

    def get_data(self, config, catalog):
        xlabel = fits_label(config['x_label'])
        ylabel = fits_label(config['y_label'])
        self.x = catalog[label_x]
        self.y = catalog[label_y]

        # Number of original data
        N = np.size(x)

        # Scale data if a luminosity
        if config['scale_x_by_ez']:
            x /= Ez(catalog['redshift'])
        if config['scale_y_by_ez']:
            y /= Ez(catalog['redshift'])

        self.x_err = (catalog[xlabel+'_err_low'] + catalog[xlabel+'_err_high']) / 2.
        self.y_err = (catalog[ylabel+'_err_low'] + catalog[ylabel+'_err_high']) / 2.

        # For now, we expect flag cuts to have already been made
#        flags = self.run_options[flags]
#        if flags is not None:
#            # FIX: Should be more error handling than this!
#            # FIX: Should write method to ensure all the counts are what we expect
#
#            mask = f.create_cuts(self)
#            self.x[mask] = -1
#            self.y[mask] = -1
#
#            print (
#                'NOTE: `Removed` counts may be redundant, '
#                'as some data fail multiple flags.'
#            )
#
#            # Take rows with good data, and all flagged data removed
#            good_rows = np.all([x != -1, y != -1], axis=0)
#            x = x[good_rows]
#            y = y[good_rows]
#            x_err = x_err[good_rows]
#            y_err = y_err[good_rows]
#
#            print ('Accepted {} data out of {}'.format(np.size(x), N))

        if N == 0:
            print (
                '\nWARNING: No data survived flag removal. '
                'Suggest changing flag parameters in `param.config`.'
                '\n\nClosing program...\n')
            raise SystemExit(2)

        print ('mean x error:', np.mean(x_err))
        print ('mean y error:', np.mean(y_err))

        return


class Fitter(object):
    def __init__(self, data, plotting_filename):
        self.viable_data = viable_data
        self.plotting_filename = plotting_filename
        return
    def fit(self):
        x_obs = viable_data[0]
        y_obs = viable_data[1]
        x_err = viable_data[2]
        y_err = viable_data[3]
        #run linmix
        print ("Using Kelly Algorithm...")
        kelly_b, kelly_m, kelly_sig = reglib.run_linmix(x_obs, y_obs, x_err, y_err)

        #use before plotting
        log_x = np.log(self.x_obs)
        x_piv = np.median(log_x)
        log_y = np.log(self.y_obs)


        return [log_x-x_piv, log_y, x_err/self.x_obs, y_err/self.y_obs, x_piv]

"""class SaveData(Fitter):
    def __init__(self, run_options, parameters)
"""

def RunFromCatalog(catalog, xlabel):
    return

def main():

    args = parser.parse_args()

    config_filename = args.config_filename

    config = Config(config_filename) #(2)

    cat_file_name = args.cat_filename

    catalog = Catalog(cat_file_name, config) #(3)

    data = Data(config, catalog) #(4)

    viable_data = data.get_data #check that this is the correct way to access

    fit = Fitter.fit(viable_data) #(6)

    # Just for fun!
    #catalog.plot_data('lambda', 'r500_band_lumin', ylog=True)


if __name__ == '__main__':
    main()
