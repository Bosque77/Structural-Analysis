Imports femap

Module Module1

    Sub Main()

        ' Step 1: Connect to Femap
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
            ' Write a message in the Femap message box indicating successful connection
            femapApp.feAppMessage(femap.zMessageColor.FCM_NORMAL, "Connected to Femap version: " & femapApp.feAppVersion)
            Console.WriteLine("Connected to Femap version: " & femapApp.feAppVersion)

            ' Step 2: Prompt user to select a group

            Dim selectedGroups As femap.Set = femapApp.feSet
            Dim selectedGroup As Int32
            If selectedGroups.SelectID(femap.zDataType.FT_GROUP, "Select group:", selectedGroup) <> femap.zReturnCode.FE_OK Then
                Console.WriteLine("No groups selected or selection cancelled.")
                Return
            End If




            ' User has successfully selected a group
            Console.WriteLine("Group " & selectedGroup & " selected.")

            ' Step 3: Create a set for spring elements within the selected group
            Dim springElements As femap.Set = femapApp.feSet
            Dim commonSpringElements As femap.Set = femapApp.feSet
            springElements.AddRule(femap.zElementType.FET_L_SPRING, femap.zGroupDefinitionType.FGD_ELEM_BYTYPE)

            Dim groupElements As femap.Set = femapApp.feSet
            groupElements.AddGroup(zDataType.FT_ELEM, selectedGroup)

            commonSpringElements.AddSet(springElements.ID)
            commonSpringElements.RemoveNotCommon(groupElements.ID)


            ' Step 4: Create a node set to find associated nodes
            Dim nodeSet As femap.Set = femapApp.feSet


            Dim elemID As Integer = commonSpringElements.First
            While elemID > 0
                Dim elem As femap.Elem = femapApp.feElem
                If elem.Get(elemID) = femap.zReturnCode.FE_OK Then
                    For Each nodeID In elem.Nodes
                        nodeSet.Add(nodeID)
                    Next
                End If
                elemID = commonSpringElements.Next
            End While

            ' Step 4: Make a copy of the springElements set
            Dim copyOfSpringElements As femap.Set = femapApp.feSet
            copyOfSpringElements.AddSet(commonSpringElements.ID)
            copyOfSpringElements.AddConnectedElements()


            ' Step 6: Remove original spring elements from the copied set to leave only associated and connected elements
            copyOfSpringElements.RemoveSet(springElements.ID)
            Dim plateElements As femap.Set = femapApp.feSet
            plateElements.AddSet(copyOfSpringElements.ID)



            Console.WriteLine("Number of connected elements: " & plateElements.Count)

            ' Step 7: Create a group for the nodes and plate elements
            Dim nextID As Integer = femapApp.feGroup.NextEmptyID
            Dim combinedGroup As femap.group = femapApp.feGroup
            combinedGroup.title = "Isolated_Joint_Elements_" + nextID.ToString()
            combinedGroup.SetAdd(zDataType.FT_NODE, nodeSet.ID)
            combinedGroup.SetAdd(zDataType.FT_ELEM, plateElements.ID)
            combinedGroup.Put(nextID) ' Save the group with a unique ID



            ' Optional: Refresh the Femap UI
            femapApp.feViewRegenerate(0) ' Regenerate all views

        End If




    End Sub

End Module
