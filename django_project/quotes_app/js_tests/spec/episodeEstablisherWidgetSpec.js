describe('The episode establisher widget', function () {
    
    var config,
        initialWidgetHtml = $('#playfield').html();
    
    // Initialize widget
    var resetWidget = function () {
        $('#playfield').html(initialWidgetHtml);
        
        // Grab references to the html inputs.
        config = {
            podcastInputElm: $('.podcast-typeahead'),
            episodeInputElm: $('.episode-typeahead'),
            podcast_id_elm: $('#podcast_id'),
            episode_id_elm: $('#episode_id'),
            podcastSelectionIndicator: 
                $('#podcast-selection-indicator'),
            episodeSelectionIndicator: 
                $('#episode-selection-indicator'),
            episode_query_url: '/%QUERY/%PODCAST'
        };

        initEpisodeEstablisherWidget(config);
    };
    
    resetWidget();
    
    afterEach(function () {
        resetWidget();
    });
    
    it('should disable the episode selector initially', function () {
        expect(config.episodeInputElm).toBeDisabled();
    });
    
    describe('when a podcast title is typed in', function () {
        
        beforeEach(function () {
            
            // Put in some dummy id selection.
            config.podcast_id_elm.html('20202')
            
            // Simulate keypress
            config.podcastInputElm.keypress();            
        });
        
        it('should indicate that a new podcast will be created', 
            function () {
            expect(config.podcastSelectionIndicator.html())
                .toContain('A new podcast will be created');
        });
        
        it('should clear the podcast pk input value', function () {
            expect(config.podcast_id_elm.val()).toBe('');
        });
        
        it('should enable the episode input', function () {
            expect(config.episodeInputElm).not.toBeDisabled();
        });
        
    });
    
    
    var podcastSelectionSpec = function (specText, triggerName) {
        
        describe(specText, function () {
            
            var selectedPodcast;
            
            beforeEach(function () {
                
                selectedPodcast = {
                    id: 68, 
                    title: 'The Joe Rogan Experience' 
                };
                
                // Select a podcast
                config.podcastInputElm
                    .trigger(triggerName, selectedPodcast)
                
            });
            
            it('should enable the episode selector', function () {
                expect(config.episodeInputElm).not.toBeDisabled();
            });
            
            it('should indicate that it was matched', function () {
                expect(config.podcastSelectionIndicator.html())
                    .toContain('Found Podcast');
            });
            
            it('should set the podcast pk input value to the podcast key', 
                function () {
                expect(config.podcast_id_elm.val())
                    .toEqual(String(selectedPodcast.id))
            });
            
        });
    };
    
    podcastSelectionSpec("when a suggested podcast is clicked", 
        'typeahead:selected');
    podcastSelectionSpec("when a suggested podcast is scrolled to", 
        'typeahead:cursorchanged');
    podcastSelectionSpec("when a suggested podcast is tabbed to",
        'typeahead:autocompleted');
    
    
    describe('when an episode title is typed in', function () {
        
        beforeEach(function () {
            
            // Put in some dummy id selection.
            config.episode_id_elm.html('20202')
            
            // Simulate keypress
            config.episodeInputElm.keypress();            
        });
        
        it('should indicate that a new episode will be created', 
            function () {
            expect(config.episodeSelectionIndicator.html())
                .toContain('A new episode will be created');
        });
        
        it('should clear the episode pk input value', function () {
            expect(config.episode_id_elm.val()).toBe('');
        });
    });
    
    var episodeSelectionSpec = function (specText, triggerName) {
        
        describe(specText, function () {
            
            var selectedEpisode;
            
            beforeEach(function () {
                
                selectedEpisode = {
                    id: 193, 
                    title: 'Lyfe in the real world ladies and gentlemen.' 
                };
                
                // Select a podcast
                config.episodeInputElm
                    .trigger(triggerName, selectedEpisode)
                
            });
            
            it('should indicate that it was matched', function () {
                expect(config.episodeSelectionIndicator.html())
                    .toContain('Found Episode');
            });
            
            it('should set the episode pk input value to the episode id', 
                function () {
                expect(config.episode_id_elm.val())
                    .toEqual(String(selectedEpisode.id))
            });
        });
    
    };
    
    episodeSelectionSpec('when a suggested episode is clicked', 
        'typeahead:selected');
    episodeSelectionSpec('when as suggested epsisode is scrolled to',
        'typeahead:cursorchanged');
    episodeSelectionSpec('when a suggested episode is tabbed to', 
        'typeahead:autocompleted');
    

});
