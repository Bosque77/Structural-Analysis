Imports femap

Module Isolated_Joint_Elements

    Sub Main()

        ' Step 1 Connect to Femap
        Dim femapApp As femap.model



        Try
            ' Try to connect to an existing instance of FEMAP
            femapApp = GetObject(, "femap.model")
        Catch ex As Exception
            ' Handle the case where FEMAP is not running or cannot be connected
            Console.WriteLine(ex.Message)
            Console.WriteLine("Error: Could not connect to FEMAP. Make sure FEMAP is running.")
            ' Exit the program if FEMAP is not connected
            Return
        End Try

        ' Proceed if connected successfully
        If Not femapApp Is Nothing Then
            ' Write a message in the Femap message box
            femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Connected to Femap version: " & femapApp.feAppVersion)
            Console.WriteLine("Connected to Femap version: " & femapApp.feAppVersion)

            ' Your code continues here...

        Else
            Console.WriteLine("FEMAP connection failed.")
        End If




        ' Step 3: Find spring elements
        Dim springElements As femap.Set = femapApp.feSet

        springElements.AddRule(femap.zElementType.FET_L_SPRING, femap.zGroupDefinitionType.FGD_ELEM_BYTYPE)

        ' Step 4: Loop through each element in springElements to find associated nodes
        Dim nodeSet As femap.Set = femapApp.feSet

        Dim elemID As Integer = springElements.First
        While elemID > 0
            Dim elem As femap.Elem = femapApp.feElem
            If elem.Get(elemID) = femap.zReturnCode.FE_OK Then
                For Each nodeID In elem.Nodes
                    nodeSet.Add(nodeID)
                Next
            End If
            elemID = springElements.Next
        End While

        ' Optionally, show how many nodes were added
        Console.WriteLine("Number of nodes added to the node set: " & nodeSet.Count)

        ' Step 5: Create a new set for connected elements
        ' Step 4: Make a copy of the springElements set
        Dim copyOfSpringElements As femap.Set = femapApp.feSet
        copyOfSpringElements.AddSet(springElements.ID)
        copyOfSpringElements.AddConnectedElements()


        ' Step 6: Remove original spring elements from the copied set to leave only associated and connected elements
        copyOfSpringElements.RemoveSet(springElements.ID)
        Dim plateElements As femap.Set = femapApp.feSet
        plateElements.AddSet(copyOfSpringElements.ID)



        Console.WriteLine("Number of connected elements: " & plateElements.Count)

        ' Step 7: Create a group for the nodes and plate elements
        Dim combinedGroup As femap.group = femapApp.feGroup
        combinedGroup.title = "Isolated_Joint_Elements"
        combinedGroup.SetAdd(zDataType.FT_NODE, nodeSet.ID)
        combinedGroup.SetAdd(zDataType.FT_ELEM, plateElements.ID)
        combinedGroup.Put(femapApp.feGroup.NextEmptyID) ' Save the group with a unique ID



        ' Optional: Refresh the Femap UI
        femapApp.feViewRegenerate(0) ' Regenerate all views



    End Sub

End Module
