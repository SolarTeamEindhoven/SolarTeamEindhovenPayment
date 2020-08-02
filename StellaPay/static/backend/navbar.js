// When we click the logout button
$("#logout-button").on("click", function () {

    // Send request to deauthenticate.
    $.get({
        url: "/deauthenticate"
    }).done(function (data) {

        // Move user back to login-page.
        location.href = "/backend";

    }).fail(function (error) {

        // Could not log out for some reason.
        console.log("Could not log out.")
    })

});