document.querySelector(".statusSubmit").addEventListener('click', () => {
    console.log("clicked!")
    $.post("/api/get_session_user", {}).done((response) => {
            console.log("USER IS OK")
            console.log(document.querySelector(".statusEdit").value, "newstatus ")
            $.post("/set-status", JSON.stringify({
                'id': response.user.id,
                'status': document.querySelector(".statusEdit").value
            })).done((response2) => {
                $(".statusEdit").value = response2.status
            }).fail(() => {
                console.log("FAILED at SET-STATUS")
            })
    })

})