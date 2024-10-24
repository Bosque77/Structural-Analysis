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
        If selectedElements.Select(femap.zDataType.FT_ELEM, True, "Select elements:") <> femap.zReturnCode.FE_OK Then
            Console.WriteLine("No elements selected or selection cancelled.")
            Return
        End If

        Console.WriteLine("Selected element ID: " & selectedElements.Count)

        ' Step 3: Find all connected elements, excluding spring elements

        Dim springsToRemove As femap.Set = femapApp.feSet
        springsToRemove.AddRule(femap.zElementType.FET_L_SPRING, femap.zGroupDefinitionType.FGD_ELEM_BYTYPE)
        Dim previousCount As Integer = 0
        Dim connectedElements As femap.Set = femapApp.feSet

        Dim elementID As Integer
        elementID = selectedElements.First()

        While elementID > 0
            connectedElements.Add(elementID)
            ' Repeat process until no new elements are added to the set
            Do
                previousCount = connectedElements.Count
                connectedElements.AddConnectedElements()
                connectedElements.RemoveSet(springsToRemove.ID) ' Remove spring elements
            Loop While connectedElements.Count > previousCount

            ' Get the next element ID
            elementID = selectedElements.Next()

        End While

        ' Step 4: Create a unique group for these elements
        Dim group_number As Int16 = femapApp.feGroup.NextEmptyID
        Dim resultGroup As femap.group = femapApp.feGroup
        resultGroup.title = "Isolated Connected Elements " + group_number.ToString()
        resultGroup.SetAdd(femap.zDataType.FT_ELEM, connectedElements.ID)
        resultGroup.Put(femapApp.feGroup.NextEmptyID)
        femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "A new group of connected elements has been created.")

        ' Optional: Refresh the Femap UI
        femapApp.feViewRegenerate(0)

        Console.WriteLine("Process completed successfully.")
    End Sub

End Module
