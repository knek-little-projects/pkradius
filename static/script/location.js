/*
    Work with `location` bar.

    
    Use `get_argument(name, default)` to get value from
        http://location?name=value
    

    Use `modify_search({name: value})` to get modified
    search path. E. g. if current location is 
        "http://...?a=b&c=d"
    then 
        `modify_search({c: 1, d: 2})`
    will return string 
        "?a=b&c=1&d=2"
        
    
    Use `ahref_modify_search({name: value})` to generate 
        $("<a href='...'")
    via `modify_search` function
*/


function re_argument(argument) {
    // generate RegExp to select location.search argument values
    return new RegExp("\\b" + argument + "=([^\\&]+)");
}

function urldecode(url) {
    return decodeURIComponent(url.replace(/\+/g, "%20"))
}

function get_argument(name, def) {
    // get location.search url decoded argument value
    var result = re_argument(name).exec(location.search);
    if (result) {
        return urldecode(result[1])
    } else {
        return def
    }
}

function get_search_dict() {
    // transform location.search to dictionary
    var search = location.search.slice(1).split('&')
    var dict = {}
    for(var i=0; i<search.length; i++){
        var key_val = search[i].split('=');
        if(key_val.length == 2) {
            var key = urldecode(key_val[0])
            var val = urldecode(key_val[1])
            dict[key] = val
        }
    }
    return dict
}

function dict_to_search(dict) {
    // transform dict to search string
    var search = ""
    for(var key in dict) {
        search += "&" + encodeURIComponent(key) + "=" + encodeURIComponent(dict[key])
    }
    return "?" + search.slice(1)
}

function modify_search(dict) {
    // modify location.search string via dictionary
    // use current location.search as base string
    var search = get_search_dict()
    for(var key in dict) {
        search[key] = dict[key]
    }
    return dict_to_search(search)
}

function ahref_modify_search(dict) {
    return $("<a>").attr("href", modify_search(dict))
}