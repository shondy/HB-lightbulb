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

function checkIsNotEmpty(value){
  // check if value doesn't contain whitespace characters only 
  const valid_value = /.*[^\s]+.*/;
  return valid_value.test(value);
}

const formIdeaDetails = document.querySelector('#idea-details');

formIdeaDetails.addEventListener('submit', (evt) => {
  evt.preventDefault();
  const method = document.querySelector('#method').value;
  const title = document.querySelector('#title').value;
  if (!checkIsNotEmpty(title)){
    return;
  }
  const description = document.querySelector('#description').value;
  if (!checkIsNotEmpty(description)){
    return;
  }
  const link = document.querySelector('#link').value;

  let url = "/ideas";
  if (method === 'PUT') {
    const idea_id = document.querySelector('#idea_id').value;
    url += `/${idea_id}`;
  }
  
  handleIdea(url, method, title, description, link);
});