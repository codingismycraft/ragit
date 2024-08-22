let conversationHistory = [];

function askQuestion() {
    const userQuery = document.getElementById("userQuery").value;
    document.body.style.cursor = 'wait';
    $.ajax({
        url: "/ragit",
        type: "POST",
        data: JSON.stringify({query: userQuery}),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function (response, status) {
            conversationHistory.push(
                {
                    question: userQuery,
                    answer: response.response,
                    message_id: response.message_id
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

function updateHistoryList() {
    const historyListElement = document.getElementById("historyList");
    historyListElement.innerHTML = "";
    for (const item of conversationHistory) {
        const historyItem = document.createElement("div");
        historyItem.className = "history_qa";
        historyItem.classList.add("history-item");

        const thumps_up_link = `<img src="/static/thumps-up.png" alt="thumps up" width="30" height="30" onclick="user_vote(${item.message_id}, 1)">`
        const thumps_down_link = `<img src="/static/thumps-down.png" alt="thumps down" width="30" height="30" onclick="user_vote(${item.message_id}, 0)" > `

        let inner_html = `<b>Q:</b> ${item.question} <br> <b>A:</b> ${item.answer} <br><hr>`;
        inner_html += thumps_up_link;
        inner_html += thumps_down_link;
        inner_html += " <br><hr>"

        historyItem.innerHTML = inner_html;
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

