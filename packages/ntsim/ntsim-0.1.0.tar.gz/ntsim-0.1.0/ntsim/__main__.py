import configargparse, argparse
import sys
import numpy as np
from argparse                       import Namespace
from tqdm import trange
from ntsim.utils.report_timing      import report_timing
from ntsim.IO.gEvent                import gEvent

from ntsim.random import set_seed

from ntsim.Base.BaseFactory                                             import BaseFactory
from ntsim.Telescopes.Factory.TelescopeFactory                          import TelescopeFactory
from ntsim.SensitiveDetectors.Factory.SensitiveDetectorFactory          import SensitiveDetectorFactory
from ntsim.MediumProperties.Factory.MediumPropertiesFactory             import MediumPropertiesFactory
from ntsim.MediumScatteringModels.Factory.MediumScatteringModelsFactory import MediumScatteringModelsFactory
from ntsim.PrimaryGenerators.Factory.PrimaryGeneratorFactory            import PrimaryGeneratorFactory
from ntsim.Propagators.Factories.ParticlePropagatorFactory              import ParticlePropagatorFactory
from ntsim.Propagators.Factories.PhotonPropagatorFactory                import PhotonPropagatorFactory
from ntsim.Propagators.Factories.RayTracerFactory                       import RayTracerFactory
from ntsim.CherenkovGenerators.Factory.CherenkovGeneratorFactory        import CherenkovGeneratorFactory
from ntsim.CloneGenerators.Factory.CloneGeneratorFactory                import CloneGeneratorFactory
from ntsim.Triggers.Factory.TriggerFactory                              import TriggerFactory
from ntsim.Analysis.Factory.AnalysisFactory                             import AnalysisFactory
from ntsim.IO.Factories.WriterFactory                                   import WriterFactory

class NTSim:
    def __init__(self):
        self.TelescopeFactory             = TelescopeFactory()
        self.SensitiveDetectorFactory     = SensitiveDetectorFactory()
        self.MediumPropertiesFactory      = MediumPropertiesFactory()
        self.MediumScatteringModelFactory = MediumScatteringModelsFactory()
        self.PrimaryGeneratorFactory      = PrimaryGeneratorFactory()
        self.ParticlePropagatorFactory    = ParticlePropagatorFactory()
        self.PhotonPropagatorFactory      = PhotonPropagatorFactory()
        self.RayTracerFactory             = RayTracerFactory()
        self.CherenkovGeneratorFactory    = CherenkovGeneratorFactory()
        self.CloneGeneratorFactory        = CloneGeneratorFactory()
        self.TriggerFactory               = TriggerFactory()
        self.AnalysisFactory              = AnalysisFactory()

        self.WriterFactory = WriterFactory()

        self.event = gEvent()

        logger.info('Initialized NTSim')

    def add_module_args(self, parser) -> dict:
        known_factories = {}
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if issubclass(attr_value.__class__, BaseFactory):
                known_factories[attr_value.__class__.__name__] = list(attr_value.known_instances.keys())
                for module_name in attr_value.known_instances:
                    attr_value.known_instances[module_name].add_args(parser)
        return known_factories

    def configure_telescope_detector(self, opts: Namespace) -> None:
        if opts.compute_hits:
            
            self.SensitiveDetectorBlueprint.configure(self.SensitiveDetectorBlueprint,opts)

            self.Telescope.build(detector_blueprint = self.SensitiveDetectorBlueprint)
            
#            self.Telescope.world.print()
            
            self.bbox_array, self.detector_array = self.Telescope.flatten_nodes()
            
            target_depth = opts.depth
            
            self.bboxes_depth    = self.Telescope.boxes_at_depth(self.bbox_array, target_depth)
            self.detectors_depth = self.Telescope.detectors_at_depth(self.bbox_array, self.detector_array, target_depth)
            
            self.effects         = self.Telescope.sensitive_detectors[0].effects
            self.effects_options = np.array([sensitive_detector.effects_options for sensitive_detector in self.Telescope.sensitive_detectors])
            self.effects_names   = np.array(self.Telescope.sensitive_detectors[0].effects_names)
            
            self.Writer.write_geometry(self.bbox_array, self.detector_array)

    def configure(self, opts: Namespace) -> None:        
        for attr_name in dir(self):
            attr_value = getattr(self, attr_name)
            if issubclass(attr_value.__class__, BaseFactory):
                attr_value.configure(opts)
                self.__dict__[f'{attr_name[:-7]}Blueprint'] = attr_value.get_blueprint()
                if not self.__dict__[f'{attr_name[:-7]}Blueprint']: continue
                try:
                    self.__dict__[attr_name[:-7]] = self.__dict__[f'{attr_name[:-7]}Blueprint'](self.__dict__[f'{attr_name[:-7]}Blueprint'].__name__)
                    self.__dict__[attr_name[:-7]].configure(opts)
                except:
                    continue
        
        self.Writer.open_file()
        
        self.configure_telescope_detector(opts)
        
        if opts.compute_hits:
            self.RayTracer.configure(self.bboxes_depth, self.detectors_depth, self.effects, self.effects_options, self.effects_names)
        
        self.MediumProperties.init()
        
        if not opts.trigger_name is None:
            self.Trigger.set_triggers()
        
        self.n_events = opts.n_events
    
    @report_timing
    def process(self) -> None:

        for event_id in trange(self.n_events):
            self.Writer.new_event(event_id)
            self.event.reset()
            
            self.PrimaryGenerator.make_event(self.event)
            
            if self.event.has_particles():
                self.ParticlePropagator.propagate(self.event)
                self.Writer.write_data(self.event.particles, folder_name='particles')
                self.Writer.write_data(self.event.tracks, folder_name='tracks')
            
            if not opts.cherenkov_generator_name is None:
                self.CherenkovGenerator.generate(self.event)
            
            if not opts.clone_generator_name is None: 
                self.CloneGenerator.make_clones_in_event(self.event, event_id)
            
            for bunch_id,photons in enumerate(self.event.photons):
                if bunch_id == 0 : self.event.EventHeader.photons_sampling_weight = photons.weight[0]
                self.event.EventHeader.n_photons_total += photons.n_photons
                self.event.EventHeader.n_photon_bunches += 1
                self.PhotonPropagator.propagate(photons,self.MediumProperties,self.MediumScatteringModel)
                self.Writer.write_photons(photons,bunch_id)
                if opts.compute_hits:
                    self.RayTracer.propagate(self.event, photons)
            
            #FIXME: trigger would better take event as an input and rewrite hits in event inside itself  
            if not opts.trigger_name is None:
                self.Trigger.apply_trigger_conditions(self.event.hits[0]) # [0] is for gHits object in list 
                self.event.hits[0] = self.Trigger.trigger_hits            # gHits object of "orig" hits is always the only one 
            
            if not opts.analysis_name is None:
                self.Analysis.analysis(self.event)
###################
            self.Writer.write_data(self.event.cloner_hits, folder_name='hits/cloner_hits')
            self.Writer.write_cloner_shifts(self.event.cloner_shifts)
            self.Writer.write_data(self.event.hits, folder_name='hits')
            self.Writer.write_event_header(self.event.EventHeader)
        self.event.ProductionHeader = opts
        self.Writer.write_prod_header(self.event.ProductionHeader)
        
        self.Writer.close_file()
        if not opts.analysis_name is None:
            self.Analysis.save_analysis()

if __name__ == '__main__':
    __name__ = 'NTSim'
    import logging.config
    from ntsim.utils.logger_config import logger_config
    
    logging.config.dictConfig(logger_config)
    logger = logging.getLogger('NTSim')
#    logformat='[%(name)45s ] %(levelname)8s: %(message)s'
#    logging.basicConfig(format=logformat)

    parser = configargparse.ArgParser()

    parser.add_argument('-l', '--log-level',type=str,choices=('deepdebug', 'debug', 'info', 'warning', 'error', 'critical'),default='INFO',help='logging level')
    parser.add_argument('--seed',type=int, default=None, help='random generator seed')
    parser.add_argument('--show-options',action="store_true", help='show all options')
    parser.add_argument('--compute_hits',action="store_true", help='if this flag is set, the detector hits are produced in the output')
    
    opts, _ = parser.parse_known_args()
    #set the random seed for this run - do this before any other initialization is done!
    set_seed(opts.seed)
    
    logger.setLevel(logging.getLevelName(opts.log_level.upper()))

    simu= NTSim()

    known_factories = simu.add_module_args(parser)
    parser.add_argument('--telescope.name', dest='telescope_name', type=str, choices=known_factories['TelescopeFactory'], default=None, help='Telescope to use')
    parser.add_argument('--detector.name', dest='sensitive_detector_name', type=str, choices=known_factories['SensitiveDetectorFactory'], default=None, help='Sensitive detector to use')
    parser.add_argument('--medium_prop.name', dest='medium_properties_name', type=str, choices=known_factories['MediumPropertiesFactory'], default='Example1MediumProperties', help='Medium properties to use')
    parser.add_argument('--medium_scat.name', dest='medium_scattering_model_name', type=str, choices=known_factories['MediumScatteringModelsFactory'], default='HenyeyGreenstein', help='Medium scattering to use')
    parser.add_argument('--generator.name', dest='primary_generator_name', type=str, choices=known_factories['PrimaryGeneratorFactory'], default='ToyGen', help='Primary Geenrator to use')
    parser.add_argument('--propagator.name', dest='particle_propagator_name', type=str, choices=known_factories['ParticlePropagatorFactory'], default='ParticlePropagator', help='Propagator to use')
    parser.add_argument('--photon_propagator.name', dest='photon_propagator_name', type=str, choices=known_factories['PhotonPropagatorFactory'], default='MCPhotonPropagator', help='Photon propagator to use')
    parser.add_argument('--ray_tracer.name', dest='ray_tracer_name', type=str, choices=known_factories['RayTracerFactory'], default='SmartRayTracer', help='Ray tracer to use')
    parser.add_argument('--cherenkov.name', dest='cherenkov_generator_name', type=str, choices=known_factories['CherenkovGeneratorFactory'], default=None, help='')
    parser.add_argument('--cloner.name', dest='clone_generator_name',type=str, choices=known_factories['CloneGeneratorFactory'], default=None, help='')
    parser.add_argument('--trigger.name', dest='trigger_name', type=str, choices=known_factories['TriggerFactory'], default=None, help='')
    parser.add_argument('--analysis.name', dest='analysis_name', type=str, choices=known_factories['AnalysisFactory'], default=None, help='')

    parser.add_argument('--writer.name', dest='writer_name', type=str, choices=known_factories['WriterFactory'], default='H5Writer', help='')

    parser.add_argument('--depth', type=int, default=0, help='depth bounding boxes')
    parser.add_argument('--n_events', type=int, default=1, help='')

    opts = parser.parse_args()

    if opts.show_options:
        print(parser.format_values())
    
    simu.configure(opts)
    
    simu.process()