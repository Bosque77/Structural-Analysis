Sub Main()
    ' Step 1: Connect to Femap
    Dim femapApp As femap.model
    Set femapApp = feFemap()

    If femapApp Is Nothing Then
        femapApp.feAppMessage(femap.zMessageColor.FCM_ERROR, "FEMAP connection failed.")
        Exit Sub
    End If

    ' Step 2: Display a prompt for the user to select elements
    Dim selectedElements As femap.Set
    Set selectedElements = femapApp.feSet
    If selectedElements.Select(femap.zDataType.FT_ELEM, True, "Select elements:") <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage(femap.zMessageColor.FCM_ERROR, "No elements selected or selection cancelled.")
        Exit Sub
    End If

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Selected element count: " & selectedElements.Count)

    ' Step 3: Find all connected elements, excluding spring elements
    Dim springsToRemove As femap.Set
    Set springsToRemove = femapApp.feSet
    springsToRemove.AddRule(femap.zElementType.FET_L_SPRING, femap.zGroupDefinitionType.FGD_ELEM_BYTYPE)
    Dim previousCount As Integer
    previousCount = 0
    Dim connectedElements As femap.Set
    Set connectedElements = femapApp.feSet

    Dim elementID As Integer
    elementID = selectedElements.First

    While elementID > 0
        connectedElements.Add(elementID)
        ' Repeat process until no new elements are added to the set
        Do
            previousCount = connectedElements.Count
            connectedElements.AddConnectedElements()
            connectedElements.RemoveSet(springsToRemove.ID) ' Remove spring elements
        Loop While connectedElements.Count > previousCount

        ' Get the next element ID
        elementID = selectedElements.Next
    Wend

    ' Step 4: Create a unique group for these elements
    Dim group_number As Integer
    group_number = femapApp.feGroup.NextEmptyID
    Dim resultGroup As femap.Group
    Set resultGroup = femapApp.feGroup
    resultGroup.title = "Isolated Connected Elements " & CStr(group_number)
    resultGroup.SetAdd(femap.zDataType.FT_ELEM, connectedElements.ID)
    resultGroup.Put(femapApp.feGroup.NextEmptyID)
    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "A new group of connected elements has been created.")

    ' Optional: Refresh the Femap UI
    femapApp.feViewRegenerate(0)

    femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Process completed successfully.")
End Sub
