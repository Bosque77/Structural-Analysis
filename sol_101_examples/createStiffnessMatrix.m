function [K] = createStiffnessMatrix(file_DMIG)
%% Temporarily defining global variables

BIN_1 = 1;
BIN_2 = 9;
BIN_3 = 17;
BIN_4 = 25;
BIN_5 = 33;
BIN_6 = 41;
BIN_7 = 49;
BIN_8 = 57;
BIN_9 = 65;

node_dof_list = {};


%% Main Code Portion 

fileID = fopen(file_DMIG,'r');

%   Forming the stiffness matrix.
%   This code goes the the KAAX section in the DMIG and formulates the stiffness matrix

line_1 = fgetl(fileID);
matrix_size = str2double(line_1(BIN_9:end));
K = zeros(matrix_size,matrix_size); 
current_line = fgetl(fileID);
line_type_indicator = current_line(BIN_2:BIN_3-1);
row_K = 0;
while ~strcmp(line_type_indicator,'MAAX    ')
    if strcmp(line_type_indicator,'KAAX    ')
        node = str2double(current_line(BIN_5:BIN_6-1));
        dof = str2double(current_line(BIN_7:BIN_8-1));
        node_dof = [node,dof];
        node_dof_list{end+1} = node_dof;
        row_K = row_K+1;
    else
        node = str2double(current_line(BIN_3: BIN_4-1));
        dof = str2double(current_line(BIN_5:BIN_6-1));
        current_stiffness = str2double(current_line(BIN_6:BIN_8-1));
        current_node_dof = [node, dof];
        col_K = indexStructure(node_dof_list,current_node_dof);
        K(row_K,col_K) = current_stiffness;
        try
            K(col_K,row_K) = current_stiffness;
        catch
            continue
        end
    end
    current_line = fgetl(fileID);
    line_type_indicator = current_line(BIN_2:BIN_3-1);
end
fclose(fileID);


function [indexed_column] = indexStructure(node_dof_list,current_node_dof)
    indexed_column = 1;
    [row,col]=size(node_dof_list);
    for i=1:col
        node_dof = node_dof_list{i};
        tf = isequal(current_node_dof,node_dof);
        if tf
            indexed_column =  i;
            break;
        end
    end

end
end