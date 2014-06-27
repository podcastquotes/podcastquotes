jQuery(document).ready(function($) {
    $(".vote_form").submit(function(e) {
            e.preventDefault();
            var btn = $("button", this);
            var q_id = $("#id_quote", this).val();
            var btn_upvote = document.getElementById('pq-quote-upvote-' + q_id);
            var btn_downvote = document.getElementById('pq-quote-downvote-' + q_id);
            var currentValue = parseInt($('#pq-quote-vote-total-' + q_id).text(),10);
            btn.attr('disabled', true);
            $.post("/clips/vote/", $(this).serializeArray(),
                function(data) {
                    if(data["newupvoteobj"]) {
                        $('#pq-quote-upvote-' + q_id).addClass("pq-quote-upvote-active");
                        $('#pq-quote-xs-upvote-' + q_id).addClass("pq-quote-upvote-active");
                        var newValue = currentValue + 1;
                        $('#pq-quote-vote-total-' + q_id).text(newValue);
                        $('#pq-quote-xs-vote-total-' + q_id).text(newValue);
                    } else if (data["newdownvoteobj"]) {
                        $('#pq-quote-downvote-' + q_id).addClass("pq-quote-downvote-active");
                        $('#pq-quote-xs-downvote-' + q_id).addClass("pq-quote-downvote-active");
                        var newValue = currentValue - 1;
                        $('#pq-quote-vote-total-' + q_id).text(newValue);
                        $('#pq-quote-xs-vote-total-' + q_id).text(newValue);
                    } else if (data["upvoteobj"]) {
                        $('#pq-quote-upvote-' + q_id).addClass("pq-quote-upvote-active");
                        $('#pq-quote-xs-upvote-' + q_id).addClass("pq-quote-upvote-active");
                        $('#pq-quote-downvote-' + q_id).removeClass('pq-quote-downvote-active');
                        $('#pq-quote-xs-downvote-' + q_id).removeClass('pq-quote-downvote-active');
                        var newValue = currentValue + 2;
                        $('#pq-quote-vote-total-' + q_id).text(newValue);
                        $('#pq-quote-xs-vote-total-' + q_id).text(newValue);
                    } else if (data["downvoteobj"]) {
                        $('#pq-quote-downvote-' + q_id).addClass("pq-quote-downvote-active");
                        $('#pq-quote-xs-downvote-' + q_id).addClass("pq-quote-downvote-active");
                        $('#pq-quote-upvote-' + q_id).removeClass('pq-quote-upvote-active');
                        $('#pq-quote-xs-upvote-' + q_id).removeClass('pq-quote-upvote-active');
                        var newValue = currentValue - 2;
                        $('#pq-quote-vote-total-' + q_id).text(newValue);
                        $('#pq-quote-xs-vote-total-' + q_id).text(newValue);
                    } else if (data["un_upvoted"]) {
                        $('#pq-quote-upvote-' + q_id).removeClass("pq-quote-upvote-active");
                        $('#pq-quote-xs-upvote-' + q_id).removeClass("pq-quote-upvote-active");
                        var newValue = currentValue - 1;
                        $('#pq-quote-vote-total-' + q_id).text(newValue);
                        $('#pq-quote-xs-vote-total-' + q_id).text(newValue);
                    } else if (data["un_downvoted"]) {
                        $('#pq-quote-downvote-' + q_id).removeClass("pq-quote-downvote-active");
                        $('#pq-quote-xs-downvote-' + q_id).removeClass("pq-quote-downvote-active");
                        var newValue = currentValue + 1;
                        $('#pq-quote-vote-total-' + q_id).text(newValue);
                        $('#pq-quote-xs-vote-total-' + q_id).text(newValue);
                    }
                    });
                btn.attr('disabled', false);
            });
        });