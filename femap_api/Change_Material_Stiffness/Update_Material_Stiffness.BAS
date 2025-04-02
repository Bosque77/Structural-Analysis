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

    ' Prompt user to select elements
    Dim elemSet As femap.Set
    Set elemSet = femapApp.feSet

    If elemSet.Select(femap.zDataType.FT_ELEM, True, "Select elements to modify") <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Element selection failed or canceled."
        Exit Sub
    End If

    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Selected element set ID: " & elemSet.ID
    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Number of elements selected: " & elemSet.Count

    If elemSet.Count = 0 Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "No elements in selection."
        Exit Sub
    End If

    ' Sets to track unique IDs
    Dim propIDs As femap.Set
    Dim layupIDs As femap.Set
    Dim matIDs As femap.Set
    Set propIDs = femapApp.feSet
    Set layupIDs = femapApp.feSet
    Set matIDs = femapApp.feSet

    ' FEMAP objects
    Dim elem As femap.Elem
    Set elem = femapApp.feElem

    Dim prop As femap.Prop
    Set prop = femapApp.feProp

    ' Loop through selected elements
    Dim elemID As Long
    Dim origPropID As Long, origLayupID As Long, origMatID As Long
    Dim rc As Long

    elemID = elemSet.First
    Do While elemID > 0
        If elem.Get(elemID) = femap.zReturnCode.FE_OK Then
            origPropID = elem.propID
            origLayupID = 0
            origMatID = 0

            If origPropID > 0 And prop.Get(origPropID) = femap.zReturnCode.FE_OK Then
                origLayupID = prop.layupID
                origMatID = prop.matlID
            Else
                origMatID = elem.matlID ' fallback
            End If

            femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, _
                "Element " & elemID & ": propID=" & origPropID & ", layupID=" & origLayupID & ", matlID=" & origMatID

            If origPropID > 0 Then propIDs.Add origPropID
            If origLayupID > 0 Then layupIDs.Add origLayupID
            If origMatID > 0 Then matIDs.Add origMatID
        Else
            femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Error reading element " & elemID
        End If
        elemID = elemSet.Next
    Loop

    ' Debug: print all unique IDs found
    Dim id As Long

    id = propIDs.First
    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Unique Property IDs found:"
    Do While id > 0
        femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Property ID: " & id
        id = propIDs.Next
    Loop

    id = layupIDs.First
    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Unique Layup IDs found:"
    Do While id > 0
        femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Layup ID: " & id
        id = layupIDs.Next
    Loop

    id = matIDs.First
    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Unique Material IDs found:"
    Do While id > 0
        femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Material ID: " & id
        id = matIDs.Next
    Loop

    ' Copy Materials FIRST
    id = matIDs.First
    Do While id > 0
        If CopyMaterial(femapApp, id, id + 10000) <> 0 Then
            femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Error copying material ID " & id
        End If
        id = matIDs.Next
    Loop

    ' Copy Layups SECOND (so they can reference the new materials)
    id = layupIDs.First
    Do While id > 0
        If CopyLayup(femapApp, id, id + 10000) <> 0 Then
            femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Error copying layup ID " & id
        End If
        id = layupIDs.Next
    Loop

    ' Copy Properties LAST (so they can reference the new materials and layups)
    id = propIDs.First
    Do While id > 0
        If CopyProperty(femapApp, id, id + 10000) <> 0 Then
            femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Error copying property ID " & id
        End If
        id = propIDs.Next
    Loop

    ' Update element propIDs only
    elemID = elemSet.First
    Do While elemID > 0
        If elem.Get(elemID) = femap.zReturnCode.FE_OK Then
            elem.propID = elem.propID + 10000

            rc = elem.Put(elemID)
            If rc <> femap.zReturnCode.FE_OK Then
                femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Error updating element " & elemID
            Else
                femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Element " & elemID & " updated successfully."
            End If
        End If
        elemID = elemSet.Next
    Loop

    Exit Sub

ConnectError:
    MsgBox "Error connecting to FEMAP: " & Err.Description
    Exit Sub
End Sub

Function CopyProperty(femapApp As femap.model, origID As Long, newID As Long) As Integer
    Dim prop As femap.Prop
    Set prop = femapApp.feProp
    If prop.Get(origID) = femap.zReturnCode.FE_OK Then
        ' Store original IDs
        Dim origLayupID As Long
        Dim origMatlID As Long
        origLayupID = prop.layupID
        origMatlID = prop.matlID
        
        ' Set new property ID
        prop.ID = newID
        
        ' Update references to layup and material IDs if they exist
        If origLayupID > 0 Then
            prop.layupID = origLayupID + 10000
        End If
        
        If origMatlID > 0 Then
            prop.matlID = origMatlID + 10000
        End If
        
        ' Save the updated property
        CopyProperty = prop.Put(newID)
        
        femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Property " & origID & " copied to " & newID & _
            " with layupID=" & prop.layupID & ", matlID=" & prop.matlID
    Else
        CopyProperty = -1
    End If
End Function

Function CopyLayup(femapApp As femap.model, origID As Long, newID As Long) As Integer
    Dim layup As femap.Layup
    
    ' Create layup object
    Set layup = femapApp.feLayup
    
    ' Get the original layup
    If layup.Get(origID) <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to get original layup ID " & origID
        CopyLayup = -1
        Exit Function
    End If
    
    ' Store the original ID and change to new ID
    layup.ID = newID
    
    ' Put the copied layup
    If layup.Put(newID) <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to create new layup ID " & newID
        CopyLayup = -1
        Exit Function
    End If
    
    ' Now get it again to update it
    If layup.Get(newID) <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to get new layup ID " & newID
        CopyLayup = -1
        Exit Function
    End If
    
    ' Try to update material IDs in plies using brute force approach
    Dim plyIndex As Long
    Dim matlID As Long
    Dim updatedCount As Long
    
    plyIndex = 1
    updatedCount = 0
    
    ' Try up to 100 plies
    For plyIndex = 1 To 100
        On Error Resume Next
        matlID = layup.GetPlyMatl(plyIndex)
        
        If Err.Number = 0 And matlID > 0 Then
            ' Valid material ID found, update it
            layup.SetPlyMatl plyIndex, matlID + 10000
            
            If Err.Number = 0 Then
                updatedCount = updatedCount + 1
                femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Layup " & newID & " Ply " & plyIndex & " updated to material ID: " & (matlID + 10000)
            Else
                femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to update material for ply " & plyIndex & ": " & Err.Description
            End If
            Err.Clear
        ElseIf Err.Number <> 0 Then
            ' No material ID or error occurred
            Err.Clear
        End If
        On Error GoTo 0
    Next plyIndex
    
    ' Save the updated layup
    If layup.Put(newID) <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Failed to save updated layup ID " & newID
        CopyLayup = -1
    Else
        CopyLayup = 0
        femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Layup " & origID & " copied to " & newID & " with " & updatedCount & " plies updated"
    End If
End Function

Function CopyMaterial(femapApp As femap.model, origID As Long, newID As Long) As Integer
    Dim mat As femap.Matl
    Set mat = femapApp.feMatl
    If mat.Get(origID) = femap.zReturnCode.FE_OK Then
        mat.ID = newID
        CopyMaterial = mat.Put(newID)
    Else
        CopyMaterial = -1
    End If
End Function
