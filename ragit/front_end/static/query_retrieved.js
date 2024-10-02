let conversationHistory = [];
let _historical_queries = null;

function askQuestion() {
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
            conversationHistory.unshift(
                {
                    question: userQuery,
                    answer: response.response,
                    message_id: response.message_id,
                    vote: null
                }
            );
            updateHistoryList();
            document.getElementById("userQuery").value = "";
            document.body.style.cursor = 'default';
        },
        error: function (request, status, error) {
            document.body.style.cursor = 'default';
            alert(request.responseText);
        }
    });
}

function make_chat_item(item) {
    const chat_div = document.createElement("div");
    chat_div.className = "chat_message";

    const question_div = document.createElement("div");
    question_div.className = "chat_question";


    question_div.innerText = item.question;
    chat_div.appendChild(question_div);

    const answer_div = document.createElement("div");
    answer_div.className = "chat_answer";


    if (item.vote === 1) {
        answer_div.className = "chat_answer chat_vote_up";
    } else if (item.vote === 0) {
        answer_div.className = "chat_answer chat_vote_down";
    } else {
        answer_div.className = "chat_answer";
    }

    answer_div.innerHTML = marked.parse(item.answer);
    chat_div.appendChild(answer_div);

    const user_vote_div = document.createElement("div");
    user_vote_div.className = "chat_vote";

    const thumps_up_img = document.createElement("img");
    thumps_up_img.src = "/static/thumps-up.png";
    thumps_up_img.width = 20;
    thumps_up_img.height = 20;
    thumps_up_img.onclick = function () {
        user_vote(item.message_id, 1);
    }
    user_vote_div.appendChild(thumps_up_img);

    const thumps_down_img = document.createElement("img")
    thumps_down_img.src = "/static/thumps-down.png";
    thumps_down_img.width = 20;
    thumps_down_img.height = 20;
    thumps_down_img.onclick = function () {
        user_vote(item.message_id, 0);
    }
    user_vote_div.appendChild(thumps_down_img);
    chat_div.appendChild(user_vote_div);

    return chat_div;

}

function updateHistoryList() {
    const historyListElement = document.getElementById("historyList");
    historyListElement.innerHTML = "";
    for (const item of conversationHistory) {
        const historyItem = make_chat_item(item);
        historyListElement.appendChild(historyItem);
    }
}

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
            updateHistoryList();
            document.body.style.cursor = 'default';
        },
        error: function (request, status, error) {
            document.body.style.cursor = 'default';
            alert(request.responseText);
        }
    });
}

function logout() {
    $.removeCookie('user_name', {path: '/'});
    $.removeCookie('ragit_auth_token', {path: '/'});
    location.reload();
}

/**
 * Loads the queries and their details (like the matching chunks that
 * were used for the RAG creation.  This function is meant to be used
 * to display the history window that is part of the validation process.
 */
function retrieve_queries() {
    document.body.style.cursor = 'wait';
    $.ajax({
            url: "/queries",
            type: "GET",
            dataType: 'json',
            success: function (data) {
                document.body.style.cursor = 'default';
                _historical_queries = data;
                const questionList = document.getElementById("question-list");
                for (let key in _historical_queries) {
                    if (data.hasOwnProperty(key)) {
                        const msg_id = key;
                        const details = _historical_queries[key];
                        const question = details["question"];
                        const li = document.createElement("li");
                        li.innerText = question;
                        li.addEventListener("click", () => display_query_details(msg_id));
                        questionList.appendChild(li);
                    }
                }
            },
            error: function (request, status, error) {
                document.body.style.cursor = 'default';
                console.error(error)
                alert(request.responseText);
            }
        }
    )
}

function display_query_details(msg_id){
    const details = _historical_queries[msg_id];

    document.getElementById("query").innerText = details.question;
    document.getElementById("response").innerText = details.response;

    document.getElementById("chunks").innerHTML = '';
    details.matches.forEach(chunk => {
        document.getElementById("chunks").appendChild(
            display_value_in_circle(chunk["distance"])
        );
        const p = document.createElement("p");
        p.innerText = chunk["txt"];
        document.getElementById("chunks").appendChild(p);
        const hr = document.createElement("hr");
        document.getElementById("chunks").appendChild(hr);
    });
    document.getElementById("prompt").innerText = details.prompt;
}
