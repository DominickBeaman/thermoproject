import matplotlib
import psychrolib
import pyromat as pm
import ht
from pyfluids import Fluid, FluidsList, Input
import math

# helper function for getting into units better suited to our problem
def getCelciusFromFahrenheit(tf):
    return (tf - 32) / 1.8

def getSquMeterFromSquFt(squFt):
    return squFt * 0.092903

def celciusToKelvin(cel):
    return cel + 273.15

def getMeterFromFeet(feet):
    return feet * 0.3048

# Define Functions that will be used throughout the code

h2o = pm.get("ig.H2O")
air = pm.get("ig.air")

# For calculating Psat given temperature| temperature in K, out in kPa
def getPsat(temperature):
    return h2o.p(T=temperature)

# For determining current water pressure| temperature in K, relativeHumidity in %, out in kPa
def getWaterPressure(temperature, relativeHumidity):
    return relativeHumidity / 100 * getPsat(temperature)

Ra = 8.314

# for getting mass flow rate of water| temperature in K, relativeHumidity in %, volumeFlow in m^3/s, out in kg/s 
def getWaterMass(temperature, relativeHumidity, volumeFlow):
    return getWaterPressure(temperature, relativeHumidity) * volumeFlow * h2o.mw() / Ra / temperature

# for getting mass flow rate| temperature in K, dryAirPressure in kPa, volumeFlow in m^3/s, out in kg/s 
def getDryAirMass(temperature, dryAirPressure, volumeFlow):
    return dryAirPressure * volumeFlow * h2o.mw() / Ra / temperature

# Used for getting the dry air pressure| pressure in kPa, waterPressure in kPa, out in kPa
def getDryAirPressure(pressure, waterPressure):
    return pressure - waterPressure

# Used for getting the specific humidity| pressure in kPa, waterPressure in kPa, out in 0 to 1
def getSpecificHumidity(pressure, waterPressure):
    return 0.622 * waterPressure / (pressure - waterPressure)


# For getting water enthalpy| temperature in K, pressure in kPa, out in kJ/kmol
def getWaterEnthalpy(temperature, pressure):
    return h2o.h(T=temperature, p=pressure)

# For getting dry air enthalpy| temperature in K, pressure in kPa, out in kJ/kmol
def getDryAirEnthalpy(temperature, pressure):
    return air.h(T=temperature, p=pressure)
    
# For getting water enthalpy flow| temperature in K, pressure in kPa, massFlow in kg/s, out in kJ/s
def getWaterEnthalpyFlow(temperature, pressure, massFlow):
    return getWaterEnthalpy(temperature, pressure) / h2o.mw() * massFlow

# For getting dry air enthalpy flow| temperature in K, pressure in kPa, massFlow in kg/s, out in kJ/s
def getDryAirEnthalpyFlow(temperature, pressure, massFlow):
    return getDryAirEnthalpy(temperature, pressure) / air.mw() * massFlow
    
# For determining required refrigerant| qout in kW, out in tons of refrigerant
def getRequiredRefrigerant(qout):
    return .2893 * qout

def getDryAirMassFlowRate(pressure, vaporpressure, volumeflowrate, temperature):
    return volumeflowrate / (air.v(T=temperature) + getSpecificHumidity(pressure, vaporpressure) * h2o.v(T=temperature))

def getVaporMassFlowRate(pressure, vaporpressure, volumeflowrate, temperature):
    return volumeflowrate / (air.v(T=temperature) / getSpecificHumidity(pressure, vaporpressure) + h2o.v(T=temperature))

# Define initial variables that will be used throughout the whole of the script
# Eventually some if not all will be expanded to be variable inputs for making graphs


# Values related to the game
gameLength = 2.5 # hours

# Stadium size information
stadiumFloorArea = getSquMeterFromSquFt(675000) # m^2
stadiumSizeRatio = 85/200
stadiumLength = math.sqrt(stadiumFloorArea / (1 + stadiumSizeRatio)) # m
stadiumWidth = stadiumFloorArea / stadiumLength # m
arenaWidth = getMeterFromFeet(85 * 10 / 1.5)
arenaLength = getMeterFromFeet(200 * 12.5 / 2.5)
stadiumHeight = 15 # m (Guess for now cant find any actual data)

print("Stadium Floor Area: " + str(stadiumFloorArea) + "m^2 , Stadium Length: " + str(stadiumLength) + "m , Stadium Width: " + str(stadiumWidth) + "m")

# Desired conditions to be mainted throughout the game
desiredHumidity = 35 # %
desiredTemperature = getCelciusFromFahrenheit(63) # C
airPressure = 84.0 # Kpa

# HVAC information
hvacVolumeFlowRate = 724000 / 60 * 0.03# m^3 / s
print("Air Flow: " + str(hvacVolumeFlowRate) + "m^3/s")

# Ice rink related values
rinkArea = getSquMeterFromSquFt(19000) # m^2
rinkLength = getMeterFromFeet(200) # m
rinkIceTemperature = getCelciusFromFahrenheit(22) # C
rinkAirSpeedAdjustment = 10
rinkAirSpeed = hvacVolumeFlowRate / (arenaWidth * stadiumHeight) * rinkAirSpeedAdjustment
print("Air Speed: " + str(rinkAirSpeed) + "m/s")

# Related to determining the heat loss through the ice
filmTemperature = (desiredTemperature + rinkIceTemperature) / 2 

# To get air fluid properties at film temp
airFluid = Fluid(FluidsList.Air).with_state(Input.temperature(filmTemperature), Input.pressure(airPressure * 1000))
airDensity = airFluid.density # kg/m^3
airThermalConduction = airFluid.conductivity
airKinematicViscosity = airFluid.kinematic_viscosity # Std
airReynoldsNumber = rinkAirSpeed * rinkLength / airKinematicViscosity
airPrandtlNumber = airFluid.prandtl
rinkNu = ht.conv_external.Nu_external_horizontal_plate(airReynoldsNumber, airPrandtlNumber)
rinkConvectionCoe = rinkNu * airThermalConduction / rinkLength
print("Ice Convection Coefficient: " + str(rinkConvectionCoe))


# Goal of section
rinkConvection = rinkArea * rinkConvectionCoe * (desiredTemperature - rinkIceTemperature) / 1000 # kW
print("Rink Heat Loss: " + str(rinkConvection) + " kW")


# Standard atmospheric conditions
airTemperature = 40 # C
airHumidity = 22 # %

# Values related to the people
amountPeople = 18000 # Persons
surfaceAreaPerson = 1.8 # m^2
heatGenerationPerson = 58.2 # W/m^2
waterBreathGenerationPerson = 16.7 / 3600# g/s
waterSweatGenerationPerson = 3.5 * 1000 / 3600 # g/s
playerHeatGeneration = 1000 # W/m^2
numberPlayers = 6 * 12

# Related to hvac analysis
mDotPeople = (waterBreathGenerationPerson * amountPeople + numberPlayers * waterSweatGenerationPerson) / 1000
qDotPeople = surfaceAreaPerson * heatGenerationPerson + playerHeatGeneration * numberPlayers / 1000
qDotIce = -rinkConvection
print("People Water Production: " + str(mDotPeople) + " kg/s")

stateOneVaporPressure = getWaterPressure(celciusToKelvin(airTemperature), airHumidity / 100)
stateOneAirPressure = getDryAirPressure(airPressure, stateOneVaporPressure)
print("State One, Vapor Pressure: " + str(stateOneVaporPressure) + " kPa")

dryAirMassFlowRate = getDryAirMassFlowRate(airPressure, stateOneVaporPressure, hvacVolumeFlowRate, celciusToKelvin(airTemperature))
stateOneVaporFlowRate = getVaporMassFlowRate(airPressure, stateOneVaporPressure, hvacVolumeFlowRate, celciusToKelvin(airTemperature))
print("Dry Air Flow Rate: " + str(dryAirMassFlowRate) + " kg/s, Vapor Flow Rate: " + str(stateOneVaporFlowRate) + " kg/s")

stateTwoVaporPressure = getWaterPressure(celciusToKelvin(desiredTemperature), desiredHumidity / 100)
stateTwoAirPressure = getDryAirPressure(airPressure, stateTwoVaporPressure)
print("State Two, Vapor Pressure: " + str(stateTwoVaporPressure) + " kPa")

stateTwoVaporFlowRate = getVaporMassFlowRate(airPressure, stateTwoVaporPressure, hvacVolumeFlowRate, celciusToKelvin(desiredTemperature))
print("State Two Vapor Flow Rate: " + str(stateOneVaporFlowRate) + " kg/s")

mDotAdditive = stateTwoVaporFlowRate - stateOneVaporFlowRate - mDotPeople
print("Water Adjustment Needed: " + str(mDotAdditive) + " kg/s")

inletEnthalpyDot = getWaterEnthalpyFlow(celciusToKelvin(airTemperature), airPressure, stateOneVaporFlowRate) + getWaterEnthalpyFlow(celciusToKelvin(desiredTemperature), airPressure, mDotPeople) + getWaterEnthalpyFlow(300, airPressure, mDotAdditive) + getDryAirEnthalpyFlow(celciusToKelvin(airTemperature), airPressure, dryAirMassFlowRate)
outletEnthalpyDot = getWaterEnthalpyFlow(celciusToKelvin(desiredTemperature), airPressure, stateTwoVaporFlowRate) + getDryAirEnthalpyFlow(celciusToKelvin(desiredTemperature), airPressure, dryAirMassFlowRate)

qNetDot = outletEnthalpyDot - inletEnthalpyDot - qDotPeople + qDotIce
qNet = qNetDot * gameLength * 3600

energyCost = 0.1 # $ / kW-h
totalCost = abs(qNetDot) * gameLength * energyCost 

print("Energy Required For A Game: " + str(qNet) + " kJ, " + str(qNetDot) + " kW, with total cost of " + str(totalCost) + "$")