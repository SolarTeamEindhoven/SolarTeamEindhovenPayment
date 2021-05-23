var leaderboard_people_weekly = document.getElementById('leaderboard_people_weekly').getContext('2d');
var leaderboard_people_monthly = document.getElementById('leaderboard_people_monthly').getContext('2d');
var leaderboard_transactions_weekly = document.getElementById('leaderboard_transactions_weekly').getContext('2d');
var leaderboard_transactions_monthly = document.getElementById('leaderboard_transactions_monthly').getContext('2d');

// Get start and end date of the week
let weekStartAndEndDate = getStartAndEndDateOfWeek();
let monthStartAndEndDate = getStartAndEndDateOfMonth();

// Store data of each user per day
// key = date
// value = dict of <user, list[transactions]>
var dataStore = {};

$.post({
    url: "/transactions/all", data: JSON.stringify({
        begin_date: monthStartAndEndDate.start.toISOString(),
        end_date: monthStartAndEndDate.end.toISOString()
    })
}).done(function (data) {
    let productCount = new Map()

    console.log(data)

    // Loop over all transactions and find count the number of occurrence of each item
    for (let transaction of data) {
        let date = Date.parse(transaction.purchase_date);
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
    // var myChart = new Chart(leaderboard_people_weekly, {
    //     type: 'doughnut',
    //     data: {
    //         datasets: [{
    //             backgroundColor: colors,
    //             borderColor: colors,
    //             // Use number of occurrences as data
    //             data: Array.from(productCount.values())
    //         }],
    //
    //         // Use name of items as labels
    //         labels: Array.from(productCount.keys())
    //
    //     },
    //     options: {
    //         legend: {
    //             // Set the labels under the doughnut chart
    //             position: "bottom"
    //         }
    //     }
    // });
    //

    console.log(getStartAndEndDateOfWeek());
    console.log(getStartAndEndDateOfMonth());


    let weekDates = [];
    let monthDates = [];


    // Iterate over the days and show it as x-labels for the week days
    for (let dayNumber = 0; dayNumber < 7; dayNumber++) {
        weekDates.push(weekStartAndEndDate.start.toLocaleString('en-US', {weekday: "long"}));
        weekStartAndEndDate.start.setDate(weekStartAndEndDate.start.getDate() + 1)
    }

    while (monthStartAndEndDate.start <= monthStartAndEndDate.end) {
        monthDates.push(monthStartAndEndDate.start.toLocaleString('nl-NL', {
            year: "numeric",
            month: "numeric",
            day: "numeric"
        }));
        monthStartAndEndDate.start.setDate(monthStartAndEndDate.start.getDate() + 1)
    }

    // console.log("First day of the week: " + firstDayOfWeek);
    // console.log("Last day of the week: " + lastDayOfWeek);

    var myChart = new Chart(leaderboard_people_weekly, {
        type: 'line',
        data: {
            datasets: [{
                label: "Vincent Bolta",
                // Use number of occurrences as data
                data: [1, 2, 2, 3, 4, 5, 6, 7],
                fill: false,
                borderColor: randomColor()
            }, {
                label: "Ava Swevels",
                // Use number of occurrences as data
                data: [3, 3.2, 3, 4, 4, 5, 6, 6],
                fill: false,
                borderColor: randomColor()
            }],

            // Use name of items as labels
            labels: weekDates

        },
        options: {
            legend: {
                // Set the labels under the doughnut chart
                position: "bottom"
            }
        }
    });

    var myChart = new Chart(leaderboard_people_monthly, {
        type: 'line',
        data: {
            datasets: [{
                label: "Vincent Bolta",
                // Use number of occurrences as data
                data: [1, 2, 2, 3, 4, 5, 6, 7],
                fill: false,
                borderColor: randomColor()
            }, {
                label: "Ava Swevels",
                // Use number of occurrences as data
                data: [3, 3.2, 3, 4, 4, 5, 6, 6],
                fill: false,
                borderColor: randomColor()
            }],

            // Use name of items as labels
            labels: monthDates

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

function getStartAndEndDateOfWeek() {
    var currentDate = new Date;
    var firstDayOfWeek = currentDate.getDate() - currentDate.getDay() + 1;
    var lastDayOfWeek = firstDayOfWeek + 6;

    firstDayOfWeek = new Date(currentDate.setDate(firstDayOfWeek));
    firstDayOfWeek.setUTCHours(0, 0, 0, 0);

    lastDayOfWeek = new Date(currentDate.setDate(lastDayOfWeek));
    lastDayOfWeek.setUTCHours(0, 0, 0, 0);

    return {
        start: firstDayOfWeek,
        end: lastDayOfWeek
    };
}

function getStartAndEndDateOfMonth() {
    var currentDate = new Date;
    var firstDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1);
    var lastDayOfMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0);

    return {
        start: firstDayOfMonth,
        end: lastDayOfMonth
    };
}

