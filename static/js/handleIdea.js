const addIdeaButton = document.querySelector('#add-idea');

addCommentButton.addEventListener('click', (evt) => {
// check first if user loged in and open a window with comment form
  if (evt.target.classList.contains('active')) {
    fetch("/ideas")
    .then(response => response.json())
    .then((responseJson) => {
      if (responseJson.success) {
        window.history.pushState();
      }
    });
  }
  else {
    alert("Please Sign in/Join to be able to add ideas")
  }
});