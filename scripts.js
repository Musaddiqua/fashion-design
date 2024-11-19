document.addEventListener('DOMContentLoaded', function () {
    // Generate Image
    document.getElementById("generate-btn").addEventListener("click", async () => {
        const prompt = document.getElementById("prompt").value;
        if (prompt.trim() === "") {
            alert("Please enter a description.");
            return;
        }

        try {
            const response = await fetch("/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ text: prompt })
            });

            const data = await response.json();

            if (data.image_url) {
                const imageContainer = document.getElementById("image-container");
                imageContainer.innerHTML = `<img src="${data.image_url}" alt="Generated Design" />`;
                imageContainer.style.display = "block"; // Show image container

                // Show classify button after image is generated
                document.getElementById("classify-btn").style.display = "inline-block";
            } else {
                alert(data.error || "Failed to generate the image.");
            }
        } catch (err) {
            console.error("Error generating image:", err);
            alert("An error occurred while generating the image.");
        }
    });

    // Classify Image
    document.getElementById("classify-btn").addEventListener("click", async () => {
        const imageElement = document.getElementById("image-container").querySelector("img");
        if (!imageElement) {
            alert("No image available for classification.");
            return;
        }

        const imagePath = imageElement.src;

        try {
            const response = await fetch("/classify", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ image_path: imagePath })
            });

            const data = await response.json();

            const resultsContainer = document.getElementById("results-container");

            if (data.type_of_clothing) {
                resultsContainer.innerHTML = `
                    <p>Type of Clothing: ${data.type_of_clothing}</p>
                    <p>Color: ${data.color}</p>
                    <p>Fabric: ${data.fabric}</p>
                `;
            } else {
                resultsContainer.innerHTML = `<p>${data.error || "Failed to classify image. Please try again."}</p>`;
            }
        } catch (err) {
            console.error("Error classifying image:", err);
            alert("An error occurred while classifying the image.");
        }
    });
});
