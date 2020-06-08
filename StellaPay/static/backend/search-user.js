// Initialize HTML element as dropdown box in SemanticUI
$('.ui.dropdown').dropdown({
    onChange: function (value, text) {
        // Grab current URL
        let url = window.location.href;

        // Try to find the ? symbol
        if (url.indexOf('?') > -1) {
            // There already is one, so append to the other params
            url += '&user=' + value
        } else {
            // There is none yet, so just add it to the URL
            url += '?user=' + value
        }

        // Go to page with new url
        window.location.href = url;
    }
});