#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 24 23:22:21 2019

@author: DRUOT Thierry : original Scilab implementation
         PETEILH Nicolas : portage to Python
"""

import numpy as np

from scipy.optimize import fsolve



class PhysicalData(object):

    def __init__(self):
        self.g = 9.80665  # Gravity acceleration at sea level

        self.rho0 = 1.225  # (kg/m3), air density at sea level
        self.P0 = 101325.  # , standard pressure at sea level
        self.T0 = 288.15  # Kelvins, standard temperature
        self.vc0 = 340.29  # m/s, sound speed at sea level

        self.r = 287.053
        self.gam = 1.40
        self.cv = self.r / (self.gam - 1.)
        self.cp = self.gam * self.cv

        # Mixed gas dynamic viscosity, Sutherland's formula
        self.mu0 = 1.715e-5
        self.Tref = 273.15
        self.S = 110.4

        self.Z = np.array([0., 11000., 20000., 32000., 47000., 50000.])
        self.dtodz = np.array([-0.0065, 0., 0.0010, 0.0028, 0.])

        self.P = np.array([self.sea_level_pressure(), 0., 0., 0., 0., 0.])
        self.T = np.array([self.sea_level_temperature(), 0., 0., 0., 0., 0.])

        for j in range(len(self.Z)-1):
            self.T[j + 1] = self.T[j] + self.dtodz[j] * (self.Z[j + 1] - self.Z[j])
            if (0. < np.abs(self.dtodz[j])):
                self.P[j + 1] = self.P[j] * (1. + (self.dtodz[j] / self.T[j]) * (self.Z[j + 1] - self.Z[j])) ** (-self.g / (self.r * self.dtodz[j]))
            else:
                self.P[j + 1] = self.P[j] * np.exp(-(self.g / self.r) * ((self.Z[j + 1] - self.Z[j]) / self.T[j]))

        self.fuel_density_data = {"kerosene": 803.0,
                                  "petrol": 803.0,
                                  "e_fuel": 803.0,
                                  "gasoline": 800.0,
                                  "liquid_h2": 70.8,
                                  "liquid_ch4": 422.6,
                                  "liquid_nh3": 681.0,
                                  "solid_nh3": 817.0,
                                  "battery": 2800.0}

        self.fuel_heat_data = {"kerosene": 43.1e6,
                               "petrol": 43.1e6,
                               "e_fuel": 43.1e6,
                               "gasoline": 46.41e6,
                               "liquid_h2": 121.0e6,
                               "liquid_ch4": 50.3e6,
                               "liquid_nh3": 16.89e6,
                               "solid_nh3": 16.89e6}


    def fuel_density(self, fuel_type, press=101325.):
        """Reference fuel density
        """
        if (fuel_type=="compressed_h2"):
            p = press*1.e-5
            fuel_density = (-3.11480362e-05*p + 7.82320891e-02)*p + 1.03207822e-01 # Compressed hydrogen at 293.15 K
        else:
            fuel_density = self.fuel_density_data.get(fuel_type, "fuel_type key is unknown")
        return fuel_density

    def fuel_heat(self, fuel_type):
        """Reference fuel lower heating value or battery energy density
        """
        fuel_heat = self.fuel_heat_data.get(fuel_type, "fuel_type key is unknown")
        return fuel_heat

    def gravity(self):
        return self.g

    def sea_level_density(self):
        return self.rho0

    def sea_level_pressure(self):
        return self.P0

    def sea_level_temperature(self):
        return self.T0

    def sea_level_sound_speed(self):
        return self.vc0

    def gas_data(self):
        return self.r, self.gam, self.cp, self.cv

    def air_density(self, pamb, tamb):
        """Ideal gas density
        """
        r, gam, Cp, Cv = self.gas_data()
        rho0 = self.sea_level_density()
        rho = pamb / (r * tamb)
        sig = rho / rho0
        return rho, sig

    def sound_speed(self, tamb):
        """Sound speed for ideal gas
        """
        r, gam, Cp, Cv = self.gas_data()
        vsnd = np.sqrt(gam * r * tamb)
        return vsnd

    def gas_viscosity(self, tamb):
        """Mixed gas dynamic viscosity, Sutherland's formula
        """
        return (self.mu0 * ((self.Tref + self.S) / (tamb + self.S)) * (tamb / self.Tref) ** 1.5)

    def reynolds_number(self, pamb, tamb, mach):
        """Reynolds number based on Sutherland viscosity model
        """
        vsnd = self.sound_speed(tamb)
        rho, sig = self.air_density(pamb, tamb)
        mu = self.gas_viscosity(tamb)
        re = rho * vsnd * mach / mu
        return re

    def atmosphere(self, altp, disa):
        """Pressure and temperature from pressure altitude from ground to 50 km
        """
        g = self.gravity()
        R, gam, Cp, Cv = self.gas_data()

        if (self.Z[-1] < altp):
            raise Exception("pressure_altitude, altitude cannot exceed 50km")

        j = np.searchsorted(self.Z[1:], altp, side="right")

        if (0. < np.abs(self.dtodz[j])):
            pamb = self.P[j] * (1 + (self.dtodz[j] / self.T[j]) * (altp - self.Z[j])) ** (-g / (R * self.dtodz[j]))
        else:
            pamb = self.P[j] * np.exp(-(g / R) * ((altp - self.Z[j]) / self.T[j]))
        tstd = self.T[j] + self.dtodz[j] * (altp - self.Z[j])
        tamb = tstd + disa

        return pamb, tamb, tstd, self.dtodz[j]

    def atmosphere_g(self, altp, disa=0.):
        """Ambiant data from pressure altitude from ground to 50 km according to Standard Atmosphere
        """
        g = self.gravity()
        pamb, tamb, tstd, dtodz = self.atmosphere(altp, disa)
        return pamb, tamb, g

    def pressure_altitude(self, pamb):
        """Pressure altitude from ground to 50 km
        """
        g = self.gravity()
        R, gam, Cp, Cv = self.gas_data()

        if (pamb < self.P[-1]):
            raise Exception("pressure_altitude, altitude cannot exceed 50km")

        j = np.searchsorted(-self.P[1:], -pamb, side="right")

        if (0. < np.abs(self.dtodz[j])):
            altp = self.Z[j] + ((pamb / self.P[j]) ** (-(R * self.dtodz[j]) / g) - 1) * (self.T[j] / self.dtodz[j])
        else:
            altp = self.Z[j] - (self.T[j] / (g / R)) * np.log(pamb / self.P[j])

        return altp

    def pressure(self, altp):
        """Pressure from pressure altitude from ground to 50 km
        """
        g = self.gravity()
        R, gam, Cp, Cv = self.gas_data()

        if (self.Z[-1] < altp):
            raise Exception("pressure_altitude, altitude cannot exceed 50km")

        j = np.searchsorted(self.Z[1:], altp, side="right")

        if (0. < np.abs(self.dtodz[j])):
            pamb = self.P[j] * (1 + (self.dtodz[j] / self.T[j]) * (altp - self.Z[j])) ** (-g / (R * self.dtodz[j]))
        else:
            pamb = self.P[j] * np.exp(-(g / R) * ((altp - self.Z[j]) / self.T[j]))

        return pamb

    def atmosphere_geo(self, altg, disa):
        """Pressure and temperature from geometrical altitude from ground to 50 km
        """
        g = self.gravity()
        R, gam, Cp, Cv = self.gas_data()

        Z = np.zeros_like(self.Z)
        dtodz = np.zeros_like(self.dtodz)
        P = np.zeros_like(self.P)
        T = np.zeros_like(self.T)

        P[0] = self.sea_level_pressure()
        T[0] = self.sea_level_temperature()

        for j in range(len(self.Z)-1):
            K = 1 + disa / self.T[j]
            dtodz[j] = self.dtodz[j] / K
            Z[j + 1] = Z[j] + (self.Z[j + 1] - self.Z[j]) * K

            T[j + 1] = T[j] + dtodz[j] * (Z[j + 1] - Z[j])
            if (0. < np.abs(dtodz[j])):
                P[j + 1] = P[j] * (1. + (dtodz[j] / (T[j] + disa)) * (Z[j + 1] - Z[j])) ** (-g / (R * dtodz[j]))
            else:
                P[j + 1] = P[j] * np.exp(-(g / R) * ((Z[j + 1] - Z[j]) / (T[j] + disa)))

        if (Z[-1] < altg):
            raise Exception("atmosphere_geo, altitude cannot exceed 50km")

        j = np.searchsorted(self.Z[1:], altg, side="right")

        if (0. < np.abs(dtodz[j])):
            pamb = P[j] * (1 + (dtodz[j] / (T[j] + disa)) * (altg - Z[j])) ** (-g / (R * dtodz[j]))
        else:
            pamb = P[j] * np.exp(-(g / R) * ((altg - Z[j]) / (T[j] + disa)))
        tamb = T[j] + dtodz[j] * (altg - Z[j]) + disa

        return pamb, tamb, dtodz[j]

    def altg_from_altp(self, altp, disa):
        """Geometrical altitude from pressure altitude
        """
        def fct(altg, altp, disa):
            pamb, tamb, dtodz = self.atmosphere_geo(altg, disa)
            zp = self.pressure_altitude(pamb)
            return altp - zp

        output_dict = fsolve(fct, x0=altp, args=(altp, disa), full_output=True)

        altg = output_dict[0][0]
        if (output_dict[2] != 1): raise Exception("Convergence problem")

        return altg

    def total_temperature(self, tamb, mach):
        """Stagnation temperature
        """
        r, gam, Cp, Cv = self.gas_data()
        ttot = tamb * (1. + ((gam - 1.) / 2.) * mach**2)
        return ttot

    def total_pressure(self, pamb, mach):
        """Stagnation pressure
        """
        r, gam, Cp, Cv = self.gas_data()
        ptot = pamb * (1 + ((gam-1.) / 2.) * mach**2)**(gam / (gam-1.))
        return ptot

    def vtas_from_mach(self, altp, disa, mach):
        """True air speed from Mach number, subsonic only
        """
        pamb, tamb, tstd, dtodz = self.atmosphere(altp,disa)
        vsnd = self.sound_speed(tamb)
        vtas = vsnd * mach
        return vtas

    def mach_from_vtas(self, altp, disa, vtas):
        """True air speed from Mach number, subsonic only
        """
        pamb, tamb, tstd, dtodz = self.atmosphere(altp,disa)
        vsnd = self.sound_speed(tamb)
        mach = vtas / vsnd
        return mach


    def mach_from_vcas(self, pamb, Vcas):
        """Mach number from calibrated air speed, subsonic only
        """
        r, gam, Cp, Cv = self.gas_data()
        P0 = self.sea_level_pressure()
        vc0 = self.sea_level_sound_speed()
        fac = gam / (gam - 1.)
        mach = np.sqrt(((((((gam - 1.) / 2.) * (Vcas / vc0) ** 2 + 1) ** fac - 1.) * P0 / pamb + 1.) ** (1. / fac) - 1.) * (2. / (gam - 1.)))
        return mach

    def vcas_from_mach(self, pamb, mach):
        """Calibrated air speed from Mach number, subsonic only
        """
        r, gam, Cp, Cv = self.gas_data()
        P0 = self.sea_level_pressure()
        vc0 = self.sea_level_sound_speed()
        fac = gam / (gam - 1.)
        vcas = vc0 * np.sqrt((2. / (gam - 1.)) * ((((pamb / P0) * ((1. + ((gam - 1.) / 2.) * mach ** 2) ** fac - 1.)) + 1.) ** (1. / fac) - 1.))
        return vcas

    def vcas_from_vtas(self, altp, disa, vtas):
        """Calibrated air speed from Mach number, subsonic only
        """
        pamb, tamb, tstd, dtodz = self.atmosphere(altp, disa)
        vsnd = self.sound_speed(tamb)
        mach = vtas / vsnd
        vcas = self.vcas_from_mach(pamb, mach)
        return vcas

    def vtas_from_vcas(self, altp,disa,vcas):
        """True air speed from calibrated air speed, subsonic only
        """
        pamb, tamb, tstd, dtodz = self.atmosphere(altp, disa)
        mach = self.mach_from_vcas(pamb, vcas)
        vsnd = self.sound_speed(tamb)
        vtas = vsnd * mach
        return vtas

    def cross_over_altp(self, vcas, mach):
        """Altitude where constant calibrated air speed meets constant Mach number, subsonic only
        """
        r, gam, Cp, Cv = self.gas_data()
        P0 = self.sea_level_pressure()
        vc0 = self.sea_level_sound_speed()
        fac = gam / (gam - 1)
        pamb = ((1. + ((gam - 1.) / 2.) * (vcas / vc0) ** 2) ** fac - 1.) * P0 / ((1. + ((gam - 1.) / 2.) * mach ** 2) ** fac - 1.)
        altp = self.pressure_altitude(pamb)
        return altp

    def climb_mode(self, speed_mode, mach, dtodz, tamb, disa):
        """Acceleration factor depending on speed driver ('cas': constant CAS, 'mach': constant Mach)
        WARNING : input is mach number whatever speed_mode
        """
        g = self.gravity()
        r, gam, Cp, Cv = self.gas_data()

        if (speed_mode == "cas"):
            fac = (gam - 1.) / 2.
            acc_factor = 1. + (((1. + fac * mach ** 2) ** (gam / (gam - 1.)) - 1.) / (1. + fac * mach ** 2) ** (
                        1. / (gam - 1.))) + ((gam * r) / (2. * g)) * (mach ** 2) * dtodz * (1 - disa / tamb)
        elif (speed_mode == "mach"):
            acc_factor = 1. + ((gam * r) / (2. * g)) * (mach ** 2) * dtodz * (1 - disa / tamb)
        else:
            raise Exception("climb_mode key is unknown")

        return acc_factor




if __name__ == '__main__':

    pass
