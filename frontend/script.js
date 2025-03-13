document.addEventListener("DOMContentLoaded", function () {
    var container = document.getElementById("heatmapContainer");
    var textCanvas = document.getElementById("textCanvas");
    var ctx = textCanvas.getContext("2d");

    function resizeCanvas() {
        textCanvas.width = window.innerWidth;
        textCanvas.height = window.innerHeight;
    }
    resizeCanvas(); // Resize canvas initially
    window.addEventListener("resize", resizeCanvas); // Resize dynamically on window change

       // Heatmap 1 (Red/Yellow)
       var heatmap1 = h337.create({
        container: container,
        radius: 200,
        maxOpacity: 1,
        minOpacity: 0,
        blur: 0.9,
        gradient: {
            0: "#FEF001",
            0.2: "#FD6104",
            1.0: "#F00505"
        }
    });

    // Heatmap 2 (Blue/Green)
    var heatmap2 = h337.create({
        container: container,
        radius: 200,
        maxOpacity: 1,
        minOpacity: 0,
        blur: 0.9,
        gradient: {
            0: "#FEF001",
            0.2: "#87FA00",
            1.0: "#00ED01"
        }
    });


    document.getElementById("loadHeatmapButton").addEventListener("click", function () {
        fetch("/get_heatmap_data")
            .then(response => response.json())
            .then(data => {
                let data1 = {
                    max: data.max,
                    data: data.data.filter((_, i) => i % 2 === 0)
                };

                let data2 = {
                    max: data.max,
                    data: data.data.filter((_, i) => i % 2 !== 0)
                };

                heatmap1.setData(data1);
                heatmap2.setData(data2);

                // Draw names on top of heatmap
                drawNames(data.data);
            })
            .catch(error => console.error("Error loading heatmap data:", error));
    });

    function drawNames(points) {
        ctx.clearRect(0, 0, textCanvas.width, textCanvas.height); // Clear canvas before drawing
        ctx.font = "bold 22px 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif";
        ctx.fillStyle = "white";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.shadowColor = "black";
        ctx.shadowBlur = 2;
        ctx.shadowOffsetX = 1;
        ctx.shadowOffsetY = 1;

        points.forEach(point => {
            if (!point.name) return;
            ctx.fillText(point.name, point.x, point.y);
        });
    }
});