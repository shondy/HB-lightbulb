const sortSelect = document.querySelector('#sort');

sortSelect.addEventListener('change', (evt) => {
// when sorting is changed, initiate submit of the search form
  const searchForm = document.querySelector('#search');
  searchForm.submit();
  
});