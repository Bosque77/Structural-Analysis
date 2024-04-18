Imports femap

Module Module1

    Sub Main()



        ' Step 1: Connect to Femap
        Dim femapApp As femap.model

        Try
            femapApp = GetObject(, "femap.model")
        Catch ex As Exception
            Console.WriteLine("Error: Could not connect to FEMAP. Make sure FEMAP is running.")
            Return
        End Try

        If femapApp Is Nothing Then
            Console.WriteLine("FEMAP connection failed.")
            Return
        End If

        ' Step 2: Display a prompt for the user to select elements
        Dim selectedElements As femap.Set = femapApp.feSet
        Dim selectedElement As Int32
        If selectedElements.SelectID(femap.zDataType.FT_ELEM, "Select elements:", selectedElement) <> femap.zReturnCode.FE_OK Then
            Console.WriteLine("No elements selected or selection cancelled.")
            Return
        End If

        Console.WriteLine("Selected element ID: " & selectedElement)

        ' Step 3: Find all connected elements, excluding spring elements
        Dim connectedElements As femap.Set = femapApp.feSet
        connectedElements.Add(selectedElement)
        Dim springsToRemove As femap.Set = femapApp.feSet
        Dim previousCount As Integer = 0

        ' Initialize springsToRemove Set
        springsToRemove.AddRule(femap.zElementType.FET_L_SPRING, femap.zGroupDefinitionType.FGD_ELEM_BYTYPE)

        ' List the number of spring elements to Console
        Console.WriteLine("Number of spring elements: " & springsToRemove.Count)


        ' Repeat process until no new elements are added to the set
        Do
            previousCount = connectedElements.Count
            connectedElements.AddConnectedElements()
            connectedElements.RemoveSet(springsToRemove.ID) ' Remove spring elements
        Loop While connectedElements.Count > previousCount

        ' Step 4: Create a unique group for these elements
        Dim resultGroup As femap.group = femapApp.feGroup
        resultGroup.title = "Isolated Connected Elements"
        resultGroup.SetAdd(femap.zDataType.FT_ELEM, connectedElements.ID)
        resultGroup.Put(femapApp.feGroup.NextEmptyID)
        femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "A new group of connected elements has been created.")

        ' Optional: Refresh the Femap UI
        femapApp.feViewRegenerate(0)

        Console.WriteLine("Process completed successfully.")
    End Sub

End Module
