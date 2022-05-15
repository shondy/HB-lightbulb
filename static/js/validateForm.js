(function () {
  const forms = document.querySelectorAll('.requires-validation')
  for (const form of forms) {
    form.addEventListener('submit', function (evt) {
      if (!form.checkValidity()) {
        evt.preventDefault();
        evt.stopPropagation();
        form.classList.add('was-validated');
        form.classList.add('invalid');
      }
    });
    }
  })()