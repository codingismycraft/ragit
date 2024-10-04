/*******************************************************************************
 * Provides functionality for the history web page.
 *
 * This module is intended exclusively for the history page. It contains
 * functions necessary to fetch and manage the historical data for
 * user-executed queries.
 *
 * Functionality Overview:
 * -----------------------
 * - Utilizes the /queries endpoint of the Ragit server to retrieve all
 * available historical data when the history page is loaded.
 *
 * - Stores the retrieved data in memory, enabling users to select and view
 *   any of the available conversations through the front-end interface.
 *
 * Future Improvements:
 * --------------------
 * As the volume of historical data increases, the current approach may lead
 * to memory and performance issues. Future enhancements will focus on making
 * data retrieval and management more dynamic to mitigate these issues.
 ******************************************************************************
 */

// Stores the retrieved queries in memory.
let _historical_queries = null;

/**
 * Loads the queries and their details calling the API.
 *
 * The function performs the following operations:
 *
 * 1. Iterates over the received data to populate the left-hand query list.
 *    Users can click on an item to view its details on the right side.
 *
 * 2. Constructs a dictionary that maps each message ID to its query details.
 *    This caching mechanism accelerates query lookup in response to user
 *    clicks.
 *
 * Queries are presented in the same order as received from the server,
 * typically sorted by creation time, with the most recent queries displayed
 * first.
 */
function retrieve_queries() {
    document.body.style.cursor = 'wait';
    _historical_queries = {};
    $.ajax({
            url: "/queries",
            type: "GET",
            dataType: 'json',
            success: function (data) {
                document.body.style.cursor = 'default';
                _historical_queries = {};
                const questionList = document.getElementById("question-list");
                for (let i = 0; i < data.length; i++) {
                    const details = data[i];
                    const msg_id = details["msg_id"];
                    _historical_queries[msg_id] = details;
                    const question = details["question"];
                    const li = document.createElement("li");
                    let label = question;
                    if (details["thumps_up"] === 1) {
                        label = "👍" + question;
                        li.className = "thumps_up_query";
                    } else if (details["thumps_up"] === 0) {
                        li.className = "thumps_down_query";
                        label = "👎" + question;
                    }
                    li.innerText = label;
                    li.addEventListener(
                        "click", () => display_query_details(msg_id)
                    );
                    questionList.appendChild(li);
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

/**
 * Should be called when the used clicks on a query to display its details.
 */
function display_query_details(msg_id) {
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

/**
 * Displays a number insider a circle.
 *
 * Creates a span element containing a number formatted to two decimal places,
 * styled to be displayed inside a circle.
 */
function display_value_in_circle(value) {
    const span = document.createElement("span");
    span.className = "circled_number";
    span.textContent = value.toFixed(2);
    return span;
}
