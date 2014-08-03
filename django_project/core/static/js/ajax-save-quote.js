jQuery(document).ready(function($) {
    $(".save_form").submit(function(e) {
            e.preventDefault();
            var btn = $("button", this);
            var q_id = $("#id_quote", this).val();
            var save_btn = document.getElementById('pq-quote-save-button-' + q_id);
            btn.attr('disabled', true);
            $.post("/highlights/save/", $(this).serializeArray(),
                function(data) {
                    if(data["savedquote"]) {
                        $(save_btn).addClass("text-yellow");
                        save_btn.innerHTML = "saved";
                    } else if (data["unsavedquote"]) {
                        $(save_btn).removeClass("text-yellow");
                        save_btn.innerHTML = "save";
                    }
                });
            btn.attr('disabled', false);
        });
    });