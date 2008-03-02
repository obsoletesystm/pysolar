#!/usr/bin/python

#    Library for calculating location of the sun

#    Copyright 2007 Brandon Stafford
#
#    This file is part of Pysolar.
#
#    Pysolar is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    Pysolar is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with Pysolar. If not, see <http://www.gnu.org/licenses/>.

import math
import datetime
import constants
import sys

#if __name__ == "__main__":
def SolarTest():
	latitude_deg = 42.364908
	longitude_deg = -71.112828
	d = datetime.datetime.utcnow()
	thirty_minutes = datetime.timedelta(hours = 0.5)
	for i in range(48):
		timestamp = d.ctime()
		altitude_deg = GetAltitude(latitude_deg, longitude_deg, d)
		azimuth_deg = GetAzimuth(latitude_deg, longitude_deg, d)
		power = GetRadiationDirect(d, altitude_deg)
		if (altitude_deg > 0):
			print timestamp, "UTC", altitude_deg, azimuth_deg, power
		d = d + thirty_minutes

def EquationOfTime(day):
	b = (2 * math.pi / 364.0) * (day - 81)
	return (9.87 * math.sin(2 *b)) - (7.53 * math.cos(b)) - (1.5 * math.sin(b))

def GetAberrationCorrection(r): 	# r is earth radius vector [astronomical units]
	return -20.4898/(3600.0 * r)

def GetAirMassRatio(altitude_deg):
	# from Masters, p. 412
	# warning: pukes on input of zero
	return (1/math.sin(math.radians(altitude_deg)))

def GetAltitude(latitude_deg, longitude_deg, utc_datetime):

# expect 19 degrees for solar.GetAltitude(42.364908,-71.112828,datetime.datetime(2007, 2, 18, 20, 13, 1, 130320))

	day = GetDayOfYear(utc_datetime)
	declination_rad = math.radians(GetDeclination(day))
	latitude_rad = math.radians(latitude_deg)
	hour_angle = GetHourAngle(utc_datetime, longitude_deg)

	first_term = math.cos(latitude_rad) * math.cos(declination_rad) * math.cos(math.radians(hour_angle))
	second_term = math.sin(latitude_rad) * math.sin(declination_rad)
	return math.degrees(math.asin(first_term + second_term))

def GetApparentExtraterrestrialFlux(day):
	# from Masters, p. 412
	return 1160 + (75 * math.sin((360/365) * (day - 275)))

def GetApparentSiderealTime(julian_day, jme, nutation):
	return GetMeanSiderealTime(julian_day) + nutation['longitude'] * math.cos(GetTrueEclipticObliquity(jme, nutation))

def GetApparentSunLongitude(geocentric_longitude, nutation, ab_correction):
	return geocentric_longitude + nutation['longitude'] + ab_correction

def GetArgumentOfLatitudeOfMoon(jce):
	return 93.27191 + (483202.017538 * jce) - (0.0036825 * pow(jce, 2)) + (pow(jce, 3) / 327270.0)

def GetAzimuth(latitude_deg, longitude_deg, utc_datetime):
# expect -50 degrees for solar.GetAzimuth(42.364908,-71.112828,datetime.datetime(2007, 2, 18, 20, 18, 0, 0))
	day = GetDayOfYear(utc_datetime)
	declination_rad = math.radians(GetDeclination(day))
	latitude_rad = math.radians(latitude_deg)
	hour_angle_rad = math.radians(GetHourAngle(utc_datetime, longitude_deg))
	altitude_rad = math.radians(GetAltitude(latitude_deg, longitude_deg, utc_datetime))

	azimuth_rad = math.asin(math.cos(declination_rad) * math.sin(hour_angle_rad) / math.cos(altitude_rad))

	if(math.cos(hour_angle_rad) >= (math.tan(declination_rad) / math.tan(latitude_rad))):
		return math.degrees(azimuth_rad)
	else:
		return (180 - math.degrees(azimuth_rad))

def GetCoefficient(jme, constant_array):
	total = 0
	for i in range(len(constant_array)):
		total = total + (constant_array[i-1][0] * math.cos(constant_array[i-1][1] + (constant_array[i-1][2] * jme)))
	return total

def GetDayOfYear(utc_datetime):
	year_start = datetime.datetime(utc_datetime.year, 1, 1,)
	delta = (utc_datetime - year_start)
	return delta.days

def GetDeclination(day):
	return 23.45 * math.sin((2 * math.pi / 365.0) * (day - 81))

def GetEquatorialHorizontalParallax(    radius_vector):
	return 8.794 / (3600 / radius_vector)

def GetFlattenedLatitude(latitude):
	latitude_rad = math.radians(latitude)
	return math.degrees(math.atan(0.99664719 * math.tan(latitude_rad)))

def GetGeocentricLatitude(jme):
	return -1 * GetHeliocentricLatitude(jme)

def GetGeocentricLongitude(jme):
	return (GetHeliocentricLongitude(jme) + 180) % 360

def GetGeocentricSunDeclination(apparent_sun_longitude, true_ecliptic_obliquity, geocentric_latitude):
	apparent_sun_longitude_rad = math.radians(apparent_sun_longitude)
	true_ecliptic_obliquity_rad = math.radians(true_ecliptic_obliquity)
	geocentric_latitude_rad = math.radians(geocentric_latitude)

	a = math.sin(geocentric_latitude_rad) * math.cos(true_ecliptic_obliquity_rad)
	b = math.cos(geocentric_latitude_rad) * math.sin(true_ecliptic_obliquity_rad) * math.sin(apparent_sun_longitude_rad)
	delta = math.asin(a + b)
	return math.degrees(delta)

def GetGeocentricSunRightAscension(apparent_sun_longitude, true_ecliptic_obliquity, geocentric_latitude):
	apparent_sun_longitude_rad = math.radians(apparent_sun_longitude)
	true_ecliptic_obliquity_rad = math.radians(true_ecliptic_obliquity)
	geocentric_latitude_rad = math.radians(geocentric_latitude)

	a = math.sin(apparent_sun_longitude_rad) * math.cos(true_ecliptic_obliquity_rad)
	b = math.tan(geocentric_latitude_rad) * math.sin(true_ecliptic_obliquity_rad)
	c = math.cos(apparent_sun_longitude_rad)
	alpha = math.atan2((a - b),  c)
	return math.degrees(alpha) % 360

def GetHeliocentricLatitude(jme):
	b0 = GetCoefficient(jme, constants.B0)
	b1 = GetCoefficient(jme, constants.B1)
	return math.degrees((b0 + (b1 * jme)) / pow(10, 8))

def GetHeliocentricLongitude(jme):
	l0 = GetCoefficient(jme, constants.L0)
	l1 = GetCoefficient(jme, constants.L1)
	l2 = GetCoefficient(jme, constants.L2)
	l3 = GetCoefficient(jme, constants.L3)
	l4 = GetCoefficient(jme, constants.L4)
	l5 = GetCoefficient(jme, constants.L5)

	l = (l0 + (l1 * jme) + (l2 * pow(jme, 2)) + (l3 * pow(jme, 3)) + (l4 * pow(jme, 4)) + (l5 * pow(jme, 5))) / pow(10, 8)
	return math.degrees(l) % 360

def GetHourAngle(utc_datetime, longitude_deg):
	solar_time = GetSolarTime(longitude_deg, utc_datetime)
	return 15 * (12 - solar_time)

def GetIncidenceAngle(topocentric_zenith_angle, slope, slope_orientation, topocentric_azimuth_angle):
    tza_rad = math.radians(topocentric_zenith_angle)
    slope_rad = math.radians(slope)
    so_rad = math.radians(slope_orientation)
    taa_rad = math.radians(topocentric_azimuth_angle)
    return math.degrees(math.acos(math.cos(tza_rad) * math.cos(slope_rad) + math.sin(slope_rad) * math.sin(tza_rad) * math.cos(taa_rad - math.pi - so_rad)))

def GetJulianCentury(julian_day):
	"""You get the Julian century or Julian ephemeris century back, depending on whether you supply
	the Julian day or the Julian ephemeris day."""
	return (julian_day - 2451545.0) / 36525.0

def GetJulianDay(utc_datetime):	# based on NREL/TP-560-34302 by Andreas and Reda
				# does not accept years before 0 because of bounds check on Python's datetime.year field
	year = utc_datetime.year
	month = utc_datetime.month
	if(month <= 2):		# shift to accomodate leap years?
		year = year - 1
		month = month + 12
	day = utc_datetime.day + (((utc_datetime.hour * 3600.0) + (utc_datetime.minute * 60.0) + utc_datetime.second) / 86400.0)
	gregorian_offset = 2 - math.floor(year / 100) + math.floor(math.floor(year / 100) / 4)
	julian_day = math.floor(365.25*(year + 4716)) + math.floor(30.6001 *(month + 1)) + day - 1524.5
	if (julian_day <= 2299160):
		return julian_day # before October 5, 1852
	else:
		return julian_day + gregorian_offset # after October 5, 1852

def GetJulianEphemerisDay(julian_day, delta_seconds):
	"""delta_seconds is value referred to by astronomers as Delta-T, defined as the difference between
	Dynamical Time (TD) and Universal Time (UT). In 2007, it's around 65 seconds.
	A list of values for Delta-T can be found here: ftp://maia.usno.navy.mil/ser7/deltat.data"""
	return julian_day + (delta_seconds / 86400.0)

def GetJulianEphemerisMillenium(julian_ephemeris_century):
	return (julian_ephemeris_century / 10.0)

def GetLongitudeOfAscendingNode(jce):
	return 125.04452 - (1934.136261 * jce) + (0.0020708 * pow(jce, 2)) + (pow(jce, 3) / 450000.0)

def GetLocalHourAngle(apparent_sidereal_time, longitude, geocentric_sun_right_ascension):
	return (apparent_sidereal_time + longitude - geocentric_sun_right_ascension) % 360

def GetMeanElongationOfMoon(jce):
	return 297.85036 + (445267.111480 * jce) - (0.0019142 * pow(jce, 2)) + (pow(jce, 3) / 189474.0)

def GetMeanAnomalyOfMoon(jce):
	return 134.96298 + (477198.867398 * jce) + (0.0086972 * pow(jce, 2)) + (pow(jce, 3) / 56250.0)

def GetMeanAnomalyOfSun(jce):
	return 357.52772 + (35999.050340 * jce) - (0.0001603 * pow(jce, 2)) - (pow(jce, 3) / 300000.0)

def GetMeanSiderealTime(julian_day):
	jc = GetJulianCentury(julian_day)
	sidereal_time =  280.46061837 + (360.98564736629 * (julian_day - 2451545.0)) + (0.000387933 * pow(jc, 2)) \
	- (pow(jc, 3) / 38710000)
	return sidereal_time % 360

def GetNutationAberrationXY(jce):
	y = constants.aberration_sin_terms
	x = []
	# order of 5 x.append lines below is important
	x.append(GetMeanElongationOfMoon(jce))
	x.append(GetMeanAnomalyOfSun(jce))
	x.append(GetMeanAnomalyOfMoon(jce))
	x.append(GetArgumentOfLatitudeOfMoon(jce))
	x.append(GetLongitudeOfAscendingNode(jce))
	sigmaxy = 0.0
	for j in range(len(x)):
		sigmaxy += x[j] * y[0][j]
	return sigmaxy

def GetNutation(jde):
	abcd = constants.nutation_coefficients
	jce = GetJulianCentury(jde)
	sigmaxy = GetNutationAberrationXY(jce)
	nutation_long = []
	nutation_oblique = []

	for i in range(len(abcd)):
		nutation_long.append((abcd[i][0] + (abcd[i][1] * jce)) * math.sin(math.radians(sigmaxy)))
		nutation_oblique.append((abcd[i][2] + (abcd[i][3] * jce)) * math.cos(math.radians(sigmaxy)))

	# 36000000 scales from 0.0001 arcseconds to degrees
	nutation = {'longitude' : sum(nutation_long)/36000000.0, 'obliquity' : sum(nutation_oblique)/36000000.0}

	return nutation

def GetOpticalDepth(day):
	# from Masters, p. 412
	return 0.174 + (0.035 * math.sin((360/365) * (day - 100)))

def GetParallaxSunRightAscension(projected_radial_distance, equatorial_horizontal_parallax, local_hour_angle, geocentric_sun_declination, projected_axial_distance):
	prd = projected_radial_distance
	ehp_rad = math.radians(equatorial_horizontal_parallax)
	lha_rad = math.radians(local_hour_angle)
	gsd_rad = math.radians(geocentric_sun_declination)
	pad = projected_axial_distance
	a = -1 * prd * math.sin(ehp_rad) * math.sin(lha_rad)
	b =  math.cos(gsd_rad) - pad * math.sin(ehp_rad) * math.cos(lha_rad)
	parallax = math.atan2(a, b)
	return math.degrees(parallax)

def GetProjectedRadialDistance(elevation, latitude):
	flattened_latitude_rad = math.radians(GetFlattenedLatitude(latitude))
	latitude_rad = math.radians(latitude)
	return math.cos(flattened_latitude_rad) + (elevation * math.cos(latitude_rad) / constants.earth_radius)

def GetProjectedAxialDistance(elevation, latitude):
	flattened_latitude_rad = math.radians(GetFlattenedLatitude(latitude))
	latitude_rad = math.radians(latitude)
	return 0.99664719 * math.sin(flattened_latitude_rad) + (elevation * math.sin(latitude_rad) / constants.earth_radius)
	
def GetRadiationDirect(utc_datetime, altitude_deg):
	# from Masters, p. 412
	day = GetDayOfYear(utc_datetime)
	flux = GetApparentExtraterrestrialFlux(day)
	optical_depth = GetOpticalDepth(day)
	air_mass_ratio = GetAirMassRatio(altitude_deg)
	return flux * math.exp(-1 * optical_depth * air_mass_ratio)

def GetRadiusVector(jme):
	r0 = GetCoefficient(jme, constants.R0)
	r1 = GetCoefficient(jme, constants.R1)
	r2 = GetCoefficient(jme, constants.R2)
	r3 = GetCoefficient(jme, constants.R3)
	r4 = GetCoefficient(jme, constants.R4)

	return (r0 + (r1 * jme) + (r2 * pow(jme, 2)) + (r3 * pow(jme, 3)) + (r4 * pow(jme, 4))) / pow(10, 8)

def GetRefractionCorrection(pressure_millibars, temperature_celsius, topocentric_elevation_angle):
    tea = topocentric_elevation_angle
    temperature_kelvin = temperature_celsius + 273.15
    a = pressure_millibars * 283.0 * 1.02
    b = 1010.0 * temperature_kelvin * 60.0 * math.tan(math.radians(tea + (10.3/(tea + 5.11))))
    return a / b

def GetSolarTime(longitude_deg, utc_datetime):
    day = GetDayOfYear(utc_datetime)
    return (((utc_datetime.hour * 60) + utc_datetime.minute + (4 * longitude_deg) + EquationOfTime(day))/60)

def GetTopocentricAzimuthAngle(topocentric_local_hour_angle, latitude, topocentric_sun_declination):
    tlha_rad = math.radians(topocentric_local_hour_angle)
    latitude_rad = math.radians(latitude)
    tsd_rad = math.radians(topocentric_sun_declination)
    a = math.sin(tlha_rad)
    b = math.cos(tlha_rad) * math.sin(latitude_rad) - math.tan(tsd_rad) * math.cos(latitude_rad)
    return 180.0 + math.degrees(math.atan2(a, b)) % 360

def GetTopocentricElevationAngle(latitude, topocentric_sun_declination, topocentric_local_hour_angle):
    latitude_rad = math.radians(latitude)
    tsd_rad = math.radians(topocentric_sun_declination)
    tlha_rad = math.radians(topocentric_local_hour_angle)
    return math.degrees(math.asin((math.sin(latitude_rad) * math.sin(tsd_rad)) + math.cos(latitude_rad) * math.cos(tsd_rad) * math.cos(tlha_rad)))

def GetTopocentricLocalHourAngle(local_hour_angle, parallax_sun_right_ascension):
    return local_hour_angle - parallax_sun_right_ascension

def GetTopocentricSunDeclination(geocentric_sun_declination, projected_axial_distance, equatorial_horizontal_parallax, parallax_sun_right_ascension, local_hour_angle):
    gsd_rad = math.radians(geocentric_sun_declination)
    pad = projected_axial_distance
    ehp_rad = math.radians(equatorial_horizontal_parallax)
    a = (math.sin(gsd_rad) - pad * math.sin(ehp_rad)) * math.cos(parallax_sun_right_ascension)
    b = math.cos(gsd_rad) - (pad * math.sin(ehp_rad) * math.cos(local_hour_angle))
    return math.degrees(math.atan2(a, b))

def GetTopocentricSunRightAscension(projected_radial_distance, equatorial_horizontal_parallax, local_hour_angle, projected_axial_distance,
        apparent_sun_longitude, true_ecliptic_obliquity, geocentric_latitude):
    gsd = GetGeocentricSunDeclination(apparent_sun_longitude, true_ecliptic_obliquity, geocentric_latitude)
    psra = GetParallaxSunRightAscension(projected_radial_distance, equatorial_horizontal_parallax, local_hour_angle, gsd, projected_axial_distance)
    gsra = GetGeocentricSunRightAscension(apparent_sun_longitude, true_ecliptic_obliquity, geocentric_latitude)
    return psra + gsra

def GetTopocentricZenithAngle(latitude, topocentric_sun_declination, topocentric_local_hour_angle, pressure_millibars, temperature_celsius):
    tea = GetTopocentricElevationAngle(latitude, topocentric_sun_declination, topocentric_local_hour_angle)
    return 90 - tea - GetRefractionCorrection(pressure_millibars, temperature_celsius, tea)

def GetTrueEclipticObliquity(jme, nutation):
	u = jme/10.0
	mean_obliquity = 84381.448 - (4680.93 * u) - (1.55 * pow(u, 2)) + (1999.25 * pow(u, 3)) \
	- (51.38 * pow(u, 4)) -(249.67 * pow(u, 5)) - (39.05 * pow(u, 6)) + (7.12 * pow(u, 7)) \
	+ (27.87 * pow(u, 8)) + (5.79 * pow(u, 9)) + (2.45 * pow(u, 10))
	return (mean_obliquity / 3600.0) + nutation['obliquity']
