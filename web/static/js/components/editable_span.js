"use strict";

let inputTemplate = (value, name) => {
    return $(`<input type="text" name="${name}" value="${value}" id="${name}-input">`)
};
let spanTemplate = (value, name) => {
    return $(`<span class="editable-span pointer llamador-hoverable llamador-subte" id="${name}-span" data-name="${name}">${value}</span><i class="fa fa-edit hoverable"></i>`)
};

let cancelButtonAction = function (event) {
    let element = $(event.data.extra.editableSpan);
    let name = `${element.data('name')}`;
    let $editableInput = $(`#${name}-input`);
    convertIntoSpan($editableInput, event.data.extra.initialValue, name);
};

let convertIntoSpan = function ($editableSpan, value, name) {
    let $okButton = $(`#${name}-ok-button`);
    let $cancelButton = $(`#${name}-cancel-button`);
    $cancelButton.fadeOut(0);
    $okButton.fadeOut(0);
    $editableSpan.replaceWith(spanTemplate(value, name));
    $(".editable-span").on('click', convertIntoInput);
};


let convertIntoInput = function () {
    let name = $(this).data('name');
    let $input = inputTemplate($(this).text(), name);
    let $okButton = $(`#${name}-ok-button`);
    let $cancelButton = $(`#${name}-cancel-button`);
    let initialValue = $(this).text();
    $(this).replaceWith($input);
    $input.select();
    $cancelButton.fadeIn(200);
    $cancelButton.on('click', {extra: {editableSpan: $(this), initialValue: initialValue}}, cancelButtonAction);
    $okButton.fadeIn(200);
};

let sendUpdate = function (endpoint, parameterName, token, id) {
    let $editableSpan = $(`#${parameterName}-input`);
    $.ajax({
        type: "POST",
        url: `${endpoint}/${id}`,
        headers: {
            Accept: "application/json",
            "X-CSRFToken": token
        },
        data: {
            parameter: parameterName,
            value: $editableSpan.val()
        }
    }).done(function (res) {
        $("#page-wrapper").append(successMessage(res.message));
        convertIntoSpan($editableSpan, $editableSpan.val(), parameterName);
    }).fail(function (err) {
        $("#page-wrapper").append(warningMessage(err.message));
        convertIntoSpan($editableSpan, $editableSpan.val(), parameterName);
        }
    );
};

$(".editable-span").on('click', convertIntoInput);