function loadSearchWindow() {
    window.location.href = "/search?query=" + $("#search-input").val();
};

function updateSearchResults() {
    $.get("/searchJSON?query=" + $("#search-input").val(),
            function (data, status) {
                $('#content').empty();
                $('#spell-area').empty();
                if (data.spell && data.spell !== $("#search-input").val()) {
                    $("#spell-tmpl").tmpl(data).appendTo("#content");
                    $('#spell-area').on('click', function() {
                    });
                }
                if (data.error) {
                    $('#content').append("Упс ничего не нашлось :(");
                }
                else {
                    $.each(data.result, function (id) {
                                            res = data.result[id]
                                            $("#result-tmpl").tmpl(res).appendTo('#content');
                                        });
                    $('#content').on('click', '.result', function() {
                    });
                }
            });
}

function initSearchRow() {
    $("#loop").click(function() {
        if ($("#search-input").val() !== "") {
            updateSearchResults();
        }
    });

    $("#search-input").keydown(function(event) {
        if ($("#search-input").val() !== "" && event.which == 13) {
            updateSearchResults();
        }
    });
};
