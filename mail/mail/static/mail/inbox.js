let active_mailbox = "";

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // If email sent
  document.querySelector('#compose-form').onsubmit = send_email; 
  
  // If email clicked
  document.addEventListener('click', event => {

    // find what element was clicked
    const element = event.target;

    // if it was an email, load it & mark as already read
    if (element.className === 'email') {      
      load_email(element.dataset.id);
      mark_as_read(element.dataset.id);
    }
    
  })

  // By default, load the inbox
  load_mailbox('inbox');      
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';  
  
}

function load_mailbox(mailbox) {
  //flag active mailbox
  if (mailbox === 'inbox') {
    active_mailbox = 'inbox';
  }
  else if (mailbox === 'sent') {
    active_mailbox = 'sent';
  }
  else if (mailbox === 'archive') {
    active_mailbox = 'archive';
  }


  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  //Load emails in the mailbox
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
      console.log(emails); 
      emails.forEach(add_email);      
    });    
}

// adds email with content to DOM
function add_email(content) {
  
  // Create new mail
  const email = document.createElement('div');
  email.className = 'email';
  email.innerHTML = `<b>${content["sender"]}</b><span> ${content["subject"]}</span><span style="color: grey; float: right;"> ${content["timestamp"]}</span>`;
  email.style.border = "1px solid black";
  email.style.padding = "4px";
  email.dataset.id = `${content["id"]}`;

  if (content["read"]) {
    email.style.backgroundColor = "#EEEEEE";
  }

  // Add email to DOM
  document.querySelector('#emails-view').append(email);   
}


function send_email() {
  // extract submitted values
  const compose_recipients = document.querySelector('#compose-recipients').value;
  const compose_subject = document.querySelector('#compose-subject').value;
  const compose_body = document.querySelector('#compose-body').value;

  // query API
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: compose_recipients,
        subject: compose_subject,
        body: compose_body
    })
  })
  .then(response => response.json())
  .then(result => {
      // Prompt about result 
      if (result["error"]) {
        alert(result["error"]);            
      }
      else {
        load_mailbox('sent');
        alert(result["message"]);   
      }
  });
  
  return false;
}

// marks email as read
function mark_as_read(email_id) {
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
        read: true
    })
  });
}

// loads email view and buttons
function load_email(email_id) {
  // Show the email-view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'block';
  
  // Clear the existing email-view
  document.querySelector('#email-view').innerHTML = "";

  // query API
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(query => {       
    // Create element and fill in the email-view
    const email = document.createElement('div');
    email.innerHTML = `<div><b>From: </b>${query["sender"]}</div>
                        <div><b>To: </b>${query["recipients"]}</div>
                        <div><b>Subject: </b>${query["subject"]}</div>
                        <div><b>Timestamp: </b>${query["timestamp"]}</div>                        
                        <hr>
                        <span style="white-space: pre-wrap">${query["body"]}</span>`;
    
    document.querySelector('#email-view').append(email);     
  });
  
  // create and attach archive/unarchive buttons
  if (active_mailbox === 'inbox') {
    const button = document.createElement('button');
    button.innerHTML = 'Archive';
    button.className = 'btn btn-sm btn-outline-primary';
    button.addEventListener('click', () => {
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: true
        })
      })
      .then(response => {
        load_mailbox('inbox');
      })    
    });
    document.querySelector('#email-view').append(button);    
  }
  
  if (active_mailbox === 'archive') {
    const button = document.createElement('button');
    button.innerHTML = 'Unarchive';
    button.className = 'btn btn-sm btn-outline-primary';
    button.addEventListener('click', () => {
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            archived: false
        })
      })
      .then(response => {
        load_mailbox('inbox');
      })    
    });
    document.querySelector('#email-view').append(button);    
  }

  // create and attach Reply button
  const reply_button = document.createElement('button');
  reply_button.innerHTML = 'Reply';
  reply_button.className = 'btn btn-sm btn-outline-primary';
  reply_button.addEventListener('click', () => {
    // prepare empty compose form
    compose_email();

    // fetch data to pre-fill the form
    fetch(`/emails/${email_id}`)
    .then(response => response.json())
    .then(query => {
      
      document.querySelector('#compose-recipients').value = query["sender"];
      // if subject already starts with 'Re:' no need to attach to the reply
      if (query["subject"].charAt(0) === 'R' && query["subject"].charAt(1) === 'e' && query["subject"].charAt(2) === ':') {
        document.querySelector('#compose-subject').value = query["subject"];  
      }
      else {
        document.querySelector('#compose-subject').value = "Re: " + query["subject"];  
      }
      document.querySelector('#compose-body').value = "On " + query["timestamp"] + " " + query["sender"] + " wrote:\n" + query["body"];       
    });        
  });
  document.querySelector('#email-view').append(reply_button);
}  
  



