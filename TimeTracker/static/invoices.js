function onInvoiceStateChange(_client_id, _timestamp, _num)
{
    $.getJSON(
        $SCRIPT_ROOT + '/invoices/change_state',
        {
            ClientID: _client_id,
            timestamp: _timestamp,
            state: $('select#'+_client_id+_timestamp).val(),
            num: _num
        },
        function(data)
        {

        }
    );
}
