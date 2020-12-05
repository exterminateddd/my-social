

document.writeln("<script src=\"https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js\"></script>")
function showError(selector, failedObject, error) {
    document.querySelector(selector).innerHTML += `
            <div class="error-message">
            <span class="error-text">could not load data: ${error} <br> object: ${failedObject}</span>
            </div>
        `
        setTimeout(() => {
            $(selector).fadeOut()
        },4000)
}
document.addEventListener('DOMContentLoaded', () => {
    let postWall = ``;
    $.post("/api/get_posts", {}).done(function(responsePosts) {
        // let user;
        // // let user = fetch("/get_session_user", {method: 'POST'}).user
        // (async function() {
        // let data = await fetch('/get_session_user', {method: 'POST'});
        // user = await data.json();
        // console.log("user inside func" ,  user)
        // })()
        // setInterval(() => console.log(user), 1000)
        // console.log("user outside func" , user)
        // user is undefined
        let user;
        $.post("/api/get_session_user", {}).done( (response) => {
            user = response.user
            responsePosts.posts.forEach(element => {
                $.post("/api/get_user_by_id", JSON.stringify({
                    'id': element.author
                })).done((resp2) => {
                    console.log(resp2)
                    let deletablePost = `
                    <a href="/delete-post/${element.id}">
                        <img src="/static/images/delete.svg" class="deletePost" alt="Delete post">
                    </a>
                `
                let adminDeletablePost = `
                <a href="/delete-post/${element.id}">
                    <img src="/static/images/delete-admin.svg" class="deletePost" alt="Delete post">
                </a>
                `
                let newPost = `
                    <h1>#${element.id}<br>${element.name}</h1>
                    <p class="content">
                        ${element.content}
                    </p>
                    <br>
                    <div class="postFooter">
                        <span>by <a href="/profile/${element.author}" class="profileLink">@${resp2.user.username}</a></span>
                        <a href="/view-post/${element.id}">
                            <img src="/static/images/more.svg" alt="More" class="seeMore">
                        </a>
                    </div>
                `;
                if (user.id === element.author) {
                    newPost = deletablePost+newPost
                } else if (user.roles.includes("admin")) {
                    newPost = adminDeletablePost+newPost
                }
                    document.querySelector(".postWall").innerHTML += `<div class="post">` + newPost + `</div>`;
                })

        })
        }).fail((xhr, status, error) => {
            showError("#alert", "user", error)
        })
    }).fail((xhr, status, error) => {
        showError("#alert", "postWall", error)
    })
})

document.querySelector(".newPostSend").addEventListener('click', (e) => {
    const content = document.querySelector('.newPostContent').value
    const title = document.querySelector('.newPostTitle').value
    console.log(title, content)
    $.post("/api/add-post", {
        'title': title,
        'content': content,
    }).done((resp) => {
            if (resp.success) {
                $.ajax({
                    'url': '/api/get_user_by_id',
                    'contentType': 'application/json',
                    method: 'POST',
                    data: JSON.stringify({
                        'id': resp.author,
                        'testfield': 'Hello'
                    }),
                    fail: () => {
                        showError('#alert', 'post author')
                    },
                    success: (resp2) => {
                        const element = resp.new_post
                let deletablePost = `
                            <a href="/delete-post/${element.id}">
                                <img src="/static/images/delete.svg" class="deletePost" alt="Delete post">
                            </a>
                        `
                let adminDeletablePost = `
                <a href="/delete-post/${element.id}">
                    <img src="/static/images/delete-admin.svg" class="deletePost" alt="Delete post">
                </a>
                `
                let newPost = `
                    <div class="post">
                        <h1>#${element.id}<br>${element.name}</h1>
                        <p class="content">
                            ${element.content}
                        </p>
                        <br>
                        <div class="postFooter">
                            <span>by <a href="/profile/${resp2.user.name}" class="profileLink">@${element.id}</a></span>
                            <a href="/view-post/${element.id}">
                                <img src="/static/images/more.svg" alt="More" class="seeMore">
                            </a>
                        </div>
                    </div>
                `
                document.querySelector(".postWall").innerHTML += newPost
                    }
                })
            } else {
                showError('#alert', 'post addition', resp.message)
            }
        }
    ).fail(() => {
        showError('#alert', 'session user')
    })
})
