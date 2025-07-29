import numpy as np
from ntsim.IO.gParticles import gParticles
from ntsim.utils.report_timing import report_timing
import ntsim.utils.systemofunits as units
from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from particle import Particle
from ntsim.utils.gen_utils import make_random_position_shifts

class ToyGen(PrimaryGeneratorBase):
    arg_dict = {
        'particle_pdgid'   : {'type': int, 'default': 13, 'help': ''},
        'n_gun_particles'  : {'type': int, 'default': 1, 'help': ''},
        'tot_energy_GeV'   : {'type': float, 'default': 1, 'help': ''},
        'position_m'       : {'type': float, 'nargs': 3, 'default': [0,0,0], 'help': ''},
        'direction'        : {'type': float, 'nargs': 3, 'default': [0,0,1], 'help': ''},
        'shifts_dimensions': {'type': float, 'nargs': 2, 'default': [0,0], 'help': ''}
    }
    arg_dict.update(PrimaryGeneratorBase.arg_dict_position)
    
    def logger_info(self):
        self.logger_generator.info(f'Generated particle "{Particle.from_pdgid(self.particle_pdgid).name}" with energy {self.tot_energy_GeV} GeV')

    @report_timing
    def make_event(self, event):
        self.particles = gParticles("Primary")
        uid = 0
        gen = 0
        pdgid = int(self.particle_pdgid)
        mass_GeV = Particle.from_pdgid(pdgid).mass*units.MeV/units.GeV # in GeV
        tot_energy = self.tot_energy_GeV
        if self.random_position:
            position, weight = self.set_random_position(1, self.random_volume)
            event.EventHeader.event_weight = weight
        else:
            position = self.position_m
        
        time = 0
        
        if self.set_angular_direction:
            direction = self.angular_direction(self.direction_theta, self.direction_phi)
        else:
            direction = self.direction

        dr = make_random_position_shifts(self.shifts_dimensions[0], self.shifts_dimensions[1], self.n_gun_particles - 1)
        new_pos = position + dr
        position = np.row_stack((position, new_pos))
        #FIXME: change withount using for
        for  i in range(self.n_gun_particles):
            self.particles.add_particles(uid, gen, pdgid, position[i], time, direction, tot_energy)
        event.particles = self.particles
        self.logger_info()