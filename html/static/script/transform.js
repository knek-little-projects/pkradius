/*
    Transform innerHTML of entities with class "transform".
    Use "data-transform" attribute as a function.

    Example:
    <div ...
        class="transform" 
        data-transform="crop_date">
        12.12.12 12:12:12.2134
    </div>

    Will result in:
    <div ... 
        data-original="12.12.12 12:12:12" 
        data-changed="12.12.12 12:12">
        12.12.12 12:12
    </div>
*/

function cropDate(s) {
    return s.replace(/\:[0-9]+\.[0-9]+$/, "")
}

function transformAccessLevelName(s) {
    switch(s.trim()) {
        case "0": 
            return "Анонимус";
        case "1": 
            return "Пользователь";
        case "2": 
            return "Модератор";
        case "3": 
            return "Администратор";
    }
}

$(function() {
    $(".transform").each(function() {
        // transform html objects
        // store original html in .data-original
        // store result html in .data-changed
        var original = $(this).html().trim();
        var transform = window[$(this).data("transform")]
        var changed = transform(original)
        $(this).data("original", original)
        $(this).data("changed", changed)
        $(this).html(changed)
    })
})