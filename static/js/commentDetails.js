const formCommentDetails = document.querySelector('#comment-details');

formCommentDetails.addEventListener('submit', (evt) => {
  evt.preventDefault();
  const method = document.querySelector('#method').value;
  const idea_id = document.querySelector('#idea_id').value;
  const description = document.querySelector('#description').value;

  let comment_id;
  if (method === 'PUT') {
    comment_id = document.querySelector('#comment_id').value;
  }
  // opener property returns a reference to the window that opened the window,
  // this window has script with addComments.js
  window.opener.handleComment(method, idea_id, description, comment_id);
  window.close();
});