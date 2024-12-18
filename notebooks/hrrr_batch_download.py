import sys
import numpy as np
import pandas as pd
from tqdm import tqdm, trange
import h5py
from herbie import Herbie

forecast = 1
if forecast:
    postfix = f'{forecast} hour fcst'
else:
    postfix = 'anl'

def yrb(x):
    return x[-183:-112,287:345]

def mkz(x):
    return x[-246:-217,222:262]

def write_daymet_h5(filename, data):
    with h5py.File(filename, 'w') as f:
        for k, v in data.items():
            try:
                f.create_dataset(k, data=v)
            except TypeError:
                g = f.create_group(k)
                for tk, tv in v.items():
                    g.create_dataset(tk, data=tv)

number_of_days = {1:31, 2:28, 3:31, 4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
cumsum = np.cumsum([0,0]+list(number_of_days.values()))

for year in [2024]:
    data = {
        "air temperature [K]": {},
        "incoming shortwave radiation [W m^-2]": {},
        "precipitation rain [m s^-1]": {},
        "precipitation snow [m SWE s^-1]": {},
        "vapor pressure air [Pa]": {},
    }
    for month in trange(1, 11):
        times = pd.date_range(f'{year}-{month}-1 06:00:00', periods=24*number_of_days[month], freq="1h")
        for i, time in tqdm(enumerate(times)):
            label = str(i+cumsum[month]*24)
            try:
                H = Herbie(time, model="hrrr", product="prs", fxx=forecast, verbose=False)
                
                # Air temperature
                t2m = H.xarray(":TMP:2 m above ground:"+postfix, remove_grib=False)
                data["air temperature [K]"][label] = yrb(t2m.t2m.values)

                # Precipitation rate
                prate = H.xarray(":PRATE:surface:"+postfix, remove_grib=False)
                prate["prate"] /= 1e3 # kg/m2/s = mm/s to m/s 
                rain = np.where(t2m.t2m.values >= 273.15, prate.prate.values, 0)
                snow = np.where(t2m.t2m.values < 273.15, prate.prate.values, 0)
                data["precipitation rain [m s^-1]"][label] = yrb(rain)
                data["precipitation snow [m SWE s^-1]"][label] = yrb(snow)

                # Relative humidity to vapor pressure
                rh = H.xarray(":RH:2 m above ground:"+postfix, remove_grib=False)
                vp = rh.r2.values/100*611.2*np.exp(17.67*(t2m.t2m.values-273.15)/(t2m.t2m.values-273.15+243.5))
                data["vapor pressure air [Pa]"][label] = yrb(vp)

                # Shortwave radiation
                srad = H.xarray(":DSWRF:surface:"+postfix, remove_grib=False)
                data["incoming shortwave radiation [W m^-2]"][label] = yrb(srad.dswrf.values)
            except:
                print(f'Herbie failed at {time}\n'*21)
                try:
                    data["air temperature [K]"][label] = data["air temperature [K]"][str(int(label)-1)]
                    data["precipitation rain [m s^-1]"][label] = data["precipitation rain [m s^-1]"][str(int(label)-1)]
                    data["precipitation snow [m SWE s^-1]"][label] = data["precipitation snow [m SWE s^-1]"][str(int(label)-1)]
                    data["vapor pressure air [Pa]"][label] = data["vapor pressure air [Pa]"][str(int(label)-1)]
                    data["incoming shortwave radiation [W m^-2]"][label] = data["incoming shortwave radiation [W m^-2]"][str(int(label)-1)]
                except KeyError:
                    print(f'\tKeyError at {time}\n'*21)
                    data["air temperature [K]"][label] = 293.15
                    data["precipitation rain [m s^-1]"][label] = 0
                    data["precipitation snow [m SWE s^-1]"][label] = 0
                    data["vapor pressure air [Pa]"][label] = 500
                    data["incoming shortwave radiation [W m^-2]"][label] = 0

        write_daymet_h5(f'./h5/hrrr_{year}{str(month).zfill(2)}_{number_of_days[month]}d.h5', data)
