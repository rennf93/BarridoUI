"use strict";

let warningMessage = (text) => {
    return `
<div class="jq-toast-wrap top-right">
    <div class="jq-toast-single jq-has-icon jq-icon-error" style="text-align: left; display: block;">
        <span class="jq-toast-loader"></span><span class="close-jq-toast-single" onclick="closeToast()">×</span>
        ${text}
    </div>
</div>`
};

let successMessage = (text) => {
    return `
<div class="jq-toast-wrap top-right">
    <div class="jq-toast-single jq-has-icon jq-icon-success" style="text-align: left; display: block;">
        <span class="jq-toast-loader"></span><span class="close-jq-toast-single" onclick="closeToast()">×</span>
        ${text}
    </div>
</div>`
};

let closeToast = () => {
    $(".jq-toast-wrap").remove();
};