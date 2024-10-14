/*******************************************************************************
 *
 * Implements the functionality needed for the RAG front end page.
 *
 ******************************************************************************
 */


// Holds the list of the chat queries executed during the user session.
let conversationHistory = [];

/**
 * Fetches the server's response by sending the user's query.
 *
 * This function triggers an AJAX POST request to the "/ragit" endpoint,
 * sending the user's query and other related parameters. On a successful
 * response, it updates the conversation history and clears the query input. If
 * an error occurs, an alert displays the error message.
 *
 */
function make_query() {
    const userQuery = document.getElementById("userQuery").value;
    const temperature = document.getElementById("temperature").value;
    const max_tokens = document.getElementById("max_tokens").value;
    const matches_count = document.getElementById("matches_count").value;

    document.body.style.cursor = 'wait';
    $.ajax({
        url: "/ragit",
        type: "POST",
        data: JSON.stringify(
            {
                query: userQuery,
                temperature: temperature,
                max_tokens: max_tokens,
                matches_count: matches_count
            }
        ),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function (response, status) {
            conversationHistory.push(
                {
                    question: userQuery,
                    answer: response.response,
                    message_id: response.message_id,
                    vote: null
                }
            );
            update_history_list();
            document.getElementById("userQuery").value = "";
            document.body.style.cursor = 'default';
        },
        error: function (request, status, error) {
            document.body.style.cursor = 'default';
            alert(request.responseText);
        }
    });
}

function load_recent_chats() {
    document.body.style.cursor = 'wait';
    $.ajax({
        url: "/recentchats/10",
        type: "GET",
        dataType: 'json',
        success: function (data, status) {
            document.body.style.cursor = 'default';
            for (let i = 0; i < data.length; i++) {
                conversationHistory.push(
                    {
                        question: data[i]["query"],
                        answer: data[i]["response"],
                        message_id: data[i]["msg_id"],
                        vote: data[i]["thumps_up"]
                    }
                );
            }
            update_history_list();
            document.getElementById("userQuery").value = "";
        },
        error: function (request, status, error) {
            alert(request.responseText);
        }
    });
}

/**
 * Creates a chat item element based on the provided data.
 *
 * This function generates a HTML structure representing a chat message,
 * including the question, answer, and voting options. The response answer
 * supports markdown formatting, and votes can be indicated by thumbs-up and
 * thumbs-down images.
 *
 * @param {Object} item - The chat item data.
 *
 * @param {string} item.question - The question text in the chat item.
 *
 * @param {string} item.answer - The answer text in the chat item.
 *
 * @param {number} item.vote - The vote state of the answer (1 for upvote, 0
 * for downvote, else neutral).
 *
 * @param {string} item.message_id - The unique identifier for the message.
 *
 * @returns {HTMLDivElement} The constructed chat item element.
 *
 */
function make_chat_item(item) {
    const chat_div = document.createElement("div");
    chat_div.className = "chat_message";

    const question_div = document.createElement("div");
    question_div.className = "chat_question";

    const question_span = document.createElement("span");

    const question_mark_img = document.createElement("img");
    question_mark_img.src = "/static/question_mark.png";
    question_mark_img.width = 30;
    question_mark_img.height = 30;
    question_mark_img.className = "question_mark_img";
    question_span.appendChild(question_mark_img);

    question_span.innerHTML += item.question;
    question_div.appendChild(question_span);
    chat_div.appendChild(question_div);

    const answer_div = document.createElement("div");
    answer_div.className = "chat_answer";

    answer_div.innerHTML = marked.parse(item.answer);
    chat_div.appendChild(answer_div);

    // chat_div.appendChild(create_audio_tag(item.message_id));
    const user_vote_div = document.createElement("div");
    user_vote_div.className = "chat_vote";

    const thumps_up_img = document.createElement("img");
    thumps_up_img.title = "Thumps Up Voting";
    thumps_up_img.src = "/static/thumps-up.png";
    thumps_up_img.width = 20;
    thumps_up_img.height = 20;
    thumps_up_img.onclick = function () {
        user_vote(item.message_id, 1);
    }

    if (item.vote === 1){
        thumps_up_img.className = "user_input_button selected_button";
    }
    else {
        thumps_up_img.className = "user_input_button";
    }

    user_vote_div.appendChild(thumps_up_img);

    const thumps_down_img = document.createElement("img")
    thumps_down_img.title = "Thumps Down Voting";
    thumps_down_img.className = "user_input_button";
    thumps_down_img.src = "/static/thumps-down.png";
    thumps_down_img.width = 20;
    thumps_down_img.height = 20;
    thumps_down_img.onclick = function () {
        user_vote(item.message_id, 0);
    }

    if (item.vote === 0){
        thumps_down_img.className = "user_input_button selected_button";
    }
    else {
        thumps_down_img.className = "user_input_button";
    }

    user_vote_div.appendChild(thumps_down_img);

    const copy_question_img = document.createElement("img")
    copy_question_img.title = "Copy to Clipboard";
    copy_question_img.className = "user_input_button";
    copy_question_img.src = "/static/copy.png";
    copy_question_img.width = 30;
    copy_question_img.height = 30;
    copy_question_img.text_to_copy = `Question: ${item.question} Answer: ${item.answer}`;
    copy_question_img.onclick = function () {
        navigator.clipboard.writeText(this.text_to_copy);
    }
    user_vote_div.appendChild(copy_question_img);
    chat_div.appendChild(user_vote_div);

    return chat_div;
}

function create_audio_tag(msg_id) {
    const audioTag = document.createElement('audio');
    audioTag.controls = true;

    audioTag.appendChild(document.createElement('source'));
    audioTag.lastElementChild.src = `/speechify/${msg_id}`;
    audioTag.lastElementChild.type = 'audio/mpeg';

    const fallbackMessage = document.createTextNode(
        'Your browser does not support the audio element.'
    );

    audioTag.appendChild(fallbackMessage);

    return audioTag;
}

/**
 * Updates the conversation history list on the webpage.
 *
 * This function clears the existing content in the history list element and
 * populates it with chat items based on the `conversationHistory` array.
 */
function update_history_list() {
    const history_list = document.getElementById("historyList");
    history_list.innerHTML = "";
    for (const item of conversationHistory) {
        const historyItem = make_chat_item(item);
        history_list.appendChild(historyItem);
    }
    // Scroll to the bottom
    history_list.scrollTop = history_list.scrollHeight;
}

/**
 * Sends to server a vote for a message and updates the conversation history.
 *
 * This function triggers an AJAX POST request to the "/vote" endpoint with the
 * message ID and vote value.  Upon successful response, it updates the vote
 * value in the global `conversationHistory` array and refreshes the history
 * list on the webpage. In case of an error, it shows an alert with the error
 * message.
 *
 */
function user_vote(message_id, vote) {
    document.body.style.cursor = 'wait';
    $.ajax({
        url: "/vote",
        type: "POST",
        data: JSON.stringify({message_id: message_id, vote: vote}),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function (response, status) {
            for (const item of conversationHistory) {
                if (item.message_id === message_id) {
                    item.vote = vote
                }
            }
            update_history_list();
            document.body.style.cursor = 'default';
        },
        error: function (request, status, error) {
            document.body.style.cursor = 'default';
            alert(request.responseText);
        }
    });
}


/**
 * Logs the user out by removing authentication cookies and reloading the page.
 *
 * This function deletes the 'user_name' and 'ragit_auth_token' cookies from
 * the root path, and then reloads the current webpage to reflect the logout
 * status.
 */
function logout() {
    $.removeCookie('user_name', {path: '/'});
    $.removeCookie('ragit_auth_token', {path: '/'});
    location.reload();
}
