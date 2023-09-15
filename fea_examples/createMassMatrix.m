function [M] = createMassMatrix(file_DMIG)
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
line_1 = fgetl(fileID);
matrix_size = str2double(line_1(BIN_9:end));
M = zeros(matrix_size,matrix_size); 
current_line = fgetl(fileID);
line_type_indicator = current_line(BIN_2:BIN_3-1);
while ~strcmp(line_type_indicator,'MAAX    ')
    if strcmp(line_type_indicator,'KAAX    ')
        node = str2double(current_line(BIN_5:BIN_6-1));
        dof = str2double(current_line(BIN_7:BIN_8-1));
        node_dof = [node,dof];
        node_dof_list{end+1} = node_dof;
    end
    current_line = fgetl(fileID);
    line_type_indicator = current_line(BIN_2:BIN_3-1);
end

% Forming the Mass Matrix
node_row=0;
dof_row = 0;

while ~strcmp(line_type_indicator,'PAX     ') && ~strcmp(line_type_indicator,'TUG1    ')
    if strcmp(line_type_indicator,'MAAX    ')
        node_row = str2double(current_line(BIN_5:BIN_6-1));
        dof_row = str2double(current_line(BIN_7:BIN_8-1));
    else
        node_col = str2double(current_line(BIN_3:BIN_4-1));
        dof_col = str2double(current_line(BIN_5:BIN_6-1));
        current_mass = str2double(current_line(BIN_6:BIN_8-1));
        current_node_dof_row = [node_row, dof_row];
        current_node_dof_col = [node_col, dof_col];
        row_M = indexStructure(node_dof_list,current_node_dof_row);
        col_M = indexStructure(node_dof_list,current_node_dof_col);
        M(row_M,col_M) = current_mass;        
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