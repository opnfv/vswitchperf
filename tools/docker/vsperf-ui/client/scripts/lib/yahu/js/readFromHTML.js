
/**
* Reads HTML contents into javascript object
* 
*
* @param {element} element to read, can be input or div element
* @returns {object} New object with values read
*/
function readFromHTML(element){
  var obj = {};
  var el = element.childNodes;
  for(var i in el){

    if(el[i] instanceof HTMLInputElement && el[i].hasAttribute('name')) {


      if(el[i].type == 'text' || el[i].type == 'number'){

          if(el[i].classList.contains('arr')){
              var key = el[i].name;
              var value = objectify(el[i].name, el[i].value);
              if(obj[key] === undefined)
                obj[key] =[];
              obj[key].push(value[key]);

          }else
              obj = mergeDeep(obj, objectify(el[i].name, el[i].value));
      }
      if(el[i].type == 'radio'){
        if(el[i].checked)
          obj = mergeDeep(obj, objectify(el[i].name, el[i].value));
      }
    
    }
    if(el[i] instanceof HTMLSelectElement && el[i].hasAttribute('name')){
      
        if(el[i].classList.contains('arr')){
              var key = el[i].name;
              var value = objectify(el[i].name, el[i].value);
              if(obj[key] === undefined)
                obj[key] =[];
              obj[key].push(value[key]);

          }else
              obj = mergeDeep(obj, objectify(el[i].name, el[i].value));      
    }
    if(el[i] instanceof HTMLDivElement){

      if(el[i].classList.contains('arr')){
        var key = el[i].getAttribute('name');
        var value = readFromHTML(el[i]);
        if(obj[key] === undefined)
          obj[key] =[];
        obj[key].push(value[key]);
      }
      else
        obj = mergeDeep(obj, readFromHTML(el[i]));
      
    }
    if(el[i] instanceof HTMLLabelElement || el[i] instanceof HTMLSpanElement)
      obj = mergeDeep(obj, readFromHTML(el[i]));
  }
  
  if(element.hasAttribute('name')){
    var newobj = {};
    newobj[element.getAttribute('name')] = obj;
    return newobj;
  }
  return obj;
}



function objectify(key, value){
  var obj = {};
  var keys = key.split('.');
  for(var i = keys.length-1; i >= 0; i--){
    obj[keys[i]] = value;
    value = obj;
    obj = {};
  }
  return value;
}
