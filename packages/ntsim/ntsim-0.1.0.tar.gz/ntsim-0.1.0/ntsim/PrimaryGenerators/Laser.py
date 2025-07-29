import numpy as np

from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from ntsim.PrimaryGenerators.Diffuser import DiffuserExponential,DiffuserCone
from ntsim.utils.gen_utils import generate_cherenkov_spectrum
from ntsim.utils.report_timing import report_timing

class Laser(PrimaryGeneratorBase):
    arg_dict = {
        'n_photons': {'type': int, 'default': 10000, 'help': 'number of photons to generate'},
        'photons_bunches': {'type': int, 'default': 1, 'help': 'number of bunches'},
        'photons_n_scatterings': {'type': int, 'default': 5, 'help': 'number of scatterings=n_steps'},
        'photons_weight': {'type': float, 'default': 1000, 'help': 'statistical weight of a photon'},
        'position_m': {'type': float, 'nargs': 3, 'default': [0.,0.,0.], 'help': 'three vector for laser position'},
        'direction': {'type': float, 'nargs': 3, 'default': [0.,0.,1.], 'help': 'unit three vector for photons direction'},
        'wavelength': {'type': float, 'default': 350, 'help': ''},
        'diffuser': {'type': str, 'nargs': 2, 'default': ('none',0), 'help': 'laser diffuser mode: (exp,sigma) or (cone, angle)'}
    }
    
    def set_diffuser(self):
        self.logger_generator.info(f'Selected diffuser: "{self.diffuser[0]}" with parameter: {self.diffuser[1]}')
        if self.diffuser[0] == 'exp':
            self.laser_diffuser = DiffuserExponential(float(self.diffuser[1]))
        elif self.diffuser[0] == 'cone':
            self.laser_diffuser = DiffuserCone(float(self.diffuser[1]))
        elif self.diffuser[0] == 'none':
            self.laser_diffuser = None
        else:
            raise ValueError('Invalid diffuser type')

    def get_direction(self):
        self.set_diffuser()
        dir0 = np.array(self.direction,dtype=np.float64)
        if not self.laser_diffuser:
            self.dir = np.tile(dir0,(self.photons_n_scatterings,self.n_photons_bunch,1))
        else:
            dir = np.tile(dir0,(self.n_photons_bunch,1))
            dir = self.laser_diffuser.random_direction(dir)
            dir = np.tile(dir,(self.photons_n_scatterings))
            dir = np.reshape(dir,(self.n_photons_bunch,self.photons_n_scatterings,3))
            dir = np.swapaxes(dir, 0, 1)
            self.dir = dir

    def make_photons(self):
        self.n_photons_bunch = int(self.n_photons/self.photons_bunches)
        self.get_direction()
        self.r  = np.tile(np.array(self.position_m,dtype=np.float64), (self.photons_n_scatterings,self.n_photons_bunch,1))
        self.t = np.tile(np.array([0.],dtype=np.float64),(self.photons_n_scatterings,self.n_photons_bunch))
        wavelengths = np.tile(np.array([self.wavelength],dtype=np.float64),self.n_photons_bunch)
        progenitor = [0]*self.n_photons
        from ntsim.IO.gPhotons import gPhotons
        photons = gPhotons()
        photons.add_photons(self.n_photons_bunch,self.photons_n_scatterings,self.r,self.t,self.dir,wavelengths,progenitor,new_weight=self.photons_weight)
        return photons

    @report_timing
    def make_event(self, event):
        event.photons = self.make_photons_generator()

    def make_photons_generator(self):
        for i in range(self.photons_bunches):
            yield self.make_photons()
