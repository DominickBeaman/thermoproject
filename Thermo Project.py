import matplotlib
import psychrolib
import pyromat as pm

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

# Define initial variables that will be used throughout the whole of the script
# Eventually some if not all will be expanded to be variable inputs for making graphs

# Values related to the people
amountPeople = 18000 # Persons
surfaceAreaPerson = 1.8 # m^2
heatGenerationPerson = 58.2 # W/m^2
waterGenerationPerson = 16.7 # g/hour

# Values related to the game
gameLength = 2.5 # hours

# Values related to the ice rink
rinkConvection = 0 # Lookup
rinkArea = 0 # Lookup

# Desired conditions to be mainted throughout the game
desiredHumidity = 30 # %
desiredTemperature = 25 + 273.15 # K

# Standard atmospheric conditions
airTemperature = 40 + 237.15 # K
airHumidity = 80 # %

print(getDryAirEnthalpy(298, 99))