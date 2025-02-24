I'm not sure what you mean by "random dimensions". A cube by definition would have equal length, width, and height. However, I will create a cube of dimensions 2 meters each in Abaqus script. Please note that Abaqus works in millimeters (mm), not meters (m), so we need to convert this to mm.

``` python
from abaqus import *
from abaqusConstants import *

# Define the session
session = mdb.JobFromInputFile(name='Job-Cube', 
                               inputFileName='Cube.inp')
s = session.sessionId()

c = mdb.models[s].ConstrainedSketch(name='__profile__', 
                                    sheetSize=2000.0)

session.modelDB[s].sketches['__profile__'].sketchOptions.setValues(
    decimalPlaces=4, gridSpacing=50.0)

# Draw the cube (a 2m x 2m x 2m cube is 2000mm x 2000mm x 2000mm)
c.rectangle(point1=(0.0, 0.0), point2=(2000.0, 2000.0))

p = mdb.models[s].Part(name='Cube', dimensionality=THREE_D, 
                       type=DEFORMABLE_BODY)

p.BaseSolidExtrude(sketch=c, depth=2000.0)

del mdb.models[s].sketches['__profile__']
```

This script creates a cube using the `BaseSolidExtrude` method which is ideal when you are working with simple 3D shapes like a cube. 

If you need to create a cube with random dimensions, you'll need to clarify what you mean by "random dimensions". But bear in mind that a cube has all three dimensions to be same, otherwise it won't be a cube.