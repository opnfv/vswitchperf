// Settings Handler Utility


function setValue(name, value, options = {'secure': true, 'max-age': 60*60*24}) {

  options = {
    path: '/',
    // add other defaults here if necessary
    ...options
  };

  if (options.expires instanceof Date) {
    options.expires = options.expires.toUTCString();
  }

  let updatedCookie = encodeURIComponent(name) + "=" + encodeURIComponent(value);

  for (let optionKey in options) {
    updatedCookie += "; " + optionKey;
    let optionValue = options[optionKey];
    if (optionValue !== true) {
      updatedCookie += "=" + optionValue;
    }
  }

  document.cookie = updatedCookie;
}

function deleteValue(key) {
  setValue(key, "", {'secure': true, 'max-age': -1})
}


// returns the cookie with the given key,
// or undefined if not found
function getValue(key){
  let matches = document.cookie.match(new RegExp(
    "(?:^|; )" + key.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
  ));
  return matches ? decodeURIComponent(matches[1]) : undefined;
}


function getAllValues() {
        var theCookies = document.cookie.split(';');
        var config = new Object();
        for (var i = 1 ; i <= theCookies.length; i++) {
          var [key, value] = theCookies[i-1].split('=');
          if(key === "")
            continue;
          config[decodeURIComponent(key.trim())] = decodeURIComponent(value.trim());
        }
        return config;
      }

function deleteAllValues(){
  for(key in getAllValues())
    deleteValue(key);
}



