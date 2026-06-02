figure('Color','w','Position',[100 100 400 350]);

bar(peak_power / SWH, 'FaceColor',[0.2 0.6 0.8]); hold on;
yline(2,'r--','LineWidth',2);

ylabel('Times Factor','FontSize',12);
xticks([]);
ylim([0 max(4, peak_power/SWH + 0.5)]);
title('Rogue Wave Criterion','FontSize',13);
grid on;
box on;
