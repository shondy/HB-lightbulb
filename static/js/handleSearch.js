const sortSelect = document.querySelector('#sort');

sortSelect.addEventListener('change', (evt) => {
// when sorting is changed, initiate submit of the search form
  const searchForm = document.querySelector('#search');
  searchForm.submit();
  
});

const perpageSelect = document.querySelector('#perpage');

perpageSelect.addEventListener('change', (evt) => {
// when per page is changed, initiate submit of the search form
  const searchForm = document.querySelector('#search');
  searchForm.submit();
  
});

const pageLinks = document.querySelectorAll('.page');

for (const pageLink of pageLinks) {
  pageLink.addEventListener('click', (evt) => {
  // when first, previous, next, or last is clicked, initiate submit of the search form
    evt.preventDefault();
    console.log("ert")
    const page = document.querySelector('#page');
    page.value = pageLink.classList[1];
    const searchForm = document.querySelector('#search');
    searchForm.submit();
    
  });
}