$("#login-button").on("click", function (event) {

    // Add a loading screen to the login box
    $(".form").addClass("loading");
    // Remove the error message box
    $("#error-message").removeClass("visible");

    // Try to login
    makeLoginAttempt().then(function (result) {
        // Successfully authenticated, so redirect client.

        // Show success message
        $("#stella-icon-loading").removeClass("hidden");
        $("#login-button-text").text("");


        // Redirect client
        setTimeout(function () {
            window.location.replace("/backend/")
        }, 2000)


    }).catch(function (result) {
        // Something went wrong while authenticating.
        // Show the error message.
        let errorMessage = $("#error-message");
        errorMessage.addClass("visible");
        errorMessage.text(result.message);
    }).finally(function () {
        // Always remove the loading icon when the promise is done.
        $(".form").removeClass("loading");
    })
})

/**
 * Make an attempt at logging in using the current credentials.
 * @returns {Promise<unknown>}
 */
function makeLoginAttempt() {
    return new Promise(function (resolve, reject) {

        // Grab the email and password input from the form
        let email = $("#input-email").val();
        let password = $("#input-password").val();

        if (email.trim() === "" || password.trim() === "") {
            reject({
                success: false,
                message: "You forgot to enter some credentials.",
                statusCode: 400
            })
            return;
        }

        // Perform a POST request to the authentication endpoint
        $.post({
            url: "/authenticate", data: JSON.stringify({
                username: email,
                password: password
            })
        }).done(function (data) {

            // User was successfully authenticated, so resolve the promise
            resolve({
                success: true,
                message: "Authenticated successfully"
            })

        }).fail(function (error) {

            // We could not authenticate, so reject the promise and pass the results.
            reject({
                success: false,
                message: error.responseText,
                statusCode: error.status
            })
        })
    });
}

// Check if user presses enter in the email or password field
$("#input-email, #input-password").keyup(function (key) {
    // Check if user presses enter
    if (key.keyCode === 13) {
        // Fake a click on the login button.
        $("#login-button").click();
    }
})




