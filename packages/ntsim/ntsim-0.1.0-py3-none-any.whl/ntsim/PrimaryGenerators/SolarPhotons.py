from pvlib import spectrum, solarposition, atmosphere
import pandas as pd
import numpy as np
from scipy import interpolate
from ntsim.IO.gPhotons import gPhotons
from ntsim.PrimaryGenerators.Base.PrimaryGeneratorBase import PrimaryGeneratorBase
from ntsim.utils.gen_utils import make_random_position_shifts
from ntsim.random import rng

class SolarPhotons(PrimaryGeneratorBase):
    arg_dict = {
        'position':  {'type': float, 'nargs': '+', 'default': [0.,0.,1360.], 'help': 'initial position'},
        'direction': {'type': float, 'nargs': '+', 'default': [0.,0.,-1.], 'help': 'unit three vector for solar photons direction'},
        'bunches': {'type': int, 'default': 3, 'help': 'bunches'},
        'year': {'type': int, 'default': 2021, 'help': 'date : year'},
        'month': {'type': int, 'default': 6, 'help': 'date : month'},
        'day': {'type': int, 'default': 21, 'help': 'date : day'},
        'hour': {'type': int, 'default': 13, 'help': 'date : hour'},
        'minute': {'type': int, 'default': 4, 'help': 'date : minute'},
        'radius' :{'type': float, 'default': 0., 'help': 'distribution radius'},
        'photons_in_bunch': {'type': int, 'default': 10000, 'help': 'photons in one bunch'}
    }

    def irradiance_on_surface(self):
        date = "{year}-{month}-{day} {hour}:{minute}".format(year = self.year, month = self.month, day = self.day , hour = self.hour, minute = self.minute)
        times = pd.date_range(date, freq='h', periods=1, tz='Etc/GMT-8')
        lat = 51.771 #Baikal lake coordinates
        lon = 104.398
        altitude = 456
        pressure = 98659 #fixed data which .spectrl2() needs
        water_vapor_content = 0.1
        tau500 = 0.1
        ozone = 0.31
        albedo = 0.05
        solpos = solarposition.get_solarposition(times, lat, lon, altitude) #calculate solar position data(zenith, azimuth and other) based on latitude, longtitude and date range
        self.solar_azimuth = solpos.azimuth
        self.solar_zenith  = solpos.apparent_zenith
        relative_airmass = atmosphere.get_relative_airmass(self.solar_zenith, model='kastenyoung1989')
        spectra = spectrum.spectrl2(
            apparent_zenith=self.solar_zenith,
            aoi=self.solar_zenith,
            surface_tilt=0,
            ground_albedo=albedo,
            surface_pressure=pressure,
            relative_airmass=relative_airmass,
            precipitable_water=water_vapor_content,
            ozone=ozone,
            aerosol_turbidity_500nm=tau500,
            )
        self.waves = spectra['wavelength']
        self.power = spectra['poa_global'].reshape(np.shape(self.waves))

    def amount_of_photons(self):
        hc = 1.985859728 * 1e-25
        bunch_waves = self.waves[0:36] # 36 items is for last wavelength = 656 nm
        power_wl = self.power[0:36] # it is not necessary, in next string it is able to make interpolate function in all wavelengths
        interpol_power_func = interpolate.interp1d(bunch_waves, power_wl)
        self.wl = np.arange(350 , 611 , 1) # bunch waves 
        dtotal_power = interpol_power_func(self.wl)*1 # power distribution
        #dtotal_power = interpol_power * np.diff(self.wl)[0]
        self.total_power = np.sum(dtotal_power)
        dtotal_photons = dtotal_power * self.wl * 1e-9 / hc
        self.total_photons = np.sum(dtotal_photons)
        self.dprob = dtotal_photons/self.total_photons # probability

    def make_photons(self):
        ph = self.photons_in_bunch
        r_def = np.tile(np.asarray(self.position), (1, ph)).reshape((1,ph,3))
        x0 = r_def[0,0,0]
        y0 = r_def[0,0,1]
        z0 = r_def[0,:,2]
        dr = make_random_position_shifts(self.radius, 0, ph)
        x = dr[:,0] + x0
        y = dr[:,1] + y0
        xy = np.dstack((x,y))
        r = np.dstack((xy, z0))
        arr_dir = np.asarray(self.direction)
        arr_dir[0] = np.cos(self.solar_azimuth[0] * np.pi/180.) * np.sin(self.solar_zenith[0] * np.pi/180.)
        arr_dir[1] = np.sin(self.solar_azimuth[0] * np.pi/180.) * np.sin(self.solar_zenith[0] * np.pi/180.)
        arr_dir[2] = -1.
        dir = np.tile(arr_dir, (1, ph)).reshape((1,ph,3))
        arr_dir_z = (-1) * np.sqrt(1 - (np.sin(self.solar_zenith[0] * np.pi/180.) / self.n_gr_arr)**2)
        wl_z = np.zeros((2,np.size(self.wl)))
        wl_z[0] = self.wl
        wl_z[1] = arr_dir_z
        wl_z = wl_z.T
        rand_waves_z = rng.choice(wl_z, ph, p = self.dprob)
        dir[:,:,2] = rand_waves_z[:,1]
        dir_norm = np.sqrt(np.sum(dir**2 , axis=2))
        dir_norm = np.repeat(dir_norm, 3, axis=1).reshape((ph,3))
        dir = dir / dir_norm
        t = np.zeros((1,ph))
        if self.radius != 0:
            weight = np.pi * (self.radius**2) * self.total_photons/(self.bunches * ph) # weight is updated in clone generator
        else:
            weight = self.total_photons/(self.bunches * ph) # weight is updated in clone generator
        rand_waves = rng.choice(self.wl, ph, p = self.dprob)
        photons = gPhotons()
        photons.add_photons(new_n_photons=ph, new_n_steps=1, new_position_m=r, new_t_ns=t, 
                            new_direction=dir, new_wavelength_nm=rand_waves, new_weight=weight, new_progenitor=[0])
        return photons
    
    def get_refraction_index(self):
        from bgvd_model.BaikalWater import BaikalWater
        BaikalWaterProps = BaikalWater()
        n_gr = interpolate.CubicSpline(BaikalWaterProps.wavelength, BaikalWaterProps.group_refraction_index, bc_type='not-a-knot')
        self.n_gr_arr = n_gr(self.wl)


    def make_photons_generator(self):
        self.irradiance_on_surface()
        self.amount_of_photons()
        self.get_refraction_index()
        for i in range(self.bunches):
            yield self.make_photons()

    def make_event(self, event):
        event.photons = self.make_photons_generator()

    # def __init__(self):
    #     super().__init__('SolarPhotons')
    #     self.module_type = 'generator'

    # def configure(self, opts):
    #     self.photons = gPhotons()
    #     self.progenitor = [0]
    #     self.position = opts.cloner_cylinder_center_m
    #     self.direction = opts.solar_direction
    #     self.photons_in_bunch = opts.solar_photons_in_bunch[0]
    #     self.bunches = opts.solar_bunches[0]
    #     self.year = opts.solar_year[0]
    #     self.month = opts.solar_month[0]
    #     self.day = opts.solar_day[0]
    #     self.hour = opts.solar_hour[0]
    #     self.minute = opts.solar_minute[0]
    #     self.radius = opts.solar_radius[0]
    #     self.n_clones = opts.cloner_n
    #     self.r_cloning = opts.cloner_cylinder_dimensions_m[0]
    #     self.amount_of_photons()
    #     self.irradiance_on_surface()
    #     self.set_date()
    #     self.make_photons()
    #     self.log.info(f"  photons in bunch : {self.photons_in_bunch}")
    #     self.log.info(f"  distribution radius : {self.radius} m")
    #     self.log.info(f"  position = {self.position}")
    #     self.log.info(f"  year : {self.year}")
    #     self.log.info(f"  month :  {self.month}")
    #     self.log.info(f"  day : {self.day}")
    #     self.log.info(f"  hour : {self.hour}")
    #     self.log.info(f"  minute : {self.minute}")
    #     self.log.info(f"  total photons : {self.total_photons} m^-2 * s^-1")
    #     self.log.info(f"  total power : {self.total_power} W/m^2")
    #     self.log.info(f"  clones : {self.n_clones}")
    #     self.log.info(f"  cloning radius : {self.r_cloning} m")
    #     self.log.info('congifured')