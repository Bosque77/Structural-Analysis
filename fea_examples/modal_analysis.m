clc
clear

%% Input Variables
K = createStiffnessMatrix('DMIG.pch');
M = createMassMatrix('DMIG.pch');
F = [0;386.089;0;0;0;0];

modal_loads = [
35645940	0	0	0;
0	35645940	0	0;
0	0	0	0;
0	0	0	0;
11881980	0	0	0;
0	11881981	0	0;
0	0	177712704	0;
0	0	0	138843296]


[r,c] = size(M);

% Solution 1
syms l
eig_problem = det(K-l.*M);
gamma = solve(eig_problem ==0.0, l);
num_of_eig_values = length(gamma)
u = zeros(r,num_of_eig_values);
for j=1:length(gamma)
    u(:,j) = null(K-gamma(j).*M);  %eigenvectors
end


Mg = u'*M*u;
Kg = u'*K*u;
Fg = u'*F;

% index=1;
% syms t
% for w=(2*pi):100*2*pi:10001*2*pi
%    A = (-w^2.*Mg+Kg);
%    b = Fg;
%    Z = A\b;
%    mode_shape_factors(:,index) = Z;
%    x_test(:,index) = u*Z;
%    x(:,index) = u*Z*exp(1i*w);
%    beam_loads(:,index) = modal_loads*Z;
% %    mag = abs(x)
% %    phase = angle(x)
%    index = index+1;
% end

index=1;
syms t

% Adjust these variables to set the modal frequency
alpha = 0.01;
beta = 0.01;

C = alpha*Mg + beta*Kg;

[r,c] = size(Mg);
C = eye(r)*0.04

spread = 0.05;
for w=1324*2*pi:spread:1325*2*pi
   A = (-w^2.*Mg+i*w*C+Kg);
   b = Fg;
   Z = A\b;
   mode_shape_factors(:,index) = Z;
   x(:,index) = abs(u*Z*exp(i*w));
   x1(:,index) = u*Z;
   beam_loads(:,index) = abs(modal_loads*Z);
   mag = abs(x)
   phase = angle(x);
   index = index+1;
end


T2 = x(2,:);
indep_var = 1320*2*pi:spread:1350*2*pi
plot(indep_var,T2)

indep_var = indep_var./(2*pi);
plot(indep_var,beam_loads(1,:))


% 
% 
% % % norm_eigenvectors = normc(eigenVector)
% wn_rad = vpa(sqrt(gamma),3); % Natural Frequency in Hz
% wn_hz = vpa(sqrt(gamma)./(2*pi),3); % Natural Frequency in Hz
% 
% % % In the MIT Lecture Video they normalize by the first row
% % for j=1:length(gamma)
% %     u(:,j) = u(:,j)/u(1,j);  %eigenvectors
% % end
%  

% 
% index=1;
% syms t
% for w=(2*pi):100*2*pi:10001*2*pi
%     A = (-w^2.*Mg+Kg);
%    b = Fg;
%    Z = A\b;
%    mode_shape_factors(:,index) = Z;
%    x_test(:,index) = u*Z;
%    x(:,index) = u*Z*exp(1i*w);
%    beam_loads(:,index) = modal_loads*Z;
% %    mag = abs(x)
% %    phase = angle(x)
%    index = index+1;
% end
% 
% 
% 
%     
%     
%    mag = abs(x);
%    phase = angle(x);
%    
   
    
   
%    input=(2*pi):100*2*pi:10001*2*pi
%    input = input/(2*pi);
%    figure
%    subplot(2,1,1)
%    plot(input,x_test(2,:))
%    subplot(2,1,2)
%    plot(input,mag(2,:))
% %    plot(input,beam_loads(1,:))
% 

