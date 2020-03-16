const Operations = {
    operationsTable: $('#operations-table').DataTable(),
    filterForm: {
        date: document.getElementsByName('fecha'),
        filterMain: document.getElementsByName('filtro'),
        filterButton: document.getElementById('enviar-filtro')
    }
};

if (window.location.href.includes('filter')) {
    const params = window.location.href.split('/');
    const date = params[params.length - 1];
    const filter = params[params.length - 2];
    Operations.filterForm.date[0].value = date;
    checkForm(filter);
}

function checkForm(radioButton) {
    document.getElementById('filtro-' + radioButton).checked = true;
}

function filtrar() {
    let filterType = 'journal';
    if (Operations.filterForm.date[0].value === '' || Operations.filterForm.filterMain[0].value === '') {
        window.location.href = '/cadete/operations';
        return;
    }
    Operations.filterForm.filterMain.forEach((el) => {
        if (el.checked) {
            filterType = el.value;
        }
    });
    window.location.href = "/cadete/operations/filter/" + filterType + '/' +
        Operations.filterForm.date[0].value;
}