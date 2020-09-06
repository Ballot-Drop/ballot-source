
(function($) {
    $('.js-subscribe').click(function() {
        const methods = {
            'subscribe': 'POST',
            'unsubscribe': 'DELETE'
        };
        const _this = $(this);
        $.ajax({
            url: urls['subscribe'],
            data: {pk: $(this).data('pk'), action: methods[$(this).data('action')] || "get"},
            method: "POST",
            success: function(data, status, jqXHR) {
                if( _this.data('action') === "unsubscribe" && data.status === "unsubscribed" ){
                    _this.text("Subscribe");
                    _this.data('action', 'subscribe');
                } else if (_this.data('action') === "subscribe" && data.status === "subscribed" ) {
                    _this.text("Unsubscribe");
                    _this.data('action', 'unsubscribe');
                }
            },
            error: function(jqXHR, status, e) {
                // do nothing
            }
        });
        return false;
    });

})( jQuery );
