Sub Main()
    Dim femapApp As femap.model

    ' Connect to FEMAP
    On Error GoTo ConnectError
    Set femapApp = GetObject(, "femap.model")
    On Error GoTo 0

    If femapApp Is Nothing Then
        MsgBox "FEMAP connection failed."
        Exit Sub
    End If

    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Connected to FEMAP version: " & femapApp.feAppVersion

    ' Prompt user to select a surface
    Dim surfSet As femap.Set
    Set surfSet = femapApp.feSet

    If surfSet.Select(femap.zDataType.FT_SURFACE, True, "Select a surface for constraints") <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Surface selection failed or canceled."
        Exit Sub
    End If

    If surfSet.Count <> 1 Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Please select exactly one surface."
        Exit Sub
    End If

    Dim surfID As Long
    surfID = surfSet.First
    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Selected surface ID: " & surfID

    ' Prompt user to select nodes
    Dim nodeSet As femap.Set
    Set nodeSet = femapApp.feSet

    If nodeSet.Select(femap.zDataType.FT_NODE, True, "Select nodes for constraints") <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Node selection failed or canceled."
        Exit Sub
    End If

    If nodeSet.Count = 0 Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "No nodes selected."
        Exit Sub
    End If

    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Selected " & nodeSet.Count & " nodes."

    ' Get the surface object
    Dim surf As femap.Surface
    Set surf = femapApp.feSurface

    If surf.Get(surfID) <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to get surface ID " & surfID
        Exit Sub
    End If

    ' Get the node object
    Dim node As femap.Node
    Set node = femapApp.feNode

    ' Create constraint set object
    Dim constraint As femap.BCSet
    Set constraint = femapApp.feBCSet

    ' Create a new constraint set
    Dim constraintID As Long
    constraintID = constraint.NextEmptyID  ' Use object's built-in method
    constraint.ID = constraintID
    constraint.title = "Surface-Node Constraints"
    constraint.active = True
    constraint.Put(constraintID)

    ' Create a new constraint definition
    Dim bcDef As femap.BCDefinition
    Set bcDef = femapApp.feBCDefinition
    
    Dim bcDefID As Long
    bcDefID = bcDef.NextEmptyID  ' Use object's built-in method
    bcDef.ID = bcDefID
    bcDef.title = "Surface-Node Enforced Displacement"
    bcDef.Put(bcDefID)

    ' Process each selected node
    Dim nodeID As Long
    Dim nodeCoord(2) As Double
    Dim nearestPoint(2) As Double
    Dim paramCoord(1) As Double
    Dim normal(2) As Double
    Dim distance As Double
    Dim constraintCount As Long
    
    constraintCount = 0
    nodeID = nodeSet.First
    
    Do While nodeID > 0
        ' Get node coordinates
        If node.Get(nodeID) = femap.zReturnCode.FE_OK Then
            nodeCoord(0) = node.x
            nodeCoord(1) = node.y
            nodeCoord(2) = node.z
            
            ' Find nearest point on surface
            If surf.NearestPoint(nodeCoord, nearestPoint, paramCoord, normal, distance) = femap.zReturnCode.FE_OK Then
                ' Create constraint direction
                Dim bcDir As Object
                Set bcDir = femapApp.feBCDir
                
                Dim bcDirID As Long
                bcDirID = bcDir.NextEmptyID  ' Use object's built-in method
                bcDir.ID = bcDirID
                bcDir.type = 0  ' 0 corresponds to BCDT_XYZ (XYZ directions)
                bcDir.x = 1     ' Enable X direction
                bcDir.y = 1     ' Enable Y direction
                bcDir.z = 1     ' Enable Z direction
                bcDir.rx = 0    ' Disable rotation X
                bcDir.ry = 0    ' Disable rotation Y
                bcDir.rz = 0    ' Disable rotation Z
                bcDir.Put(bcDirID)
                
                ' Create the constraint object
                Dim bco As Object
                Set bco = femapApp.feBCObject
                
                Dim bcoID As Long
                bcoID = bco.NextEmptyID  ' Use object's built-in method
                bco.ID = bcoID
                bco.setID = constraintID
                bco.defID = bcDefID
                bco.dirID = bcDirID
                bco.entityID = nodeID
                bco.entityType = 1  ' 1 corresponds to BCET_NODE (node entity)
                
                ' Set the enforced displacement values to connect to the nearest point
                bco.value1 = nearestPoint(0) - nodeCoord(0)  ' X displacement
                bco.value2 = nearestPoint(1) - nodeCoord(1)  ' Y displacement
                bco.value3 = nearestPoint(2) - nodeCoord(2)  ' Z displacement
                
                If bco.Put(bcoID) = femap.zReturnCode.FE_OK Then
                    constraintCount = constraintCount + 1
                    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Created constraint for node " & nodeID & " (distance: " & Format(distance, "0.000") & ")"
                Else
                    femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to create constraint for node " & nodeID
                End If
            Else
                femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to find nearest point on surface for node " & nodeID
            End If
        Else
            femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to get node " & nodeID
        End If
        
        nodeID = nodeSet.Next
    Loop
    
    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Created " & constraintCount & " enforced displacement constraints."
    Exit Sub
    
ConnectError:
    MsgBox "Error connecting to FEMAP: " & Err.Description
End Sub