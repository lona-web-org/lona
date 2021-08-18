lona_context.add_disconnect_hook(function(lona_context, event) {
    document.querySelector('#lona').innerHTML = 'Server disconnected';
});
