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

    ' Prompt user to select elements directly
    Dim elemSet As femap.Set
    Set elemSet = femapApp.feSet

    If elemSet.Select(femap.zDataType.FT_ELEM, True, "Select elements to modify") <> femap.zReturnCode.FE_OK Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Element selection failed or canceled."
        Exit Sub
    End If

    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Element Set ID: " & elemSet.ID
    femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, "Number of elements selected: " & elemSet.Count

    If elemSet.Count = 0 Then
        femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "No elements in selection."
        Exit Sub
    End If

    ' Create sets to store unique Prop, Layup, and Material IDs
    Dim propIDs As femap.Set
    Dim layupIDs As femap.Set
    Dim matIDs As femap.Set
    Set propIDs = femapApp.feSet
    Set layupIDs = femapApp.feSet
    Set matIDs = femapApp.feSet

    Dim elemID As Long
    Dim origPropID As Long
	Dim origLayupID As Long
	Dim origMatID As Long
    Dim rc As Long

    Dim elem As femap.Elem
    Set elem = femapApp.feElem

    ' Loop over elements in set and gather original IDs
    elemID = elemSet.First
    Do While elemID > 0
        If elem.Get(elemID) = femap.zReturnCode.FE_OK Then
            origPropID = elem.propID
            origLayupID = elem.layupID
            origMatID = elem.matlID

            femapApp.feAppMessage femap.zMessageColor.FCM_NORMAL, _
                "Element " & elemID & ": propID=" & origPropID & ", layupID=" & origLayupID & ", matlID=" & origMatID & ", type=" & elem.type

            If origPropID > 0 Then propIDs.Add origPropID
            If origLayupID > 0 Then layupIDs.Add origLayupID
            If origMatID > 0 Then matIDs.Add origMatID
        Else
            femapApp.feAppMessage femap.zMessageColor.FCM_ERROR, "Error retrieving data for element " & elemID
        End If
        elemID = elemSet.Next
    Loop

    ' Debug: List unique IDs found
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



    Exit Sub

ConnectError:
    MsgBox "Error connecting to FEMAP: " & Err.Description
    Exit Sub
End Sub
