// Initialize HTML element as dropdown box in SemanticUI
$('.ui.dropdown').dropdown({
    onChange: function (value, text) {
        // Grab current URL
        let url = new window.URL(document.location);

        // Set paramater 'user' to email address of user.
        url.searchParams.set("user", value);

        // Go to page with new url
        window.location.href = url.toString();
    }
});