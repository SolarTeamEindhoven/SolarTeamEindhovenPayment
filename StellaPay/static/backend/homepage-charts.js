var ctx = document.getElementById('transaction_categories').getContext('2d');

$.post({
    url: "/transactions/all", data: JSON.stringify({})
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

