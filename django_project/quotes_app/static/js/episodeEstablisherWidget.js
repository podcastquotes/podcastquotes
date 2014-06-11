var initEpisodeEstablisherWidget = function (config) {


    var podcastInputElm = config.podcastInputElm,
        episodeInputElm = config.episodeInputElm,
        podcast_id_elm = config.podcast_id_elm,
        episode_id_elm = config.episode_id_elm,
        episodeSelectionIndicator = config.episodeSelectionIndicator,
        podcastSelectionIndicator = config.podcastSelectionIndicator,
        
        // HARDCODED WARNING
        episode_query_url = '/episodes/json?q=%QUERY&podcast_id=%PODCAST',
        podcast_query_url = '/podcasts/json?q=%QUERY';


    var createEpisodeQueryUrl = function (url, query) {
        /**
        * Helper function which will fill 
        * out which episodes to query on.
        */

        this.podcast_id = this.podcast_id || '';

        url = url.replace("%QUERY", query);
        url = url.replace("%PODCAST", this.podcast_id);

        return url;
    }

    //
    // Configure the bloodhounds
    //

    var podcastBloodhound = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('title'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: podcast_query_url,
        }
    });

    var episodeBloodhound = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('title'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        remote: {
            url: episode_query_url,
            replace: createEpisodeQueryUrl.bind(createEpisodeQueryUrl)
        }
    });

    podcastBloodhound.initialize();
    episodeBloodhound.initialize();

    //
    // Activate typeaheads on inputs
    //
    var podcastSelectionHandler = function (event, podcast, name) {

        // Configure the episode url creator to 
        // use the selected podcast id.
        createEpisodeQueryUrl.podcast_id = podcast.id;

        // Set value of podcast_id to selected podcast
        podcast_id_elm.val(podcast.id);

        // Indicate that an existing episode was selected
        podcastSelectionIndicator.html('Found Podcast');

        // Enable Episode Selector
        episodeInputElm.prop('disabled', false);

    }

    podcastInputElm.typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },{
        name: 'podcast',
        displayKey: 'title',
        source: podcastBloodhound.ttAdapter()
    })
        .on('typeahead:selected', podcastSelectionHandler)
        .on('typeahead:cursorchanged', podcastSelectionHandler)
        .keypress(function() {
            podcastSelectionIndicator.html('A new podcast will be created');
            episodeInputElm.prop('disabled', false);
        });


    episodeInputElm.typeahead({
        hint: true,
        highlight: true,
        minLength: 1
    },{
        name: 'episode',
        displayKey: 'title',
        source: episodeBloodhound.ttAdapter()
    })
        .on('typeahead:selected', function (event, episode, name) {
            // Set value of podcast_id to selected podcast
            episode_id_elm.val(episode.id);

            // Indicate that an existing episode was selected
            episodeSelectionIndicator.html('Found Episode');
        })
        .keypress(function() {
            episodeSelectionIndicator.html('A new episode will be created');
        });

    // Set initial states
    episodeInputElm.prop('disabled', true);

};
