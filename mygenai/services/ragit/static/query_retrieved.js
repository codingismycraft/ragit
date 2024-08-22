let conversationHistory = [];

function askQuestion() {
    const userQuery = document.getElementById("userQuery").value;
     document.body.style.cursor = 'wait';
    $.ajax({
        url: "/",
        type: "POST",
        data: JSON.stringify({query: userQuery}),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        success: function (response, status) {
            const answer = response.response;
            conversationHistory.push({question: userQuery, answer: response.response});
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
        historyItem.innerHTML = `<b>Q:</b> ${item.question} <br> <b>A:</b> ${item.answer} <br><hr>`;
        historyListElement.appendChild(historyItem);
    }
}

function logout() {
    $.removeCookie('user_name', { path: '/' });
    $.removeCookie('ragit_auth_token', { path: '/' });
    location.reload();
}

