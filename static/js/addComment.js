const addCommentButton = document.querySelector('#add-comment');

addCommentButton.addEventListener('click', (evt) => {
// check first ask the user what they want the new rating to be
    if (evt.target.classList.contains('active')) {
        const idea_id = location.pathname.split('/')[2];
        window.open(`/comments/${idea_id}`,'targetWindow', 
            `toolbar=no,
            location=no,
            status=no,
            menubar=no,
            scrollbars=yes,
            resizable=yes,
            width=400,
            height=400`);
    }
    else {
        alert("Please Sign in/Join to be able to add comments")
    }
});


const editCommentButtons = document.querySelectorAll('.edit-comment');


for (button of editCommentButtons){
    button.addEventListener('click', (evt) => {
        const idea_id = location.pathname.split('/')[2];
        const comment_id = evt.target.id;
        console.log("comment_id", comment_id);
        window.open(`/comments/${idea_id}/${comment_id}`,'targetWindow', 
            `toolbar=no,
            location=no,
            status=no,
            menubar=no,
            scrollbars=yes,
            resizable=yes,
            width=400,
            height=400`);
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
        if (responseJson.status) {
            window.location.reload();
        }
      });
    }
