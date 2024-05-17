Sub Main()
    ' Step 1: Connect to Femap
    Dim femapApp As femap.model
    Set femapApp = feFemap()

    If femapApp Is Nothing Then
        femapApp.feAppMessage(femap.zMessageColor.FCM_ERROR, "FEMAP connection failed.")
        Exit Sub
    End If

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Connected to Femap version: " & femapApp.feAppVersion)

    ' Step 2: Prompt user to select a group
    Dim selectedGroups As femap.Set
    Set selectedGroups = femapApp.feSet
    Dim selectedGroup As Long
    If selectedGroups.SelectID(femap.zDataType.FT_GROUP, "Select group:", selectedGroup) <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage(femap.zMessageColor.FCM_ERROR, "No groups selected or selection cancelled.")
        Exit Sub
    End If

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Group " & selectedGroup & " selected.")

    ' Step 3: Create a set for spring elements within the selected group
    Dim springElements As femap.Set
    Set springElements = femapApp.feSet
    springElements.AddRule(femap.zElementType.FET_L_SPRING, femap.zGroupDefinitionType.FGD_ELEM_BYTYPE)

    Dim groupElements As femap.Set
    Set groupElements = femapApp.feSet
    groupElements.AddGroup(femap.zDataType.FT_ELEM, selectedGroup)

    Dim commonSpringElements As femap.Set
    Set commonSpringElements = femapApp.feSet
    commonSpringElements.AddSet(springElements.ID)
    commonSpringElements.RemoveNotCommon(groupElements.ID)

    ' Step 4: Create a node set to find associated nodes
    Dim nodeSet As femap.Set
    Set nodeSet = femapApp.feSet

    Dim elemID As Integer
    elemID = commonSpringElements.First
    While elemID > 0
        Dim elem As femap.Elem
        Set elem = femapApp.feElem
        If elem.Get(elemID) = femap.zReturnCode.FE_OK Then
            For Each nodeID In elem.Nodes
                nodeSet.Add(nodeID)
            Next
        End If
        elemID = commonSpringElements.Next
    Wend

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Number of nodes added to the node set: " & nodeSet.Count)

    ' Step 5: Make a copy of the springElements set and find connected elements
    Dim copyOfSpringElements As femap.Set
    Set copyOfSpringElements = femapApp.feSet
    copyOfSpringElements.AddSet(commonSpringElements.ID)
    copyOfSpringElements.AddConnectedElements()

    ' Step 6: Remove original spring elements from the copied set to leave only associated and connected elements
    copyOfSpringElements.RemoveSet(springElements.ID)
    Dim plateElements As femap.Set
    Set plateElements = femapApp.feSet
    plateElements.AddSet(copyOfSpringElements.ID)

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Number of connected elements: " & plateElements.Count)

    ' Step 7: Create a group for the nodes and plate elements
    Dim nextID As Integer
    nextID = femapApp.feGroup.NextEmptyID
    Dim combinedGroup As femap.group
    Set combinedGroup = femapApp.feGroup
    combinedGroup.title = "Isolated_Joint_Elements_" & nextID
    combinedGroup.SetAdd(femap.zDataType.FT_NODE, nodeSet.ID)
    combinedGroup.SetAdd(femap.zDataType.FT_ELEM, plateElements.ID)
    combinedGroup.Put(nextID) ' Save the group with a unique ID

    ' Optional: Refresh the Femap UI
    femapApp.feViewRegenerate(0) ' Regenerate all views

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Process completed successfully.")
End Sub
