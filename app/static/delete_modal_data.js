const modal = document.getElementById('modal');
modal.addEventListener('show.bs.modal', function (event) {
    this.querySelector('#form-delete').action = event.relatedTarget.dataset.action; 
    this.querySelector('#book_title').textContent = event.relatedTarget.dataset.title;
});