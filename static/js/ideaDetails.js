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
  const image = document.querySelector('#image').value;


  let idea_id;
  if (method === 'PUT') {
    idea_id = document.querySelector('#idea_id').value;
  }
  
  window.opener.handleIdea(method, title, description, link, image, idea_id);
  window.close();
});