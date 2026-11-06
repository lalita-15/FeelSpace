
document.addEventListener("DOMContentLoaded", () => {

    // =====================================
    // ELEMENTS
    // =====================================

    const moodOptions = document.querySelectorAll(".mood-option");
    const moodHint = document.getElementById("mood-hint");

    const thoughtInput = document.getElementById("thought-content");
    const anonymousCheckbox = document.getElementById("anonymous");

    const shareButton = document.getElementById("share-btn");
    const refreshButton = document.getElementById("refresh-btn");

    const message = document.getElementById("form-message");
    const thoughtsContainer = document.getElementById("thoughts-container");


    // =====================================
    // MOOD STATE
    // =====================================

    let selectedMood = "";
    let selectedEmoji = "";

    const moodEmojiMap = {
        Happy: "😊",
        Sad: "😢",
        Excited: "🤩",
        Anxious: "😰",
        Loved: "🥰",
        Calm: "😌",
        Motivated: "🔥",
        Tired: "😴",
        Grateful: "🥹",
        Confused: "😕",
        Confident: "😎",
        Lonely: "🫂"
    };


    // =====================================
    // MESSAGE HELPER
    // =====================================

    function showMessage(text, type = "") {

        message.textContent = text;

        message.classList.remove("success", "error");

        if (type) {
            message.classList.add(type);
        }
    }


    // =====================================
    // MOOD SELECTION
    // =====================================

    moodOptions.forEach((option) => {

        option.addEventListener("click", () => {

            // Remove previous selected state
            moodOptions.forEach((item) => {

                item.classList.remove("selected");

                item.setAttribute("aria-pressed", "false");

            });

            // Select clicked mood
            option.classList.add("selected");

            option.setAttribute("aria-pressed", "true");

            // Store selected mood and emoji
            selectedMood = option.dataset.mood;

            selectedEmoji = option.dataset.emoji;

            // Fallback if emoji attribute is missing
            if (!selectedEmoji) {
                selectedEmoji = moodEmojiMap[selectedMood] || "💜";
            }

            // Update mood confirmation
            moodHint.textContent =
                `${selectedEmoji} You're feeling ${selectedMood} today.`;

            moodHint.classList.add("active");

            // Clear previous error message
            showMessage("");

        });

    });


    // =====================================
    // CREATE THOUGHT CARD
    // =====================================

    function createThoughtCard(thought) {

        const card = document.createElement("article");

        card.className = "thought-item";


        // Thought metadata
        const meta = document.createElement("div");

        meta.className = "thought-meta";


        // Author name
        const author = document.createElement("span");

        author.textContent = thought.anonymous
            ? "Anonymous"
            : "Community Member";


        // Mood badge with emoji
        const moodBadge = document.createElement("span");

        moodBadge.className = "mood-badge";

        const emoji = moodEmojiMap[thought.mood] || "💜";

        moodBadge.textContent =
            `${emoji} ${thought.mood || "Feeling"}`;


        // Thought content
        const content = document.createElement("p");

        content.textContent = thought.content;


        // Date and time
        const date = document.createElement("small");

        if (thought.created_at) {

            const createdDate = new Date(thought.created_at);

            date.textContent = createdDate.toLocaleString();

        } else {

            date.textContent = "Recently shared";

        }


        // Assemble card
        meta.append(author, moodBadge);

        card.append(meta, content, date);

        return card;

    }


    // =====================================
    // LOAD COMMUNITY THOUGHTS
    // =====================================

    async function loadThoughts() {

        thoughtsContainer.textContent = "Loading community thoughts...";

        refreshButton.disabled = true;

        try {

            const response = await fetch("/api/thoughts");

            if (!response.ok) {

                throw new Error("Unable to load thoughts");

            }

            const thoughts = await response.json();

            thoughtsContainer.replaceChildren();


            // Empty community state
            if (!Array.isArray(thoughts) || thoughts.length === 0) {

                const emptyState = document.createElement("div");

                emptyState.className = "empty-state";


                const emoji = document.createElement("span");

                emoji.className = "empty-emoji";

                emoji.textContent = "💜";


                const heading = document.createElement("h3");

                heading.textContent = "Your community is waiting.";


                const description = document.createElement("p");

                description.textContent =
                    "Be the first to share a little piece of your heart.";


                emptyState.append(emoji, heading, description);

                thoughtsContainer.appendChild(emptyState);

                return;

            }


            // Display all thoughts
            thoughts.forEach((thought) => {

                const card = createThoughtCard(thought);

                thoughtsContainer.appendChild(card);

            });

        } catch (error) {

            console.error("Community feed error:", error);

            thoughtsContainer.textContent =
                "Unable to load thoughts. Please try again.";

        } finally {

            refreshButton.disabled = false;

        }

    }


    // =====================================
    // SHARE A NEW THOUGHT
    // =====================================

    shareButton.addEventListener("click", async () => {

        const content = thoughtInput.value.trim();


        // Validate thought
        if (!content) {

            showMessage(
                "Please write something before sharing.",
                "error"
            );

            thoughtInput.focus();

            return;

        }


        // Validate mood
        if (!selectedMood) {

            showMessage(
                "Please select your mood emoji first.",
                "error"
            );

            document.getElementById("mood").scrollIntoView({
                behavior: "smooth",
                block: "center"
            });

            return;

        }


        // Disable button while submitting
        shareButton.disabled = true;

        shareButton.textContent = "Sharing your thought...";


        try {

            const response = await fetch("/api/thoughts", {

                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({

                    content: content,

                    mood: selectedMood,

                    anonymous: anonymousCheckbox.checked

                })

            });


            const result = await response.json();


            if (!response.ok) {

                throw new Error(
                    result.error || "Unable to share thought"
                );

            }


            // Success message
            showMessage(
                `${selectedEmoji} Your thought has been shared successfully!`,
                "success"
            );


            // Reset form
            thoughtInput.value = "";

            anonymousCheckbox.checked = false;


            // Reset mood selection
            moodOptions.forEach((option) => {

                option.classList.remove("selected");

                option.setAttribute("aria-pressed", "false");

            });


            selectedMood = "";

            selectedEmoji = "";


            moodHint.textContent = "Select a mood to continue 💜";

            moodHint.classList.remove("active");


            // Reload community feed
            await loadThoughts();


            // Scroll to community section
            document.getElementById("community").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });


        } catch (error) {

            console.error("Share thought error:", error);

            showMessage(
                error.message || "Unable to save thought. Please try again.",
                "error"
            );

        } finally {

            shareButton.disabled = false;

            shareButton.textContent = "Post your thought →";

        }

    });


    // =====================================
    // REFRESH COMMUNITY FEED
    // =====================================

    refreshButton.addEventListener("click", () => {

        loadThoughts();

    });


    // =====================================
    // INITIAL PAGE LOAD
    // =====================================

    loadThoughts();

});
