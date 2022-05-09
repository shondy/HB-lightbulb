const voteLinks = document.querySelectorAll('.vote');

for (const voteLink of voteLinks){
  voteLink.addEventListener('click', (evt) => { 
    // go through all inputs and check if its filled out
    evt.preventDefault();
    vote = evt.target;

    const voteJSON = {
      idea_id: vote.parentElement.classList[1],
    };
    
    console.log(voteJSON);

    if (vote.style.color === "lightgray") {
      fetch('/votes', {
        method: 'POST',
        body: JSON.stringify(voteJSON),
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then((response) => response.json())
      .then((responseJson) => {
        if (responseJson.success) {
          vote.style.color = "green";
          const voteTotal = document.getElementsByClassName(`total-votes ${voteJSON.idea_id}`)[0];
          voteTotal.innerText = 1 + parseInt(voteTotal.innerText);
        }
      });
    }
    else {
      fetch('/votes', {
        method: 'DELETE',
        body: JSON.stringify(voteJSON),
        headers: {
          'Content-Type': 'application/json',
        },
      })
      .then((response) => response.json())
      .then((responseJson) => {
        if (responseJson.success) {
          vote.style.color = "lightgray";
          const voteTotal = document.getElementsByClassName(`total-votes ${voteJSON.idea_id}`)[0];
          voteTotal.innerText = parseInt(voteTotal.innerText) - 1;
        }
      });
    }
  });
  
}