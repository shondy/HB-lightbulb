const showWindowForIdea = url => {
  window.open(`${url}`,'targetWindow', 
      `toolbar=no,
      location=no,
      status=no,
      menubar=no,
      scrollbars=yes,
      resizable=yes,
      width=700,
      height=700`);
};

if (document.querySelector('.add-idea')) {
  const addIdeaButton = document.querySelector('.add-idea');

  addIdeaButton.addEventListener('click', (evt) => {
  // check first if user loged in and open a window with comment form
    if (evt.target.classList.contains('available')) {
      const url = `/ideas`;
      showWindowForIdea(url);
    }
    else {
      alert("Please Sign in/Join to be able to add ideas")
    }
  });
}

if (document.querySelector('.edit-idea')) {
  const editIdeaButton = document.querySelector('.edit-idea');

  editIdeaButton.addEventListener('click', (evt) => {
  // check first if user loged in and open a window with comment form

    const idea_id = evt.target.parentElement.id;
    const url = `/ideas/${idea_id}`;
    showWindowForIdea(url);
  });
}

function handleIdea(method, title, description, link, idea_id) {
  // create comment - method POST, update comment - method PUT

  let url = `/ideas`; 
  url = (idea_id === undefined ? url : url + `/${idea_id}`);

  const ideaJSON = {
    title: title,
    description: description,
    link: link,
  };

  
  fetch(`${url}`, {
    method: method,
    body: JSON.stringify(ideaJSON),
    headers: {
      'Content-Type': 'application/json',
    },
  })
  .then((response) => response.json())
  .then((responseJson) => {
    if (responseJson.success) {
        window.location.reload();
    }
  });
}
