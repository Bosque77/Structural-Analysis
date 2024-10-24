Sub Main()
    ' Step 1: Connect to Femap
    Dim femapApp As femap.model
    Set femapApp = feFemap()

    If femapApp Is Nothing Then
        femapApp.feAppMessage(femap.zMessageColor.FCM_ERROR, "FEMAP connection failed.")
        Exit Sub
    End If

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Connected to Femap version: " & femapApp.feAppVersion)

    ' Step 3: Find spring elements
    Dim springElements As femap.Set
    Set springElements = femapApp.feSet
    springElements.AddRule(femap.zElementType.FET_L_SPRING, femap.zGroupDefinitionType.FGD_ELEM_BYTYPE)

    ' Step 4: Loop through each element in springElements to find associated nodes
    Dim nodeSet As femap.Set
    Set nodeSet = femapApp.feSet

	Dim elemID As Integer
	elemID = springElements.First
	While elemID > 0
	    Dim elem As femap.Elem
	    Set elem = femapApp.feElem
	    If elem.Get(elemID) = femap.zReturnCode.FE_OK Then
	        For Each nodeID In elem.Nodes
	            nodeSet.Add(nodeID)
	        Next
	    End If
	    elemID = springElements.Next
	Wend

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Number of nodes added to the node set: " & nodeSet.Count)

    ' Step 5: Create a new set for connected elements
    Dim copyOfSpringElements As femap.Set
    Set copyOfSpringElements = femapApp.feSet
    copyOfSpringElements.AddSet(springElements.ID)
    copyOfSpringElements.AddConnectedElements()

    ' Step 6: Remove original spring elements from the copied set to leave only associated and connected elements
    copyOfSpringElements.RemoveSet(springElements.ID)
    Dim plateElements As femap.Set
    Set plateElements = femapApp.feSet
    plateElements.AddSet(copyOfSpringElements.ID)

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Number of connected elements: " & plateElements.Count)

    ' Step 7: Create a group for the nodes and plate elements
    Dim combinedGroup As femap.group
    Set combinedGroup = femapApp.feGroup
    combinedGroup.title = "Isolated_Joint_Elements"
    combinedGroup.SetAdd(femap.zDataType.FT_NODE, nodeSet.ID)
    combinedGroup.SetAdd(femap.zDataType.FT_ELEM, plateElements.ID)
    combinedGroup.Put(femapApp.feGroup.NextEmptyID) ' Save the group with a unique ID

    ' Optional: Refresh the Femap UI
    femapApp.feViewRegenerate(0) ' Regenerate all views

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Process completed successfully.")
End Sub
