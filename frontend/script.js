document.addEventListener("DOMContentLoaded", function () {
    // Create the heatmap instance but do not set data initially
    var heatmap = h337.create({
        container: document.getElementById("heatmapContainer"),
        radius: 150,
        maxOpacity: 0.6,
        minOpacity: 0,
        blur: 0.85,
    });

    document.getElementById("loadHeatmapButton").addEventListener("click", function () {
        fetch("/get_heatmap_data")
            .then(response => response.json())
            .then(data => {
                heatmap.setData(data); // Load heatmap data
            })
            .catch(error => console.error("Error loading heatmap data:", error));
    });
});