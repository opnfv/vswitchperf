function writeToHTML(element, obj){

  shrinkHTML(element)
  _writeToHTML(element, obj);
}


/* Remove all extra arr elements with delete button, i.e. make arr.length=1*/
function shrinkHTML(element){

  var delButtons = element.querySelectorAll('[data-del]');
  if(delButtons.length == 0)
    return;

  for(button of [...delButtons])
    button.click();
  
}


function _writeToHTML(element, obj){

  var el = [...element.childNodes];
  for(var i in el)
  {

      if(el[i] instanceof HTMLInputElement && el[i].hasAttribute('name')){

          if(el[i].type == 'text' || el[i].type == 'number'){

              if(el[i].classList.contains('arr')){

                  var name = el[i].getAttribute('name');
                  var values = readValue(obj, name);

                  if(values !== undefined && (Array.isArray(values) && values.length)){

                      var buttons = element.parentNode.querySelectorAll(`[data-add="${name}"]`);
                      var addButton = buttons[buttons.length -1];
                      for(var j=0; j< values.length-1; j++)
                        addButton.click();
                   
                      // Update value inside all input boxes
                      for(var box of element.parentNode.getElementsByClassName('arr'))
                        if(box.getAttribute("name") === name)
                          box.value =  values.pop();
                  }

              }
              else{
                  var value = readValue(obj, el[i].name);
                  if(value !== undefined)
                    el[i].value = value;
              }
          }

          if(el[i].type == 'radio'){
            var value = readValue(obj, el[i].name);
            if(el[i].value === value){
              el[i].checked = true;
            }
          }

      }
      if(el[i] instanceof HTMLSelectElement && el[i].hasAttribute('name')){

          if(el[i].classList.contains('arr')){

              var name = el[i].getAttribute('name');
              var values = readValue(obj, name);

              if(values !== undefined && (Array.isArray(values) && values.length)){

                  var buttons = element.parentNode.querySelectorAll(`[data-add="${name}"]`);
                  var addButton = buttons[buttons.length -1];
                  for(var j=0; j< values.length-1; j++)
                    addButton.click();
                   
                  // Update value inside all input boxes
                  for(var box of element.parentNode.getElementsByClassName('arr'))
                        if(box.getAttribute("name") === name){
                          var defaultValue = box.value;
                          var option = values.pop();
                          box.value = option;
                          if(box.value !=option)
                            box.value = defaultValue;
                        }
              }

          }
          else{

                var option = readValue(obj, el[i].name);
                var defaultValue = el[i].value;
                el[i].value = option;
                if ( el[i].value != option)
                    el[i].value = defaultValue;
          }

      }
      if(el[i] instanceof HTMLDivElement){

          if(el[i].hasAttribute('name') && el[i].classList.contains('arr'))
          {              
            
              var name = el[i].getAttribute('name');
              var values = readValue(obj, name);

              if(values !== undefined && (Array.isArray(values) && values.length)){

                  var buttons = element.querySelectorAll(`[data-add="${name}"]`);
                  var addButton = buttons[buttons.length -1];
                  for(var j=0; j< values.length-1; j++)
                    addButton.click();
                   
                  // Update value inside all divs
                  for(var div of element.getElementsByClassName('arr'))
                    if(div.getAttribute("name") === name)
                      _writeToHTML(div , values.pop());
              }

          } //else-if single div
          else if(el[i].hasAttribute('name')){
              var value = readValue(obj, el[i].getAttribute('name'));
              if(value !== undefined)
                _writeToHTML(el[i], value);

          }//else-if blank div without attribute name, then simply pass values to next child
          else
              _writeToHTML(el[i], obj);
      }
      if(el[i] instanceof HTMLLabelElement || el[i] instanceof HTMLSpanElement)
          _writeToHTML(el[i], obj);

  }
}


  // Reads value from obj with string 'key1.key2.key3' convention
  function readValue(obj, str) {
    str = str.replace(/\[(\w+)\]/g, '.$1'); // convert indexes to properties
    str = str.replace(/^\./, '');           // strip a leading dot
    var a = str.split('.');
    for (var i = 0; i < a.length; ++i) {
        var key = a[i];
        if (key in obj) {
            obj = obj[key];
        } else {
            // alert('Key '+key+ ' not Found');
            return undefined;
        }
    }
    return obj;
  }
