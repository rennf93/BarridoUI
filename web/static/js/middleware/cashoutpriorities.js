function send_products(token) {

    let table = $(".product-row");
    let products = [];
    let companyId = $("#products-table").data('company');
    console.log(companyId)

    for (let i = 1; i < table.size() + 1; i++) {
        let valor = $(`.product-row:nth-of-type(${i})`).data('value');
        console.log($(`.product-row:nth-of-type(${i})`).data('value'));
        products.push(valor);
    }
    products_string = products.join(',')
    console.log(products_string);
     $.ajax({
        type: "POST",
        url: `./cashoutpriorities/update/${companyId}`,
        headers: {
            Accept: "application/json",
            "X-CSRFToken": token
        },
        data: {
           products_string
        }
    }).done(function (res) {
        console.log(res);
        $("#page-wrapper").append(successMessage(res.message));
        convertIntoSpan($editableSpan, $editableSpan.val(), parameterName);
    }).fail(function (err) {
        console.log(err);
        $("#page-wrapper").append(warningMessage(err.message));
        convertIntoSpan($editableSpan, $editableSpan.val(), parameterName);
        }
    );

}

function on_click_company(token) {

    let companyId = $("#select-company option:selected").val();
    let companyName = $("#select-company option:selected").text();
    console.log(companyId);
    console.log(companyName)

    let encodedCompanyName = encodeURIComponent(companyName);

    $("body").load(
        "./cashoutpriorities?company_id=" + companyId + "&company_name=" + encodedCompanyName
    );
}