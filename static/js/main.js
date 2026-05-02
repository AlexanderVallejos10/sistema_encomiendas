document.addEventListener('DOMContentLoaded', function () {
    const tooltips = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltips.forEach(function (el) {
        new bootstrap.Tooltip(el);
    });

    setTimeout(function () {
        document.querySelectorAll('.alert').forEach(function (alert) {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);

    window.confirmar = function (mensaje) {
        return confirm(mensaje || '¿Estás seguro?');
    };

    document.querySelectorAll('.fila-link').forEach(function (fila) {
        fila.addEventListener('click', function () {
            window.location = this.dataset.href;
        });
    });
});