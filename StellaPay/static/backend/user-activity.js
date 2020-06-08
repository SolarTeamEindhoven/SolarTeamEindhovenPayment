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

