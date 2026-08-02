document.addEventListener('DOMContentLoaded', function () {
  const deleteButtons = document.querySelectorAll('form button.btn-danger');
  deleteButtons.forEach(button => {
    button.addEventListener('click', function (event) {
      const form = event.target.closest('form');
      if (form && !confirm('Are you sure you want to perform this action?')) {
        event.preventDefault();
      }
    });
  });
});
