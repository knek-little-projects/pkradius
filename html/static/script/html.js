/*
    Use "content-table" class to create ToC for its parent entity.

    Example:
    <div>
        <div class="content-table">
            This is ToC.
        </div>
        ...
        This is text with headers for ToC.
        ...
        <h1>...</h1>
        ...
        <h2>...</h2>
        ...
    </div>
    
    
    Use "click" class and "data-click=f" to add click-trigger with function f.
    
    Example:
    <a class="click" data-click="alert">dosmth</a>
    
    Will result in:
    alert($([this object]))
    
    
    Use "allow-tab" for textarea.
*/


function make_content_table($toc, $scope) {
    // $toc - container for ToC
    // $scope - container with headers (h1, h2, h3...)
    $scope.find("h1, h2, h3").each(function(i) {
        var current = $(this);
        var id = current.attr("id")
        if (!id) {
            id = "title-" + i
            current.attr("id", id)
        }
        $toc.append("<a class='header-link header-link-" + current.prop("tagName").toLowerCase() + "' href='#" + id + "' title='" + current.text() + "'>" + current.text() + "</a>");
    })
    $toc.prepend("<h2 class='content-table-header'>ОГЛАВЛЕНИЕ</h2>")
}


$(function() {

    // click on image -> open in new tab
    $("img.window").click(function() {
        window.open($(this).attr("src"), '_blank');
    })
    
    // make content tables
    $(".content-table").each(function() {
        make_content_table($(this), $(this).parent())
    })

    // clear cellspacing for tables
    $("table").attr("cellspacing", 0)
    
    // set logout href
    $("#logout-href").click(function() {
        $("#logout-form").submit()
    })
    
    $(".click").click(function(){
        var fname = $(this).data("click")
        window[fname]($(this))
    })
    
    $("textarea.allow-tab").keydown(function(e) { 
        switch(e.keyCode || e.which) {
            case 9: 
                // tab was pressed
                // get caret position/selection
                var start = this.selectionStart;
                var end = this.selectionEnd;
                var space = "    ";
                var $this = $(this);

                // set textarea value to: text before caret + tab + text after caret
                $this.val($this.val().substring(0, start)
                            + space
                            + $this.val().substring(end));

                // put caret at right position again
                this.selectionStart = this.selectionEnd = start + space.length;

                // prevent the focus 
                e.preventDefault(); 
                break;
        } 
    })
})