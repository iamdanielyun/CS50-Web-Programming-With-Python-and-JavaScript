document.addEventListener('DOMContentLoaded', function() {

  // By default, load the inbox
  upload_mailbox('inbox');

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  
  //Sending mail
  document.querySelector('#compose-form').onsubmit = send_mail;

  //Uploading maibox
  document.getElementsByName('mailbox').forEach(button => {
    button.onclick = () => {
      var mailbox = String(button.value);
      upload_mailbox(mailbox);
    }
  });
})

//////////////////////////////////////////////////////////////////////

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

///////////////////////////////////////////////////////////////////////

function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
}

///////////////////////////////////////////////////////////////////////

//View individual email
function view_email(id, mailbox) {
  const email_id = parseInt(id);

  //Make API call 
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(data => {

    //clear out all views
    document.querySelector('#compose-view').style.display = 'none';
    document.querySelector('#emails-view').style.display = 'none';
    document.querySelector('#email').style.display = 'block';
    document.querySelector('#email').innerHTML = '';

    //Info
    const sender = data.sender;
    const recipients = data.recipients;
    const subject = data.subject; 
    const timestamp = data.timestamp;
    const body = data.body;

    let archive_button;
    if(mailbox == 'inbox') 
      archive_button = `<button onclick=change_archive(this) id="archive" value=${email_id} class="btn btn-sm btn-outline-primary">Archive</button>`;
    else if(mailbox == 'archive') 
      archive_button = `<button onclick=change_archive(this) id="unarchive" value=${email_id} class="btn btn-sm btn-outline-primary">Unarchive</button>`;
    else
      archive_button = '';
      
    //Display info 
    const email = document.createElement('div');
    email.innerHTML = `
    <b>From: </b> ${sender} <br>
    <b>To: </b> ${recipients} <br>
    <b>Subject: </b> ${subject} <br>
    <b>Timestamp: </b> ${timestamp} <br>
    <button id="reply" value=${email_id} onclick=reply(this) class="btn btn-sm btn-outline-primary">Reply</button>
    ${archive_button}
    <hr>
    ${body}
    `;
    document.querySelector('#email').append(email); 

    //Mark email as read
    fetch(`/emails/${email_id}`, {
      method: 'PUT',
      body: JSON.stringify({
        read: true
      })
    })
  }); 
}

/////////////////////////////////////////////////////////////////////////

//Reply
function reply(button) {

  //Email info
  const email_id = parseInt(button.value);

  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(data => {

    //Load composition form
    compose_email();

    //Pre-fill out form
    const sender = data.sender;
    const subject = data.subject;
    const body = data.body;
    const timestamp = data.timestamp;

    document.querySelector('#compose-recipients').value = sender;
    document.querySelector('#compose-body').value = `On ${timestamp} ${sender} wrote: ${body}`;
    document.querySelector('#compose-subject').value = `Re: ${subject}`;
  })

   
}

////////////////////////////////////////////////////////////////////////

//Archive/Unarchive
function change_archive(button) {

  //This email id
  const email_id = parseInt(button.value);
  let action = String(button.id);
  let archived;

  //Archive
  if(action == 'archive')
    archived = true;
  //Unarchive
  if(action == 'unarchive')
    archived = false;

  //API call
  fetch(`/emails/${email_id}`, {
    method: 'PUT',
    body: JSON.stringify({
      archived: archived
    })
  })
  .then(() => upload_mailbox('inbox'));
}

/////////////////////////////////////////////////////////////////////////

//Upload mailbox
function upload_mailbox(mailbox) {
  
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(data => {
    load_mailbox(mailbox);
     
    //Inbox or archived
    if(mailbox=='inbox' || mailbox =='archive') {
      for(var i=0; i<data.length; i++)
      {
        const info = data[i];
        const email_id = info.id;
        const sender = info.sender;
        const subject = info.subject; 
        const timestamp = info.timestamp;
        const read = info.read;
        let background_color;

        if(read === false) background_color = "white";
        else background_color = "#C8C8C8"; 

        const email = document.createElement('div');
        email.innerHTML = `
        <div style="border-style: solid; background-color: ${background_color}">
          <div style="float: left;"> 
            <b>${sender}</b>
          </div>
          &nbsp;&nbsp;${subject}
          <div style="float: right;"> 
            ${timestamp}
          </div>
        </div>
        `;
        //when clicked view the email
        email.addEventListener('click', () => view_email(email_id, mailbox));
        document.querySelector('#emails-view').append(email);
      } 
    }

    //Sent mailbox
    else {
      for(var i=0; i<data.length; i++)
      {
        const info = data[i];
        const email_id = info.id;
        const recipients = info.recipients;
        const subject = info.subject; 
        const timestamp = info.timestamp;
        const is_inbox = false;
        const email = document.createElement('div');
        email.innerHTML = `
        <div style="border-style: solid; width: 800px; background-color: #C8C8C8">
          <div style="float: left;"> 
            <b>${recipients}</b>
          </div>
          &nbsp;&nbsp;
          ${subject}
          <div style="float: right;"> 
            ${timestamp}
          </div>
        </div>
        `;
        //when clicked view the email
        email.addEventListener('click', () => view_email(email_id, mailbox));
        document.querySelector('#emails-view').append(email);
      } 
    }
  });
}

//////////////////////////////////////////////////////////////////////

//Extract emails 
function extract_emails(text) {
  return text.match(/([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9._-]+)/gi);
}

////////////////////////////////////////////////////////////////////////

//Send mail
function send_mail() {

  //Necessary values
  const recipient_field = String(document.querySelector('#compose-recipients').value);
  const recipients = extract_emails(recipient_field).join(','); 
  // const recipients = String(document.querySelector('#compose-recipients').value);
  const subject = String(document.querySelector('#compose-subject').value);
  const body = String(document.querySelector('#compose-body').value);

  //API call to send email
  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
      recipients: recipients,
      subject: subject, 
      body: body
    })
  });
}

