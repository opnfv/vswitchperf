
// Add button
function duplicate(button){
    if(button.hasAttribute("data-add"))
      var name = button.getAttribute("data-add");

    newdiv = button.previousElementSibling.cloneNode(true);
    if(newdiv instanceof HTMLDivElement || newdiv instanceof HTMLLabelElement || newdiv instanceof HTMLSpanElement)
        if (!newdiv.lastElementChild.classList.contains('del-button')){
          del =`<div data-del="${name}" class="del-button" onclick="remove(this)"></div>`
          newdiv.innerHTML += del;
        }
    button.parentNode.insertBefore(newdiv, button)
  
}

// Delete Button
function remove(button){
  button.parentNode.parentNode.removeChild(button.parentNode);
}

