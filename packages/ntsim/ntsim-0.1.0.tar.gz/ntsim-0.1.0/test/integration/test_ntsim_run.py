import pytest
import subprocess
import h5py

def run_shell(cmd, check=True):
    """run the shell command. If 'check==True' check that returncode is 0"""
    
    print(f'Running in shell: {cmd}')
    p = subprocess.run(cmd.split(), capture_output=True)
    if check:
        try:
            p.check_returncode()
        except subprocess.CalledProcessError:
            print(str(p.stdout, 'utf-8'))
            print(str(p.stderr, 'utf-8'))
            raise
    return p

def run_ntsim(params, output_dir=None, check=True):
    """run the ntsim with given output directory. 
    If 'check'==True, raises CalledProcessError, if the process exited with nonzero status.
    """
    if output_dir:
        params+=" --H5Writer.h5_output_dir "+str(output_dir)
    return run_shell("python3 -m ntsim "+params, check=check)

def test_basic_run_ToyGen(tmp_path):
    run_ntsim("--generator ToyGen --ToyGen.particle_pdgid 13 --ToyGen.tot_energy_GeV 2", output_dir=tmp_path)
    #check file contents
    with h5py.File(tmp_path/"events.h5") as f:
        #check that we have only one event
        assert list(f.keys())==['ProductionHeader','event_0']
        #check the event contents
        assert list(f['event_0'].keys()) == ['event_header', 'hits', 'particles', 'photons', 'tracks']
        #check the primary particle
        primaries = f['event_0/particles/Primary']
        assert len(primaries)==1, "Expect one primary particle"
        t=primaries[0]
        assert t['pdgid']==13, "Expect muon primary"
        assert t['E_tot_GeV']==2.0, "Expect 2 GeV muon"
        #check that we have tracks
        tracks = f['event_0/tracks/g4_tracks_0']
        assert abs(tracks['E_tot_GeV'][0]-2.0)/2.0 < 1e-5, "Expect initial muon Etot is around 2 GeV"
        assert len(tracks)>0
        #check that we have specific particles' tracks in geant simulation
        particles = set(tracks['pdgid'])
        assert 13 in particles, "Must have muon tracks"
        assert 11 in particles, "Must have electron tracks"
        assert 22 in particles, "Must have photon tracks"
    

def test_run_Laser(tmp_path):
    run_ntsim("--generator Laser --Laser.wavelength 400 --writer H5Writer --H5Writer.h5_save_event photons", output_dir=tmp_path)
    #Result: events.h5 file which has only 'photons' folder in event (set by H5Writer)
    with h5py.File(tmp_path/"events.h5") as f:
        assert list(f['event_0'].keys()) == ['event_header','photons']

def test_run_SolarPhotons(tmp_path):
    #Generate photons from the Sun which are propagated in 20 steps. This is an example of photon propagator.
    run_ntsim("--generator SolarPhotons --photon_propagator MCPhotonPropagator --MCPhotonPropagator.n_scatterings 20", output_dir=tmp_path)
    #Result: events.h5 file with data about photons and 'event_0/photons/photons_j/r' tables has 20 horizontal strings which are coordinates of photons at each scattering step
    with h5py.File(tmp_path/"events.h5") as f:
        #loop over all photons
        for name, photons in f['event_0/photons'].items():
            print(name, photons['r'])
            assert len(photons['r'])==20, "Expected excatly 20 scatterings"

def test_run_Laser_with_BGVD_compute_hits(tmp_path):
    #Generate muon and configure Telescope with detector's effects. --compute_hits provides option for writer to save geometry and for ray_tracer for calculating hits.
    run_ntsim("--generator Laser --Laser.position_m -13.8 -211.9 95  --telescope BGVDTelescope --detector BGVDSensitiveDetector --compute_hits", output_dir=tmp_path)
    #Result: events.h5 file with event data and geometry folder which has data about telescope's configuration
    with h5py.File(tmp_path/"events.h5") as f:
        assert 'geometry' in f, "File must have 'geometry' folder with telescope description"
        hits = f['event_0/hits/Hits']
        print(hits)
        assert len(hits)>=7000, "We expect at least 7000 hits" 
        
def test_run_Muon_with_BGVD_produces_hits(tmp_path):
    #Generate muon and configure Telescope with detector's effects. --compute_hits provides option for writer to save geometry and for ray_tracer for calculating hits.
    run_ntsim("--generator ToyGen --ToyGen.tot_energy_GeV 1000 --ToyGen.position_m 186.75 213 95  --telescope BGVDTelescope --detector BGVDSensitiveDetector --compute_hits --cherenkov=CherenkovGenerator", output_dir=tmp_path)
    #Result: events.h5 file with event data and geometry folder which has data about telescope's configuration
    with h5py.File(tmp_path/"events.h5") as f:
        assert 'geometry' in f, "File must have 'geometry' folder with telescope description"
        assert  'Hits' in f['event_0/hits'], "No 'Hits' in 'event_0/hits'."
        
def test_run_Laser_with_diffuser(tmp_path):
    #Generate muon and configure Telescope with detector's effects. --compute_hits provides option for writer to save geometry and for ray_tracer for calculating hits.
    run_ntsim("--generator Laser --Laser.diffuser exp 5", output_dir=tmp_path)
    #Result: events.h5 file with event data and geometry folder which has data about telescope's configuration
    with h5py.File(tmp_path/"events.h5") as f:
        assert 'event_0' in f, "File must have 'event_0'"

