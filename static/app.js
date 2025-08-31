// Clear button functionality
document.getElementById("clear-btn").addEventListener("click", () => {
    document.getElementById("notes").value = "";
    document.getElementById("result").innerHTML = "";
});
document.getElementById("generate-btn").addEventListener("click", async () => {
    const notes = document.getElementById("notes").value.trim();
    const generateBtn = document.getElementById("generate-btn");
    const container = document.getElementById("result");

    // Validate input
    if (!notes) {
        alert("Please enter some study notes first!");
        return;
    }

    // Show loading state
    generateBtn.textContent = "Generating...";
    generateBtn.disabled = true;
    container.innerHTML = '<div style="text-align: center; color: #666;">Generating flashcards...</div>';

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `notes=${encodeURIComponent(notes)}`
        });

        const data = await response.json();

        if (data.status === "ok") {
            container.innerHTML = ""; // clear loading message
            if (data.questions && data.questions.length > 0) {
                data.questions.forEach((flashcard, index) => {
                    const card = document.createElement("div");
                    card.classList.add("flashcard");
                    card.innerHTML = `
                        <div class="question">Q${index + 1}: ${flashcard.question}</div>
                        <div class="answer">${flashcard.answer}</div>
                    `;
                    container.appendChild(card);
                });
                // Show success message
                const successMsg = document.createElement("div");
                successMsg.style.cssText = "text-align: center; color: #28a745; margin-top: 20px; font-weight: bold;";
                successMsg.textContent = `Successfully generated ${data.questions.length} flashcards!`;
                container.appendChild(successMsg);
            } else {
                container.innerHTML = '<div style="text-align: center; color: #666;">No flashcards were generated. Please try with different content.</div>';
            }
        } else if (data.status === "limit") {
            // Create popup box
            const popup = document.createElement("div");
            popup.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 4px 24px rgba(0,0,0,0.18);
                padding: 32px 24px 24px 24px;
                z-index: 9999;
                min-width: 320px;
                max-width: 90vw;
                text-align: center;
                color: #2a2a2a;
            `;
            // Close button
            const closeBtn = document.createElement("span");
            closeBtn.textContent = "×";
            closeBtn.style.cssText = `
                position: absolute;
                right: 18px;
                top: 12px;
                font-size: 2rem;
                font-weight: bold;
                color: #e53e3e;
                background: #fff;
                border-radius: 50%;
                box-shadow: 0 2px 8px rgba(0,0,0,0.10);
                width: 36px;
                height: 36px;
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
                border: 2px solid #e53e3e;
                z-index: 10;
            `;
            closeBtn.onclick = function() {
                popup.remove();
            };
            popup.appendChild(closeBtn);
            // Message
            const msg = document.createElement("div");
            msg.style.cssText = "margin-top: 18px; font-size: 1.15rem; font-weight: bold; color: #e53e3e;";
            msg.innerHTML = `You have reached the daily limit of generating flashcards.<br>Please come back tomorrow or <a href='/payment' style='color:#2563eb; text-decoration:underline; font-weight:bold;'>upgrade your plan</a>.`;
            popup.appendChild(msg);
            document.body.appendChild(popup);
            container.innerHTML = "";
        } else {
            container.innerHTML = `<div style="text-align: center; color: #dc3545;">Error: ${data.message || "Something went wrong"}</div>`;
        }
    } catch (error) {
        console.error("Error:", error);
        container.innerHTML = '<div style="text-align: center; color: #dc3545;">Failed to connect to server. Please check your internet connection.</div>';
    } finally {
        // Reset button state
        generateBtn.textContent = "Generate Flashcards";
        generateBtn.disabled = false;
    }
});
