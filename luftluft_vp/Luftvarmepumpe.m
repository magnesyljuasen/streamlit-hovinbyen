%Luftvarmepumpe


clear all
close all
clc


pkg load io
data=xlsread('Effekt_hus.xlsx');
T=data(:,1);
E=data(:,2);


P_nominal=5             % nominell effekt på VP
COP_nominal=5           % nominell COP

%SN- NSPEK 3031:2023 - tabell K.13
T_data=[-15 2 7]
P_HP10000=[0.46 0.72 1;0.23 0.36 0.5;0.09 0.14 0.2];
COP1000=[0.44 0.53 0.64;0.61 0.82 0.9;0.55 0.68 0.82];

tic
for i=1:8760

if T(i)>=7
T_klima=7;
elseif T(i)<=-15
T_klima=-15;
else
T_klima=T(i);
end


P_HP=interp1(T_data,P_HP10000',T_klima).*P_nominal;
COP_HP=interp1(T_data,COP1000',T_klima).*COP_nominal;


if E(i) >= P_HP(1)
P=P_HP(1);
COP=COP_HP(1);
elseif E(i) <= P_HP(3)
P=E(i);
COP=COP_HP(3);
else
P=E(i);
COP=interp1(P_HP,COP_HP,P);
end

if T(i)<-15
COP=1;
P=0;
end

P_air(i)=P-P/COP;
P_VP(i)=P;
end
toc
figure, plot(E,'r')
hold on, plot(P_VP,'b')
hold on, plot(P_air,'g')
xlabel('timer')
ylabel('Termisk effekt (kW)')
    [legend_handle, hobj1] =legend('Husets varmebehov','Levert fra varmepumpe','Bidrag fra uteluft')
textobj = findobj(hobj1, 'type', 'text');
set(textobj, 'Interpreter', 'latex', 'fontsize', 16);
set(legend_handle,'Location','North','LineWidth',1, 'Orientation','vertical','edgecolor',[1 1 1])

sum(P_air)/sum(E)

Results=sortrows([E,P_air'],-1);
figure, plot(Results(:,1),'r')
hold on, plot(Results(:,2),'g')
xlabel('timer')
ylabel('Termisk effekt (kW)')
    [legend_handle, hobj1] =legend('Husets varmebehov','Bidrag fra uteluft')
textobj = findobj(hobj1, 'type', 'text');
set(textobj, 'Interpreter', 'latex', 'fontsize', 16);
set(legend_handle,'Location','North','LineWidth',1, 'Orientation','vertical','edgecolor',[1 1 1])

