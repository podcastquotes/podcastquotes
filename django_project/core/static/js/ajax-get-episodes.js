$(document).ready(function() {
    $('#id_podcast').change(function() {
        $('#id_episode').empty();
        $('#id_episode').append('<option>Select an episode</option>');
        $('#episode_selector').show();
        podcast_id = $(this).val();
        request_url = '/get-episodes/' + podcast_id + '/';
        $.ajax({
            url: request_url,
            success: function(data) {
                $.each(data, function(key, value) {
                    $('#id_episode').append('<option value="' + key + '">' + value + '</option>');
                });
            }
        })
    })    
});