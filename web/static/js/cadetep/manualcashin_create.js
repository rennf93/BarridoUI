function onTenantChanged() {
    var tenant = $('#id_tenant').val()
    var $channel_select = $('#id_channel');
    var $agreement_select = $('#id_agreement');
    var $agreement_type_input = $('#id_agreement_type');

    $channel_select.find('option').remove();
    $channel_select.append('<option value>Seleccione...</option>');
    $agreement_select.find('option').remove();
    $agreement_select.append('<option value>Seleccione...</option>');
    $agreement_type_input.val('');

    if (tenant)
        fetch('create/get_channels?tenant=' + tenant)
            .then(response => response.json())
            .then(json => {
                $.each(json, (key, value) => $channel_select.append('<option value=' + key + '>' + value + '</option>'));
            });
}

function onChannelChanged() {
    var tenant = $('#id_tenant').val()
    var channel = $('#id_channel').val()
    var $agreement_select = $('#id_agreement');
    var $agreement_type_input = $('#id_agreement_type');

    $agreement_select.find('option').remove();
    $agreement_select.append('<option value>Seleccione...</option>');
    $agreement_type_input.val('');

    if (tenant && channel)
        fetch('create/get_agreements?tenant=' + tenant + '&channel=' + channel)
            .then(response => response.json())
            .then(json => {
                $.each(json, (key, value) => $agreement_select.append('<option value="' + value.code + '"' +
                    ' data-agreement-type="' + value.type + '">' + value.name +
                        ' (' +  value.type + ')' + '</option>'));
            });
}

function onAgreementChanged() {
    var $agreement_select = $('#id_agreement');
    var $agreement_type_input = $('#id_agreement_type');

    if ($agreement_select.val())
        $agreement_type_input.val($('#id_agreement option:selected')[0].getAttribute("data-agreement-type"))
}
