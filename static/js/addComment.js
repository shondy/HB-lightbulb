addCommentButton = document.querySelector('#add-comment');

addCommentButton.addEventListener('click', (evt) => {
// check first ask the user what they want the new rating to be
    if (evt.target.classList.contains('active')) {
        const idea_id = location.pathname.split('/')[2];
        window.open(`/comments?idea_id=${idea_id}`,'targetWindow', 
            `toolbar=no,
            location=no,
            status=no,
            menubar=no,
            scrollbars=yes,
            resizable=yes,
            width=SomeSize,
            height=SomeSize`);
    }
    else {
        alert("Please Sign in/Join to be able to add comments")
    }
});
