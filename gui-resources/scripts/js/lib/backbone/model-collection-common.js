'use strict';

// Shared functions and variables for collections and models.
define({

    // Params to be added automatically to the request
    // headers:     added to request header in all requests
    // data:        added as url parameters in all requests
    // pagination:  (for collections only) added as url parameters in pagination requests
    // updates   :  (for collections only) added as url parameters in requests for collection updates
    syncParams: {
        headers: {},
        data: {}
    }
});
