document.getElementById("exportBtn").addEventListener("click", function() {
    var text = document.getElementById("transcriptionResult").textContent;
    var blob = new Blob([text], { type: "text/plain;charset=utf-8" });
    var url = URL.createObjectURL(blob);

    // Create a new anchor element
    var a = document.createElement("a");
    a.href = url;
    a.download = "Chronos_voice_export.txt"; // File name for download
    document.body.appendChild(a);
    a.click(); // Trigger a click on the element to download the file
    document.body.removeChild(a); // Clean up
    URL.revokeObjectURL(url); // Free up memory
});