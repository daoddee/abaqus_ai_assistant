from abaqus import *
from abaqusConstants import *
import os
from caeModules import *
from driverUtils import executeOnCaeStartup
executeOnCaeStartup()
if os.path.exists('C:/Mac/Home/Desktop/abaqus_ai/abaqus_ai_assistant/backend/backend/current_model.cae'):
    openMdb('C:/Mac/Home/Desktop/abaqus_ai/abaqus_ai_assistant/backend/backend/current_model.cae')
else:
    mdb.Model(name='NewModel')
    mdb.saveAs('C:/Mac/Home/Desktop/abaqus_ai/abaqus_ai_assistant/backend/backend/current_model.cae')
from abaqus import *
from abaqusConstants import *
import regionToolset
import displayGroupMdbToolset as dgm
import part

# Create a new model database
mdb.Model(name='BeamModel', modelType=STANDARD_EXPLICIT)

# Get the current model
myModel = mdb.models['BeamModel']

# Create a part
myBeam = myModel.Part(name='Beam', dimensionality=THREE_D, type=DEFORMABLE_BODY)

# Create sketch for beam
mySketch = myModel.ConstrainedSketch(name='BeamSketch', sheetSize=200)

# Define beam dimensions
length = 1800.0
height = 200.0 
width = 100.0 

# Draw the beam
mySketch.rectangle(point1=(0.0, 0.0), point2=(length, height))

# Create the beam from sketch
myBeam.BaseSolidExtrude(sketch=mySketch, depth=width)

# Delete sketch as it is no longer needed
del myModel.sketches['BeamSketch']

# Create Material
myMaterial = myModel.Material(name='Steel')
elasticProperties = (209000, 0.3)
myMaterial.Elastic(table=(elasticProperties, ))

# Create Solid Section
mySection = myModel.HomogeneousSolidSection(name='BeamSection', material='Steel', thickness=None)

# Assign section to the part
region = (myBeam.cells,)
myBeam.SectionAssignment(region=region, sectionName='BeamSection')

# Generate Mesh
myBeam.seedPart(size=20.0, deviationFactor=0.1, minSizeFactor=0.1)
myBeam.generateMesh()

# Refresh the viewport
session.viewports['Viewport: 1'].forceRefresh()



Please ensure that the script is placed in the same directory as Abaqus, or adapt the import route of 'mdb' properly. Also note that to execute the script Abaqus should be open and you need to run the script in the Abaqus command line tool.
mdb.save()

session.viewports['Viewport: 1'].setValues(displayedObject=mdb.models['NewModel'].parts['BeamPart'])
