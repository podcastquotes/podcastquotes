beforeEach(function () {
  jasmine.addMatchers({
      
    toBeDisabled: function () {
        
      return {
        compare: function (actual) {
          
          var passed = actual.prop('disabled') === true;
          var message;
          
          if (passed) {
            message = "The element is disabled.";
          }
          
          else {
            message = "The element is not disabled.";
          }
          return {
            pass: passed,
            message: message
          }
          
        }
      };
      
    }
    
  });
});
