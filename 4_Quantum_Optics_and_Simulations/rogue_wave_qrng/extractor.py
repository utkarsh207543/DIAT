figFiles = dir("*.fig");

for k = 1:length(figFiles)
    fig = openfig(figFiles(k).name, 'invisible');
    ax = findall(fig, 'Type', 'axes');
    lines = findall(ax, 'Type', 'line');

    X = get(lines, 'XData');
    Y = get(lines, 'YData');

    [~, name, ~] = fileparts(figFiles(k).name);
    save([name '_data.mat'], 'X', 'Y');

    close(fig)
end
