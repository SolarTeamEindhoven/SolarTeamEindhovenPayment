// Get data of user we requested and use it to make an API call
const requested_user = JSON.parse(document.getElementById('requested_user').textContent);

// Only look up data if we have a specific member.
if ($("#transaction_categories").length) {
    const ctx = document.getElementById('transaction_categories').getContext('2d');

    $.post({
        url: "/transactions/user", data: JSON.stringify({
            email: requested_user.email // Use email of request user to request transactional data
        })
    }).done(function (data) {
        let productCount = new Map()

        // Loop over all transactions and find count the number of occurrence of each item
        for (let transaction of data) {
            let item_bought = transaction.item_bought

            if (productCount.has(item_bought)) {
                productCount.set(item_bought, productCount.get(item_bought) + 1)
            } else {
                productCount.set(item_bought, 1)
            }
        }

        // Function to generate random colors for the doughnut chart
        var randomColor = function () {
            var r = Math.floor(Math.random() * 255);
            var g = Math.floor(Math.random() * 255);
            var b = Math.floor(Math.random() * 255);
            return "rgb(" + r + "," + g + "," + b + ")";
        };

        let colors = [];

        // Create random colors
        for (product of productCount.keys()) {
            colors.push(randomColor())
        }

        // Generate a doughnut chart to show
        var myChart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                datasets: [{
                    backgroundColor: colors,
                    borderColor: colors,
                    // Use number of occurrences as data
                    data: Array.from(productCount.values())
                }],

                // Use name of items as labels
                labels: Array.from(productCount.keys())

            },
            options: {
                legend: {
                    // Set the labels under the doughnut chart
                    position: "bottom"
                }
            }
        });
    }).fail(function (error) {
        console.log('Error while loading pie chart.')
        console.log("Status code: " + error.status + "\nError message: " + error.responseText)
    })
}

// When the user clicks the button to remove a card
$(".remove-device-button").on("click", function (data) {

    // Get card id from table
    const cardId = $(this).parent().siblings(".card-id").text();

    // Open a modal asking if they want to remove the card
    $(".delete-card-modal").modal({
        onApprove: function () {

            $.post({
                url: "/identification/remove-card-mapping", data: JSON.stringify({
                    email: requested_user.email, // Use email of request user to request transactional data
                    card_id: cardId
                })
            }).done(function () {
                location.reload();
            }).fail(function (error) {
                console.log('Error while removing card.')
                console.log("Status code: " + error.status + "\nError message: " + error.responseText)
            });
        }
    }).modal('show');
});

// Make sure datepickers are ready
$("#fromDateInput").datepicker({
    defaultDate: -1, // Default date is yesterday
    firstDay: 1, // First day is monday
    maxDate: 0, // From date cannot be bigger than today
    dateFormat: "dd/mm/yy",
    onSelect: tryReloadTableView
});

// Make sure datepickers are ready
$("#toDateInput").datepicker({
    defaultDate: 0, // Default date is today
    firstDay: 1, // First day is monday
    maxDate: 0, // To date cannot be bigger than today
    dateFormat: "dd/mm/yy",
    onSelect: tryReloadTableView
});

// If the user clicks on a button, open the date picker
$("#fromDateButton").click(function () {
    $("#fromDateInput").datepicker("show");
});

$("#toDateButton").click(function () {
    $("#toDateInput").datepicker("show");
});

/**
 * Try to reload the view of the table (if needed). This means that only the data that is relevant is shown.
 */
function tryReloadTableView() {

    // Get from and to date using Moment.js
    fromDate = moment($("#fromDateInput").val(), "DD/MM/YYYY");
    toDate = moment($("#toDateInput").val(), "DD/MM/YYYY");

    // Check if both date inputs are valid
    if (!fromDate.isValid() || !toDate.isValid()) {
        return;
    }

    // For every entry, check the date entry and
    $(".transaction_entry").each(function () {

        // Find out what the purchase date of the item was.
        purchaseDate = moment($(this).children(".item_purchase_datetime").text(), "DD MMM YYYY - HH:mm");

        // Check if this is a valid purchase date.
        if (!purchaseDate.isValid()) return;

        // Check if item is purchased between selected dates.
        if (purchaseDate.isBetween(fromDate, toDate, "day", "[]")) {
            // Show it
            $(this).show();
        } else {
            // If this is not a valid date, hide it.
            $(this).hide();
        }
    });

    // Update total costs
    updateTotalCost();

}

/**
 * Function to update the total cost (in the footer of the transaction table)
 */
function updateTotalCost() {
    // Keep track of total cost
    totalCost = 0.0;

    // For every entry, check the date entry and
    $(".transaction_entry").each(function () {

        if ($(this).is(":visible")) {
            totalCost += parseFloat($(this).children(".item_price").text().replace("€", ""))
        }
    });

    // Update total costs
    $("#total_cost_footer").text("€" + totalCost.toFixed(2));
}

// Call it once on initial data.
updateTotalCost();


// Whenever the user clicks the generate CSV button, we open the modal to choose what CSV is generated.
$("#generateCSVButton").on("click", function () {
    // Open the modal to choose CSV type
    $(".generate-csv-modal").modal('show');
});

// Whenever the user clicks the 'only user' button (in the modal)
$("#generate-single-user-button").on("click", function () {

    // Hide icon and show loader instead
    $(this).children(".icon").hide();
    $(this).children(".loader").addClass("active").removeClass("disabled");

    // When CSV is generated ...
    generateCSVFile(false).then(r => {

        // Show icon and hide loader.
        $(this).children(".icon").show();
        $(this).children(".loader").addClass("disabled").removeClass("active");

        // Also close the modal
        $(".generate-csv-modal").modal('hide');
    });
});

// Whenever the user clicks the 'all users' button.
$("#generate-all-users-button").on("click", function () {

    // Hide icon and show loader instead
    $(this).children(".icon").hide();
    $(this).children(".loader").addClass("active").removeClass("disabled");

    // When CSV is generated ...
    generateCSVFile(true).then(r => {

        // Show icon again and hide loader
        $(this).children(".loader").addClass("disabled").removeClass("active");
        $(this).children(".icon").show();

        // Hide the modal
        $(".generate-csv-modal").modal('hide');
    });
});

/**
 * Generate a CSV file and let the client download it
 * @param allUsers True if data of all users should be included. False if only the currently selected user should be included
 */
function generateCSVFile(allUsers) {
    return new Promise((resolve, reject) => {
        let fromDate = moment.utc($("#fromDateInput").val(), "DD/MM/YYYY"); // Parse it as if it was UTC (as data is stored in UTC)
        let toDate = moment.utc($("#toDateInput").val(), "DD/MM/YYYY"); // Parse it as if it was UTC (as data is stored in UTC)

        // If the to-date is valid, we want to add a day. We want to include the whole day as well.
        if (toDate.isValid()) {
            toDate.add(1, "d");
        }

        let data = JSON.stringify({
            email: allUsers ? undefined : requested_user.email, // Use email of requester or undefined if all users are requested
            begin_date: fromDate.isValid() ? fromDate.toISOString() : undefined, // If date is not valid, don't provide it.
            end_date: toDate.isValid() ? toDate.toISOString() : undefined // If date is not valid, don't provide it.
        })

        $.post({
            url: "/transactions/generate_csv", data: data
        }).done(function (data, textStatus, jqXHR) {

            // Do some magic to convert it to a proper csv file.
            var filename = "";
            var disposition = jqXHR.getResponseHeader('Content-Disposition');
            if (disposition && disposition.indexOf('attachment') !== -1) {
                var filenameRegex = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/;
                var matches = filenameRegex.exec(disposition);
                if (matches != null && matches[1]) filename = matches[1].replace(/['"]/g, '');
            }
            var type = jqXHR.getResponseHeader('Content-Type');

            var blob;
            if (typeof File === 'function') {
                try {
                    blob = new File([data], filename, {type: type});
                } catch (e) { /* Edge */
                }
            }
            if (typeof blob === 'undefined') {
                blob = new Blob([data], {type: type});
            }

            if (typeof window.navigator.msSaveBlob !== 'undefined') {
                // IE workaround for "HTML7007: One or more blob URLs were revoked by closing the blob for which they were created. These URLs will no longer resolve as the data backing the URL has been freed."
                window.navigator.msSaveBlob(blob, filename);
            } else {
                var URL = window.URL || window.webkitURL;
                var downloadUrl = URL.createObjectURL(blob);

                // If we have a filename, try to download it.
                if (filename) {
                    // use HTML5 a[download] attribute to specify filename
                    var a = document.createElement("a");
                    // safari doesn't support this yet
                    if (typeof a.download === 'undefined') {
                        window.location.href = downloadUrl;
                    } else {
                        a.href = downloadUrl;
                        a.download = filename;
                        document.body.appendChild(a);
                        a.click();
                    }
                } else {
                    // Download the file
                    window.location.href = downloadUrl;
                }

                // Remove the URL
                setTimeout(function () {
                    URL.revokeObjectURL(downloadUrl);
                }, 100); // cleanup
            }

            resolve();

        }).fail(function (error) {

            console.log('Error getting CSV file.')
            console.log("Status code: " + error.status + "\nError message: " + error.responseText)

            reject();
        });
    });
}




