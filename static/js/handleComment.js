const showWindowForComment = url => {
        window.open(`${url}`,'targetWindow', 
            `toolbar=no,
            location=no,
            status=no,
            menubar=no,
            scrollbars=yes,
            resizable=yes,
            width=800,
            height=500`);
};

const addCommentButton = document.querySelector('.add-comment');

addCommentButton.addEventListener('click', (evt) => {
// check first if user loged in and open a window with comment form
  if (evt.target.parentElement.classList.contains('active')) {
    const idea_id = location.pathname.split('/')[2];
    const url = `/comments/${idea_id}`;
    showWindowForComment(url);
  }
  else {
    alert("Please Sign in/Join to be able to add comments")
  }
});


const editCommentButtons = document.querySelectorAll('.edit-comment');

for (button of editCommentButtons){
  button.addEventListener('click', (evt) => {
    // open comment form 
    const idea_id = location.pathname.split('/')[2];
    const comment_id = evt.target.parentElement.id;
    const url = `/comments/${idea_id}/${comment_id}`;
    showWindowForComment(url);
  });
}

const deleteCommentButtons = document.querySelectorAll('.delete-comment');

for (button of deleteCommentButtons){
  button.addEventListener('click', (evt) => {
    const idea_id = location.pathname.split('/')[2];
    const comment_id = evt.target.parentElement.id;
    const url = `/comments/${idea_id}/${comment_id}`;
    fetch(`${url}`, {
      method: 'DELETE',
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
  });
}

function handleComment(method, idea_id, description, comment_id) {
  // create comment - method POST, update comment - method PUT

  let url = `/comments/${idea_id}`; 
  url = (comment_id === undefined ? url : url + `/${comment_id}`);

  const commentJSON = {
      description: description,
    };

  console.log("url = ", url, "commentJSON = ", commentJSON);
  fetch(`${url}`, {
    method: method,
    body: JSON.stringify(commentJSON),
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
