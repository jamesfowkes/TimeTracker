function onInvoiceStateChange(_client_id, _date_identifier, _num, _timestamp)
{
    $.getJSON(
        $SCRIPT_ROOT + '/invoices/change_state',
        {
            ClientID: _client_id,
            date_identifier: _date_identifier,
            state: $('select#'+_client_id+_timestamp).val(),
            num: _num
        },
        function(data)
        {

        }
    );
}
