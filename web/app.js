// Get the elements from the HTML. QuerySelector fetches the first html element wwith the given CSS descriptpr (class) that it can find.
const chat = document.querySelector(".chat");
const form = document.querySelector(".input-area");
const input = document.querySelector(".input-area input")
const status_dot = document.querySelector(".status-dot")

let conversation_id = null;

form.addEventListener("submit", async function(event) {
    // Default behavior on submit is reload the page. Something we do not want
    event.preventDefault();

    // Gets the value from the input field and trims off beginning and ending spaces
    const message = input.value.trim();

    // Do not do anything if the message is empty
    if (message === "") {
        return;
    }

    // Add the message as user message 
    addMessage(message, "user-message")

    // Add the thinking animation
    const thinkingMessage = addThinkingMessage()

    try {

        requestBody = {
            prompt: message
        }

        if (conversation_id !== null) {
            requestBody.conversation_id = conversation_id;
        }

        // Reset the input field so the field is cleared
        input.value = "";
        input.focus();

        // Call api endpoint with user message to get the response
        const response = await fetch("/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(requestBody)
        });

        // Parse response to json
        const data = await response.json()

        // Fetch the conversation id. Should be the same as before when it was set already, or otherwise replace the empty one
        conversation_id = data.conversation_id;

        // remove the thinking animation
        thinkingMessage.remove();

        // Add the Ada Response message
        addMessage(data.response, "ada-message")
    } catch (error) {
        console.error("Chat request failed: ", error);
        
        thinkingElement.remove();

        addMessage("Entschuldigung, ich konnte gerade keine Antwort erzeugen.", "ada-message")
    }
})

// Use highlight-js library to highlight codeblocks semantically based on the language
const renderer = new marked.Renderer();

renderer.code = function({text, lang}) {
    let highlighted;

    if (lang && hljs.getLanguage(lang)){
            highlighted = hljs.highlight(text, {
                language: lang
            }).value;
        } else {
            highlighted = hljs.hightAuto(text).value;
        }
        return `
            <pre>
                <code class="hljs">${highlighted}</code>
            </pre>
        `;
};

function addThinkingMessage() {
    // Create new div
    const thinkingElement = document.createElement("div");

    // Add css classes to div
    thinkingElement.classList.add(
        "message",
        "ada-message",
        "thinking"
    );

    // Add three span elements as children to the div. These are going to be the animated thinking points
    thinkingElement.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    // Add element to chat frame and scroll down to newest message
    chat.appendChild(thinkingElement);
    chat.scrollTop = chat.scrollHeight;

    // Return the thinking element so that it can be removed later
    return thinkingElement;
}

function addMessage(message, origin) {
    // Create an empty <div></div> block
    const messageElement = document.createElement("div");
    // Give it the relevant css classes, always message and either "user-message" or "ada-message"
    messageElement.classList.add("message", origin);

    if(origin === "ada-message") {
        // Parse message with marked library to display markdown properly as html content
        const html = marked.parse(message, {
            renderer: renderer
        });
        
        // Set the content between <div></div> to the message text. Treat it innnerHTML and sanitize with DOMPurify Library to escape html code.
        messageElement.innerHTML= DOMPurify.sanitize(html);
    } else {
    // Set the content between <div></div> to the message text. Treat it as text to escape html code
    messageElement.textContent=message;

    }
    
    // Append the new element as a child to the overall chat box. Because of display flex column, it will be appended vertically automatically
    chat.appendChild(messageElement);
    // Scroll the chat box all the way down. Necessary for many messages because of overflow-y auto
    chat.scrollTop = chat.scrollHeight;
}

async function loadConversations() {
    const response = await fetch("/conversations");

    if (!response.ok) {
        throw new Error("Failed to load conversations");
        console.log(error);
    }

    const data = await response.json();

    console.log(data);

    renderConversations(data.conversations)
}

function renderConversations(conversations) {
    const list = document.getElementById("conversation-list");

    list.innerHTML = "";

    for(const conversation of conversations) {
        const item = document.createElement("div");

        item.className = "conversation-item";
        item.dataset.id = conversation.id;
        item.textContent = conversation.title ?? "New Conversation";

        item.addEventListener("click", () => {
            loadConversation(conversation.id);
        })

        list.appendChild(item)
    }
}

async function loadConversation(conversation_id) {
    const response = await fetch(`/conversations/${conversation_id}`);

    if (!response.ok) {
        console.error(
            "Failed to load conversation: ",
            response.status
        );
        return;
    }

    const conversation = await response.json();

    console.log("Loaded Conversation: ", conversation);

    setActiveConversation(conversation_id)
    renderConversation(conversation);
    
}

function renderConversation(conversation) {
    const chat = document.querySelector(".chat");

    chat.innerHTML = "";

    for (const message of conversation.messages) {
        addMessage(message.content, message.role === "assistant" ? "ada-message" : "user-message");
    }
}

function setActiveConversation(conversation_id) {
    document.querySelectorAll(".conversation-item").forEach(item => {
        item.classList.toggle(
            "active",
            item.dataset.id === conversation_id
        )
    })
}

document
    .getElementById("new-chat-button")
    .addEventListener("click", () => {
        startNewChat();
    })

function startNewChat() {
    chat.innerHTML = "";
    document
        .querySelectorAll(".conversation-item")
        .forEach( item => {
            item.classList.remove("active");
        });
    
    conversation_id = null;
}

async function checkHealth() {
    try {
        const response = await fetch("/health")
        if(!response.ok) {
            throw new Error("Health check failed");
        }
        api_status = response.json().status
        if(status === "degraded") {
            status_dot.classList.add("degraded")
            status_dot.classList.remove("offline");
            status_dot.classList.remove("online");
        }
        status_dot.classList.add("online")
        status_dot.classList.remove("offline");
        status_dot.classList.remove("degraded");
    } catch(error) {
        status_dot.classList.remove("online");
        status_dot.classList.add("offline");
        status_dot.classList.remove("degraded");
    }
}

checkHealth();
loadConversations();