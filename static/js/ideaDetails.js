function handleIdea(url, method, title, description, link) {
  // create fetch request for create/update an idea
  // return to previous refreshed window 
  const ideaJSON = {
    title: title,
    description: description,
    link: link,
  };

  fetch(url, {
    method: method,
    body: JSON.stringify(ideaJSON),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseJson) => {
    if (responseJson.success) {
      // window.history.back();
      window.open(`/ideas/${responseJson.idea_id}/comments`, '_self');
    }
  });
}


const formIdeaDetails = document.querySelector('#idea-details');

formIdeaDetails.addEventListener('submit', (evt) => {
  evt.preventDefault();
  if (formIdeaDetails.classList.contains('invalid')){
    formIdeaDetails.classList.remove('invalid');
    return;
  }
  const method = document.querySelector('#method').value;
  const title = document.querySelector('#title').value;
  const description = document.querySelector('#description').value;
  const link = document.querySelector('#link').value;

  let url = "/ideas";
  if (method === 'PUT') {
    const idea_id = document.querySelector('#idea_id').value;
    url += `/${idea_id}`;
  }
  
  handleIdea(url, method, title, description, link);
});