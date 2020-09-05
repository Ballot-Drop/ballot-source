
(function($) {
    $('.js-subscribe').click(function() {
        const methods = {
            'subscribe': 'POST',
            'unsubscribe': 'DELETE'
        };
        $.ajax({
            url: urls['subscribe'],
            data: {pk: $(this).data('pk'), action: methods[$(this).data('action')] || "get"},
            method: "POST",
            success: function(data, status, jqXHR) {
                console.log('success');
                console.log(data);
                console.log(status);
                console.log(jqXHR);
            },
            error: function(jqXHR, status, e) {
                console.log(jqXHR);
                console.log(status);
                console.log(e);
            }
        });
        return false;
    });

})( jQuery );
