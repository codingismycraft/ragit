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
                update_queries_from_server(data);
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
 * Updates the history view using the data retrieved from the server.
 */
function update_queries_from_server(data) {
    _historical_queries = {};
    let first_msg_id = null;
    const questionList = document.getElementById("question-list");
    questionList.innerHTML = '';
    for (let i = 0; i < data.length; i++) {
        const details = data[i];
        const msg_id = details["msg_id"];
        if (first_msg_id === null) {
            first_msg_id = msg_id;
        }

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
    if (first_msg_id != null) {
        display_query_details(first_msg_id);
    }
}

/**
 * Should be called when the used clicks on a query to display its details.
 */
function display_query_details(msg_id) {
    $("#delete_query_btn").removeClass().addClass("action_button disabled");
    const details = _historical_queries[msg_id];

    document.getElementById("query").innerText = details.question;
    document.getElementById("response").innerText = details.response;

    let label = "Response";
    if (details["thumps_up"] === 1) {
        label = "👍" + label;
    } else if (details["thumps_up"] === 0) {
        label = "👎" + label;
    }
    document.getElementById("response_label").innerText = label;

    document.getElementById("chunks").innerHTML = '';
    details.matches.forEach(chunk => {
        const chunks_container = document.getElementById("chunks");
        chunks_container.appendChild(
            display_value_in_circle(chunk["distance"])
        );

        chunks_container.appendChild(
            make_label_value("source", chunk["source"])
        )

        chunks_container.appendChild(
            make_label_value("page", chunk["page"])
        )

        const p = document.createElement("p");
        p.innerText = chunk["txt"];
        chunks_container.appendChild(p);

        const hr = document.createElement("hr");
        chunks_container.appendChild(hr);
    });
    document.getElementById("prompt").innerText = details.prompt;

    $("#temperature_span").text(details.temperature);
    $("#max_tokens_span").text(details.max_tokens);
    $("#number_of_matches_span").text(details.count_matches);

    const received_at = format_date_time(details.received_at);
    $("#received_at").text(received_at);


    $("#delete_query_btn").removeClass().addClass("action_button");

    $("#delete_query_btn").off("click");

    $("#delete_query_btn").click(function () {
        const userConfirmed = confirm(
            'Are you sure you want to delete the active query information?'
        );

        if (userConfirmed) {
            delete_query(msg_id);
        }
    })
}

/**
 * Deletes a Query from the database using the message id.
 */
function delete_query(msg_id) {
    document.body.style.cursor = 'wait';
    const url = `/queries/${msg_id}`;
    $.ajax({
            url: url,
            type: "DELETE",
            dataType: 'json',
            success: function (data) {
                document.body.style.cursor = 'default';
                retrieve_queries()
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

/**
 * Converts a data string.
 *
 * Receives a date in this format:
 * 2024-10-06T14:20:51.650732
 *
 * and returns it to the following:
 * Sun 06, October 2024 2:20 pm
 *
 */
function format_date_time(input) {
    const date = new Date(input);

    // Options for day of the week and month
    const dayOfWeekShort = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    const monthNames = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];

    // Extract components
    const dayOfWeek = dayOfWeekShort[date.getUTCDay()];
    const day = String(date.getUTCDate()).padStart(2, '0');
    const month = monthNames[date.getUTCMonth()];
    const year = date.getUTCFullYear();

    // Extract and format time components
    let hours = date.getUTCHours();
    const minutes = String(date.getUTCMinutes()).padStart(2, '0');
    const ampm = hours >= 12 ? 'pm' : 'am';
    hours = hours % 12;
    hours = hours ? hours : 12; // the hour '0' should be '12'

    return `${dayOfWeek} ${day}, ${month} ${year} ${hours}:${minutes} ${ampm}`;
}


/**
 * Create a span element to wrap the label and value
 */
function make_label_value(label, value) {
    const span = document.createElement('span');
    span.className = 'label-value-pair';

    const labelElement = document.createElement('span');
    labelElement.className = 'label';
    labelElement.textContent = label + ':';

    const valueElement = document.createElement('span');
    valueElement.className = 'value';
    valueElement.textContent = value;

    span.appendChild(labelElement);
    span.appendChild(valueElement);

    return span;
}