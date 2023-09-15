INIT MASTER(S)
NASTRAN OP2NEW=0,SYSTEM(319)=1
ID dynamics,Femap
SOL SEMODES
CEND
  TITLE = a1
  ECHO = NONE
  DISPLACEMENT(PUNCH) = ALL
  SPCFORCE(PUNCH) = ALL
  METHOD = 1
  SPC = 1
BEGIN BULK
$ ***************************************************************************
$   Written by : Femap
$   Version    : 12.0.1a
$   Translator : MSC/MD Nastran
$   From Model : C:\Users\fschwa02\Desktop\Dynamics_Learning\dynamics_example.modfem
$   Date       : Tue Sep 24 08:22:07 2019
$   Output To  : C:\Users\fschwa02\Desktop\Dynamics_Learning\
$ ***************************************************************************
$
PARAM,PRGPST,YES
PARAM,POST,-1
PARAM,OGEOM,NO
PARAM,AUTOSPC,YES
PARAM,GRDPNT,0
PARAM,WTMASS,.0025901
EIGRL          1                       6       0                    MASS
CORD2C         1       0      0.      0.      0.      0.      0.      1.+FEMAPC1
+FEMAPC1      1.      0.      1.        
CORD2S         2       0      0.      0.      0.      0.      0.      1.+FEMAPC2
+FEMAPC2      1.      0.      1.        
$ Femap Constraint Set 1 : Fixed
SPC1           1  123456       1
$ Femap Property 1 : Stiff Rod
$ Femap PropShape 1 : 5,0,1.,0.,0.,0.,0.,0.
$ Femap PropOrient 1 : 5,0,0.,1.,2.,3.,4.,-1.,0.,0.
PBEAM          1       13.141593 .785398 .785398      0.1.569474      0.+       
+             0.     -1.      1.      0.      0.      1.     -1.      0.+       
+           YESA      1.                                                +       
+       .8861769.8861772                                                        
$ Femap Material 1 : A286 Alloy Steel-Solution Treated and Aged,   Min Properties
MAT1           1  2.91+7             .31    .287    9.-6     70.        +       
+        130000.  85000.  85000.
MAT4           11.6667-442.46979    .287                        
GRID           1       0      0.      0.      0.       0
GRID           2       0      3.      0.      0.       0
CONM2          2       2       0     10.      0.      0.      0.                
CBEAM          3       1       1       2      0.      1.      0.
ENDDATA
