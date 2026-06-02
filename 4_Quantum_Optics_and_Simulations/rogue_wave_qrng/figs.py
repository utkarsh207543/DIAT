

clear; clc; close all;

% -------------------------------
% PARAMETERS
% -------------------------------
ROGUE_FACTOR = 2.2;
MIN_CURVE_LENGTH = 10;
HIST_BINS = 60;

% -------------------------------
% FIND FILES
% -------------------------------
files = dir('*_data.mat');

fprintf('Found %d data files\n\n', length(files));

for f = 1:length(files)

    filename = files(f).name;
    fprintf('Processing %s\n', filename);

    data = load(filename);
    if ~isfield(data, 'Y')
        fprintf('  Skipping (no Y)\n');
        continue;
    end

    Y = data.Y;
    valid_curves = {};

    % -------------------------------
    % DATA CLEANING
    % -------------------------------
    for k = 1:numel(Y)
        y = squeeze(Y{k});
        if ~isvector(y), continue; end
        if length(y) < MIN_CURVE_LENGTH, continue; end
        if all(isnan(y)), continue; end
        valid_curves{end+1} = y;
    end

    if isempty(valid_curves)
        fprintf('  No valid curves\n');
        continue;
    end

    % -------------------------------
    % MERGE INTENSITY
    % -------------------------------
    intensity = [];
    for k = 1:length(valid_curves)
        y = valid_curves{k};
        y = y(isfinite(y) & y > 0);
        intensity = [intensity; y(:)];
    end

    if length(intensity) < 100
        fprintf('  Insufficient statistics\n');
        continue;
    end

    % -------------------------------
    % SWH CALCULATION
    % -------------------------------
    sorted_I = sort(intensity, 'descend');
    top_third = sorted_I(1:floor(length(sorted_I)/3));
    SWH = mean(top_third);
    threshold = ROGUE_FACTOR * SWH;

    % -------------------------------
    % ROGUE EVENTS
    % -------------------------------
    rogue_idx = find(intensity > threshold);
    rogue_events = intensity(rogue_idx);

    fprintf('  SWH = %.3f | Threshold = %.3f | RW events = %d\n', ...
            SWH, threshold, length(rogue_events));

    % =========================================================
    % FIGURE 1: INTENSITY HISTOGRAM (HEAVY TAIL)
    % =========================================================
    figure('Color','w');
    histogram(intensity, HIST_BINS, 'Normalization','pdf');
    set(gca,'YScale','log');
    hold on;
    xline(SWH,'r--','LineWidth',2);
    xline(threshold,'b--','LineWidth',2);
    xlabel('Intensity (a.u.)');
    ylabel('PDF (log scale)');
    title(['Intensity Distribution – ' strrep(filename,'_','\_')]);
    legend('PDF','SWH','2.2×SWH');
    grid on;
    saveas(gcf, strrep(filename,'_data.mat','_hist.png'));

    % =========================================================
    % FIGURE 2: TIME SERIES WITH ROGUE EVENTS
    % =========================================================
    figure('Color','w');
    plot(intensity,'k'); hold on;
    plot(rogue_idx, rogue_events,'ro','MarkerFaceColor','r');
    yline(threshold,'b--','LineWidth',2);
    xlabel('Event Index');
    ylabel('Intensity (a.u.)');
    title('Temporal Localization of Rogue Waves');
    legend('Intensity','Rogue Events','Threshold');
    grid on;
    saveas(gcf, strrep(filename,'_data.mat','_timeseries.png'));

    % =========================================================
    % FIGURE 3: SURVIVAL FUNCTION (P(I > x))
    % =========================================================
    [cdf_vals, x_vals] = ecdf(intensity);
    survival = 1 - cdf_vals;

    figure('Color','w');
    semilogy(x_vals, survival,'k','LineWidth',2); hold on;
    xline(threshold,'r--','LineWidth',2);
    xlabel('Intensity (a.u.)');
    ylabel('P(I > x)');
    title('Survival Function (Extreme Statistics)');
    grid on;
    saveas(gcf, strrep(filename,'_data.mat','_survival.png'));

end

fprintf('\n✓ Rogue-wave analysis complete\n');
