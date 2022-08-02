document.addEventListener('DOMContentLoaded', function() {

    //By default all posts
    posts("all");
    
    //Current user
    const current_user = document.querySelector('#user').value;

    document.querySelector('#compose').addEventListener('click', () => upload_view('compose-view'));
    document.querySelector('#posts').addEventListener('click', () => posts('all'));
    document.querySelector('#following').addEventListener('click', () => posts('following'));
    document.querySelector('#profile').addEventListener('click', () => profile(current_user));
 
    //Creating Post
    document.querySelector('#compose-form').onsubmit = compose;
})


//Upload view
function upload_view(view) {
    
    //Show view and hide other views
    document.getElementsByName('view').forEach(div => {
        div.style.display = 'none';
    });

    //Clear out compose field
    document.querySelector('#compose-body').value = ''; 

    document.querySelector(`#${view}`).style.display = 'block'; 
}


//Create new post
function compose() {

    //Necessary values
    const content = String(document.querySelector('#compose-body').value);

    //API call
    fetch('/network/create', {
        method: 'POST',
        body: JSON.stringify({
            content: content
        })
    });

    //Redirect to main page
    upload_view('posts-view');
}


//Show all posts
function posts(type) {

    //if all posts
    if(type == "all")
        upload_view('posts-view');
    else if(type == "following")
        upload_view('following-view');

    //API Call
    fetch(`/network/posts/${type}`)
    .then(response => response.json())
    .then(table => {
        
        //Current User
        const current_user = table.current_user;
        //Posts
        const data = table.posts;

        //Display posts
        display_posts(current_user, data, "posts");
    }); 
}


//Show profile
function profile(username) {
    upload_view('profile-view');

    //API Call
    fetch(`/network/profile/${username}`)
    .then(response => response.json())
    .then(data => {
        
        //Current User
        let current_user = data.current_user;
        //Follower Count
        let followers_count = data.followers_count;
        //Following Count
        let following_count = data.following_count;
        //Posts
        let posts = data.posts;

        const following_info = document.createElement('div');
        following_info.innerHTML = `
        <div>
            <h1><b>Followers:</b> ${followers_count}</h1>
        </div>
        <div>
            <h1><b>Following:</b> ${following_count}</h1>
        </div>
        `;
        document.querySelector('#profile-view').append(following_info);

        //Display posts
        display_posts(current_user, posts, "profile");
    });
} 


//Like or unLike post
function change_like() {

}


//Show all likes
function show_likes() {

}


//Follow
function follow() {

}


//Unfollow
function unfollow() {
    
}


//Displaying posts
function display_posts(current_user, data, view) {
    for(var i=0; i<data.length; i++)
        {                                   
            const info = data[i];
            const username = info.creator;
            const content = info.content;
            const date = info.date;
            const likes = info.likes;

            let background_color = "green";
            let like_or_unlike = "Like";

            for(var j=0; j<likes.length; j++) 
            {
                //If user liked post already
                if(current_user == likes[j]) {
                    background_color = "red";
                    like_or_unlike = "Unlike";
                    break;
                }
            }

            //Create element
            const post = document.createElement('div');
            post.innerHTML = `
            <div>
                <div>
                    <h5>Posted by <b>${username}</b> on <b>${date}</b></h5>
                </div>
                <div>
                    <button style="
                    background-color:${background_color}; 
                    color: black;
                    border: 2px solid #4CAF50;">
                    ${like_or_unlike}
                    </button>
                    <button class="btn btn-primary">All Likes</button>
                </div>
                <div>
                    ${content}
                </div>    
            </div>
            <hr>
            `;
            post.addEventListener('click', () => profile(username));
            document.querySelector(`#${view}-view`).append(post);
        }
}
