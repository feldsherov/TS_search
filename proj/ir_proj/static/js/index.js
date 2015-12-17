function loadSearchWindow() {
    window.location.href = "/search?query=" + $("#search-input").val();
};

function initSearchRow() {
    $("#loop").click(function() {
        if ($("#search-input").val() !== "") {
            loadSearchWindow();
        }
    });

    $("#search-input").keydown(function(event) {
        if ($("#search-input").val() !== "" && event.which == 13) {
            loadSearchWindow();
        }
    });
};
