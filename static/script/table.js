/*
    Sortable, searchable and traformable tables for PagerUI.
    
    Use class "sortable" on "th" headers to add 
    a sorting functionality.
    
    Use class "searchable" on "th" header to add 
    a searching field. Specify search type via
        data-search-type=regex 
        data-search-type=substr (default)
    in table attributes. Don't forget to add 
        data-field=[document field name]
    to "th"-element.
    
    Use class "transformable" on "th" header to add switchable
    transform functionality to a column. Add to all relevant
    <td> elements classes
        transform
        [field name]
    and attribute
        data-transform="[func]"
        
    Example:
    <table data-search-type="regex">
        <tr>
            <th data-field="address" 
                class="sortable searchable transformable">
                    Address
            </th>
        </tr>
        <tr>
            <td data-transform="streetToGoogleView" 
                class="transform address">
                    Russia, Moscow, Lenin street 1
            </td>
        </tr>
    </table>
*/


function html_arrow(direction) {
    // show user the direction of column sorting
    var arrow = direction == -1 ? "&darr;" : "&uarr;"
    return "&nbsp;" + arrow + "&nbsp;";
}


function search_input_keypress(e) {
    // on [enter]
    if (e.which == 13) {
        var search = {};
        var $input = $(this)
        var $table = $input.closest("table");
        
        // collect all search inputs
        $table.find("input.search").each(function() {
            var $other_input = $(this)
            var val = $other_input.val().trim()
            
            // test if not empty
            if (val) {
                
                // test for valid regex
                if ($table.data("search-type") == "regex") {
                    try {
                        var test = new RegExp(val);
                    } catch (e) {
                        alert(e)
                        return
                    }
                }
                
                // collect
                search[$other_input.data("field")] = val
            }
        })
        
        // go to first page of the modified search
        location.search = modify_search({
            "search": JSON.stringify(search),
            "page": 0
        })
    }
}

function search_input_focusin(e) {
    var $input = $(this)
    var $header = $input.closest("th")
    var search_type = $header.data("search-type")

    // change looks
    $input
        .css("width", "125px")
        .attr("placeholder", search_input_placeholder(search_type, true))
    
    // replace column elements with its original values
    if ($header.hasClass("transformable")) {
        $("td." + $header.data("field")).each(function() {
            var $td = $(this)
            $td.html($td.data("original"))
        })
    }
}

function search_input_placeholder(search_type, is_focused) {
    if (is_focused) {
        if (search_type == "regex") {
            return " поиск regex "
        } else {
            return " поиск строки "
        }
    } else {
        return " [...] "
    }
}

function search_input_focusout(e) {
    var $input = $(this)
    var $header = $input.closest("th")
    var search_type = $header.data("search-type")
    
    // change looks
    if($input.val()) {
        $input.css("width", "125px")
    } else {
        $input
            .css("width", "35px")
            .attr("placeholder", search_input_placeholder(search_type, false))
    }
    
    // transform column elements
    if ($header.hasClass("transformable")) {
        $("td." + $header.data("field")).each(function() {
            var $td = $(this)
            $td.html($td.data("changed"))
        })
    }
}

function gen_search_input($header, search_type) {
    // prepare search field for th.searchables
    var $input = $("<input>")
        .attr("type", "text")
        .attr("placeholder", search_input_placeholder(search_type, false))
        .data("search-type", search_type)
        .data("field", $header.data("field"))
        .addClass("search")
        .keypress(search_input_keypress)
        .focusin(search_input_focusin)
        .focusout(search_input_focusout)
    
    return $input
}


$(function() {

    // add sort link
    $("th.sortable").each(function() {
        var $header = $(this)
        
        // reverse direction
        var sort_direction = get_argument("direction", "-1") == "-1" ? 1 : -1; 
        
        // properties with "s__" prefix are made for search
        // use name without this prefix to sort
        var sort_field = $header.data("field").replace("s__", "")
        
        // generate sort link
        var $a = ahref_modify_search({
            "sort": sort_field, 
            "direction": sort_direction
        })
        
        $header.wrapInner($a)
        
        // additionally, if the location bar has sort parameter
        // and it matches current header name
        // then add an html arrow to it
        if (sort_field == get_argument("sort")) {
            $header.append(html_arrow(sort_direction))
        }
    })

    // add search input
    $("th.searchable").each(function() {
        var $header = $(this)
        var $table = $header.closest("table")
        
        // specify search type (regex or substr)
        var search_type = $table.data("search-type") || "substr";
        
        // extract previous search arguments
        try {
            var search_args = JSON.parse(get_argument("search", "{}"))
        } catch (e) {
            var search_args = {}
            console.log(e)
        }
        
        // generate input field
        var $input = gen_search_input($header, search_type);
        // and insert current search if it is relevant to the element
        if (search_args.hasOwnProperty($header.data("field"))) {
            var search_text = search_args[$header.data("field")]
            $input.val(search_text)
        }
        // refresh
        $input.focusout()
        
        // append it to the header
        $(this).append("&nbsp;")
        $(this).append($input)
    })
})