/*
    Make PagerUI work.
*/

$(function() {
    // go to page
    $(".pager .goto").click(function() {
        location.search = modify_search({
            "page": $(this).data("page")
        })
    })
    
    // change page number on [enter]
    $(".pager .input-page").keypress(function(event) {
        if(event.which == 13) {
            location.search = modify_search({
                "page": Math.abs(parseInt($(this).val()) || 0) - 1
            })
        }
    })
    
    // change number of elements per page on [enter]
    $(".pager .element-number input").keypress(function(event) {
        console.log($(this))
        if(event.which == 13) {
            location.search = modify_search({
                "show": Math.abs(parseInt($(this).val()) || 100)
            })
        }
    })
})