
from abaqus import *
from abaqusConstants import *

session.viewports['Viewport: 1'].setValues(displayedObject=None)
mdb.models['Model-1'].ConstrainedSketch(name='__profile__', sheetSize=200.0)
mdb.models['Model-1'].sketches['__profile__'].rectangle(point1=(0, 0), point2=(1, 1))
mdb.models['Model-1'].Part(dimensionality=THREE_D, name='Cube', type=DEFORMABLE_BODY)
mdb.models['Model-1'].parts['Cube'].BaseSolidExtrude(sketch=mdb.models['Model-1'].sketches['__profile__'], depth=1.0)
